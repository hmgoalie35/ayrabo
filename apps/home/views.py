import logging

from django.core.urlresolvers import reverse
from django.shortcuts import render, redirect
from django.views.generic import View, TemplateView

from userprofiles.models import UserProfile

logger = logging.getLogger()


class HomePageView(View):
    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated():
            if UserProfile.objects.filter(user=self.request.user).exists():
                template_name = 'home/authenticated_home.html'
            else:
                return redirect(reverse('create_userprofile'))
        else:
            template_name = 'home/anonymous_home.html'

        return render(self.request, template_name)


class AboutUsView(TemplateView):
    template_name = 'home/about_us.html'


class ContactUsView(TemplateView):
    template_name = 'home/contact_us.html'
