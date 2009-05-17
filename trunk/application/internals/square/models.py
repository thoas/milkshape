import StringIO
import logging

from os import unlink, rename
from os.path import join, exists
from PIL import Image
from datetime import datetime

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django import forms
from django.utils.translation import ugettext_lazy as _

from issue.models import Issue
from square.constance import *

class AbstractSquareManager(models.Manager):
    def __init__(self):
        super(AbstractSquareManager, self).__init__()

    def neighbors(self, square):
        return self.filter(coord__in=list(str(key)\
            for key in square.neighbors().keys()))\
                .order_by('pos_x', 'pos_y')

class SquareManager(AbstractSquareManager):
    def bulk_create(square_list):
        for square in square_list:
            print square._meta.db_table

class SquareOpenManager(AbstractSquareManager):
    def neighbors_standby(self, square, is_standby=False):
        neighbors = square.neighbors().keys()
        neighbors.append(tuple((square.pos_x, square.pos_y)))
        
        logging.info('standbuy set to %d for %s' % (is_standby, neighbors))
        self.filter(coord__in=list(str(key)\
            for key in neighbors)).update(is_standby=is_standby)
        #from django.db import connection, transaction
        #cursor = connection.cursor()
        #cursor.execute("UPDATE square_squareopen SET is_standby = %d WHERE coord IN %s"
        #                    % (int(is_standby), str(tuple(str(neighbor) for neighbor in neighbors))))
        #transaction.commit_unless_managed()

class AbstractSquare(models.Model):
    pos_x = models.IntegerField(_('pos_x'))
    pos_y = models.IntegerField(_('pos_y'))
    coord = models.CharField(_('coord'), max_length=20, unique=True, blank=True)
    issue = models.ForeignKey(Issue, verbose_name=_('issue'))

    class Meta:
        abstract = True

    def save(self, force_insert=False, force_update=False):
        self.coord = str((self.pos_x, self.pos_y))
        logging.info('++ %s - %d' % (self.coord, force_insert))
        super(AbstractSquare, self).save(force_insert, force_update)

    def neighbors(self):
        if not hasattr(self, 'square_neighbors'):
            self.square_neighbors = dict((tuple((self.pos_x + POS_X[i], self.pos_y + POS_Y[i])), i)\
                for i in range(LEN_POS))
        return self.square_neighbors

def get_filename(instance, filename):
    """docstring for get_filename"""
    return instance.template_name

