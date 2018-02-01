from allauth.account.views import signup
from django.conf.urls import url
from django.urls import reverse_lazy
from django.views import generic

from userprofiles.views import UserProfileUpdateView, UserProfileCreateView
from . import views

urlpatterns = [
    url(r'^$', UserProfileUpdateView.as_view(), name='account_home'),
    url(r'^complete-registration/$', UserProfileCreateView.as_view(), name='account_complete_registration'),
    url(r'^email-confirmation/new/$', views.NewConfirmationEmailView.as_view(), name='account_new_email_confirmation'),
    url(r'^email/$', generic.RedirectView.as_view(url=reverse_lazy('home')), name='account_email'),
    url(r'^inactive/$', generic.RedirectView.as_view(url=reverse_lazy('home')), name='account_inactive'),
    url(r'^register/$', signup, name='account_register'),
    url(r'^signup/$', generic.RedirectView.as_view(url=reverse_lazy('account_register')), name='account_signup'),
    url(r'^password/change/$', views.PasswordChangeView.as_view(), name='account_change_password'),
]
