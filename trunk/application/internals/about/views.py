# Create your views here.
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from django.conf import *
from django.core.urlresolvers import reverse

from about.models import Contact
from about.forms import ContactForm

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            subject = form.cleaned_data['subject']
            content = form.cleaned_data['content']
            sender = form.cleaned_data['name']
            
            recipients = [admin[1] for admin in settings.ADMINS]
            
            print recipients
            from django.core.mail import send_mail
            send_mail(subject, content, sender, recipients)
            
            return HttpResponseRedirect(reverse('contact_thanks'))
    else:
        form = ContactForm()

    return render_to_response('contact.html', {
        'form': form,
    })
