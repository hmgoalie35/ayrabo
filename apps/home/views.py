from django.views.generic import View
from django.shortcuts import render
import logging

logger = logging.getLogger()


class HomePageView(View):
    def get(self, *args, **kwargs):
        logger.info('home page')
        return render(self.request, 'home/anonymous_home.html')
