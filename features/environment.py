import os

from behave import use_step_matcher
from django.conf import settings
from django.contrib.sites.models import Site
from selenium import webdriver

use_step_matcher('re')


def before_all(context):
    context.driver = webdriver.PhantomJS(
        executable_path=os.path.join(settings.NODE_MODULES_ROOT, 'phantomjs-prebuilt/bin/phantomjs'))
    context.driver.maximize_window()
    context.url_kwargs = {}
    # context.fixtures = ['dev_fixtures.json']


def after_all(context):
    context.driver.quit()


def before_scenario(context, scenario):
    site = Site.objects.get_current()
    site.name = '127.0.0.1'
    site.domain = context.get_url().split('http://')[1]
    site.save()