class Square(AbstractSquare):
    background_image = models.ImageField(upload_to=get_filename, blank=True, null=True)
    date_booked = models.DateField(_('date_booked'), blank=True, null=True)
    date_finished = models.DateField(_('date_finished'), blank=True, null=True)
    # 1 : full | 0 : booked
    status = models.BooleanField(_('status'), default=0)

    user = models.ForeignKey(User, verbose_name=_('user'),\
                        related_name=_('participations'), blank=True, null=True)
    square_parent = models.ForeignKey('Square', verbose_name=_('square_parent'),\
                        related_name=_('squares_child'), blank=True, null=True)
    template_name = models.CharField(_('template_name'),\
                        max_length=150, blank=True, null=True)

    objects = SquareManager()
    
    @staticmethod
    def retrieve_template(template_name):
        template_path = join(settings.TEMPLATE_ROOT, template_name)
        if not exists(template_path):
            return False
        template = Image.open(template_path)
        template.filename = template_name
        return template

    @staticmethod
    def buffer(template_image):
        buffer = StringIO.StringIO()
        template_image.save(buffer, format=FORMAT_IMAGE, quality=90)
        return buffer

    def generate_thumbs(self, image):
        thumbs = {}
        steps = self.get_steps()
        for step in steps:
            image.thumbnail((step, step))
            thumb_path = join(settings.UPLOAD_THUMB_ROOT, '%s_%s.png'\
                            % (str(step), self.background_image.name))
            logging.info(thumb_path)
            if exists(thumb_path):
                logging.warn('erase thumbnail %s' % thumb_path)
                unlink(thumb_path)
            thumbs[step] = image.save(thumb_path, format='PNG', quality=90)
        return thumbs
    
    def build_template(self):
        self.date_booked = datetime.now()
    
        self.template_name = self.get_formatted_background_image()

        image = Image.new(DEFAULT_IMAGE_MODE, (self.issue.size_with_double_margin,\
                    self.issue.size_with_double_margin), DEFAULT_IMAGE_BACKGROUND_COLOR)

        neighbors_keys = self.neighbors()
        logging.info(neighbors_keys)

        neighbors = Square.objects.neighbors(self)
        logging.info(neighbors)

        # square creation
        for neighbor in neighbors:
            coord_tuple = tuple((neighbor.pos_x, neighbor.pos_y))
            index = neighbors_keys[coord_tuple]
            im = Image.open(neighbor.get_background_image_path())

            logging.debug('%s -> %s (%s)' %\
                    (self.issue.crop_pos[index],\
                        self.issue.paste_pos[index], LITERAL[index]))

            crop = im.crop(self.issue.crop_pos[index])
            image.paste(crop, self.issue.paste_pos[index])

        # if square is already created
        if self.background_image:
            image_tmp_path = self.get_background_image_path()
            if exists(image_tmp_path):
                image_tmp = Image.open(image_tmp_path)
                logging.warn('background already exists, paste image %s' % image_tmp_path)
                image.paste(image_tmp, self.issue.creation_position_crop)
            
        image.save(self.get_template_path(), format=FORMAT_IMAGE, quality=90)
        image.filename = self.template_name
        return image
    
    def populate_neighbors(self, template_full):
        """docstring for thumbs"""
        
        # refresh neighbors background_image_name with overlap
        neighbors_keys = self.neighbors()
        neighbors = Square.objects.neighbors(self)
        
        logging.debug('neighbors : %s' % neighbors)
        for neighbor in neighbors:
            neighbor_current_key = tuple((neighbor.pos_x, neighbor.pos_y))
            index = neighbors_keys[neighbor_current_key]
            neighbor_path = neighbor.get_background_image_path()
            
            if not exists(neighbor_path):
                logging.error('%s doesn\'t exists')
                continue
            
            logging.info('rebuilding %s' % neighbor_path)
            image = Image.open(neighbor_path)
            image.paste(template_full.crop(self.issue.paste_pos[index]), self.issue.crop_pos[index])
            
            # PIL weakness : we can't resave an image in the same path, unlink before the old.
            unlink(neighbor_path)
            image.save(neighbor_path, format=image.format, quality=90)
            
            # delete all thumbs to recreate them
            neighbor.generate_thumbs(image)
            
            del neighbors_keys[neighbor_current_key]
            
            logging.info('- %d' % index)
        
        logging.info('populate %s' % neighbors_keys.keys())
        
        # create square side by side with overlap
        for x, y in neighbors_keys.keys():
            if (x >= 0 and x < self.issue.nb_case_y) and (y >= 0 and y < self.issue.nb_case_x):
                index = neighbors_keys[tuple((x, y))]
                
                # create square in database with no user set
                # thought INSERT ... INTO VALUES ((...), (...))
                new_square = Square.objects.create(
                    pos_x=x,
                    pos_y=y,
                    issue=self.issue
                )
                
                new_square_open = SquareOpen.objects.create(
                    pos_x=x,
                    pos_y=y,
                    issue=self.issue
                )
                
                image, thumbs = new_square.build_background_image(template_full.crop(self.issue.paste_pos[index]),\
                                    self.issue.crop_pos[index], settings.UPLOAD_HD_ROOT)
                
                logging.info('+ (%d, %d) -> %s' % (x, y, image.name))
        
        logging.info('+ %s' % image.name)

    def save(self, force_insert=False, force_update=False):
        if self.user:
            if not self.status:
                self.template = self.build_template()
        else:
            self.background_image = self.get_formatted_background_image()
        
        if self.pk and self.status:
            self.date_finished = datetime.now()
            self.background_image = self.get_formatted_background_image()
        super(Square, self).save(force_insert, force_update)
        
        # now, square saved, template uploaded, we can build thumbs and update neighbors
        if self.status and self.pk:
            template_full_path = self.get_template_full_path()
            
            # if the template uploaded already exists, we erase it
            if exists(template_full_path):
                logging.warn('%s already exists, erase...' % template_full_path)
                unlink(template_full_path)
                
            # rename the default location, from media directory to a dedicated one
            rename(join(settings.MEDIA_ROOT, self.template_name), template_full_path)
            
            template_full = Image.open(template_full_path)

            # create background_image_path with with template_full
            image, thumbs = self.build_background_image(template_full.crop(self.issue.creation_position_crop),\
                                self.issue.creation_position_paste, settings.UPLOAD_HD_ROOT)
            
            # update neighbors with overlap
            self.populate_neighbors(template_full)

    def build_background_image(self, im_crop, paste_pos, directory_root):
        image = Image.new(DEFAULT_IMAGE_MODE, self.get_size(), DEFAULT_IMAGE_BACKGROUND_COLOR)
        image.paste(im_crop, paste_pos)
        image.save(join(directory_root, self.get_formatted_background_image()),\
                        format=FORMAT_IMAGE, quality=90)
        image.name = self.get_formatted_background_image()

        logging.info(join(directory_root, self.get_formatted_background_image()))
        return image, self.generate_thumbs(image)

    def __unicode__(self):
        return self.coord

    def get_template(self):
        return Square.retrieve_template(self.template_name)\
                    if not hasattr(self, 'template') else self.template

    def get_template_path(self):
        return join(settings.TEMPLATE_ROOT, self.template_name)

    def get_template_full_path(self):
        return join(settings.UPLOAD_TEMPLATE_ROOT, self.template_name)
    
    def get_background_image_path(self):
        """docstring for get_background_image_path"""
        return join(settings.UPLOAD_HD_ROOT, self.background_image.name)
    
    def get_background_image_thumb_path(self, size):
        return join(settings.UPLOAD_THUMB_ROOT, '%s_%s' % (size, self.background_image.name))
    
    def get_upload_hd_url(self, size):
        """docstring for get_upload_hd_url"""
        return join(settings.MEDIA_URL, settings.UPLOAD_HD_DIR, '%s_%s'\
                % (str(size), self.background_image.name))

    def get_formatted_background_image(self):
        if not hasattr(self, 'formatted_background_image'):
            now = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')
            self.formatted_background_image = 'x%s_y%s__%s__%s.tif' %\
                                    (self.pos_x, self.pos_y, self.issue.slug, now)
            if self.user:
                self.formatted_background_image = '%s__%s'\
                    % (self.user.username, self.formatted_background_image)
        return self.formatted_background_image

    def get_size(self):
        if not hasattr(self, 'size'):
            self.size = tuple((self.issue.size, self.issue.size))
        return self.size

    def get_steps(self):
        if not hasattr(self, 'steps'):
            self.steps = self.issue.steps()
        return self.steps

    def delete(self):
        super(Square, self).delete()

class SquareOpen(AbstractSquare):
    date_created = models.DateField(_('date_created'), auto_now_add=True)

    # 0 : can be booked ; 1 : a square has been booked next to
    is_standby = models.BooleanField(_('is_standby'), default=settings.DEFAULT_IS_STANDBY)
    objects = SquareOpenManager()
        