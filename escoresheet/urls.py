"""escoresheet URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from home.views import HomePageView
from django.views.generic import RedirectView
from allauth.account.views import signup
from django.core.urlresolvers import reverse_lazy
from account_custom.views import EditAccountView, NewConfirmationEmailView

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$', HomePageView.as_view(), name='home'),
    url(r'^account/edit/$', EditAccountView.as_view(), name='account_edit'),
    url(r'^account/email/confirmation/new/$', NewConfirmationEmailView.as_view(), name='account_new_email_confirmation'),
    url(r'^account/register/$', signup, name='account_register'),
    url(r'^account/signup/$', RedirectView.as_view(url=reverse_lazy('account_register')), name='account_signup'),
    url(r'^account/', include('allauth.urls')),
]
