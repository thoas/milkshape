from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^email/$', 'account.views.email', name='acct_email'),
    url(r'^signup/(?P<confirmation_key>[a-zA-Z0-9]{10,20})/$', 'account.views.signup', name='acct_signup_key'),
    url(r'^signup/$', 'account.views.signup', name='acct_signup'),
    url(r'^login/$', 'account.views.login', name='acct_login'),
    url(r'^password_change/$', 'account.views.password_change', name='acct_passwd'),
    url(r'^invitations/$', 'account.views.invitations', name='acct_invitations'),
    url(r'^invitations/(?P<confirmation_key>[a-zA-Z0-9]{10,20})/$', 'account.views.invitations', name='acct_invitations_key'),
    url(r'^password_reset/$', 'account.views.password_reset', name='acct_passwd_reset'),
    url(r'^timezone/$', 'account.views.timezone_change', name='acct_timezone_change'),
    url(r'^language/$', 'account.views.language_change', name='acct_language_change'),
    url(r'^logout/$', 'django.contrib.auth.views.logout', {'template_name': 'logout.html'}, name='acct_logout'),
    
    url(r'^confirm_email/(\w+)/$', 'emailconfirmation.views.confirm_email', name='acct_confirm_email'),
    
    #(r'^validate/$', 'ajax_validation.views.validate', {'form_class': SignupForm}, 'signup_form_validate'),
)
