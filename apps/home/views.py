from django.views.generic import View, TemplateView
from django.shortcuts import render
import logging

logger = logging.getLogger()


class HomePageView(View):
    def get(self, *args, **kwargs):
        logger.info('home page')
        return render(self.request, 'home/anonymous_home.html')


class AboutUsView(TemplateView):
    template_name = 'home/about_us.html'


class ContactUsView(TemplateView):
    template_name = 'home/contact_us.html'
