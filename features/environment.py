import os

from behave import use_step_matcher
from django.conf import settings
from selenium import webdriver

use_step_matcher('re')

PHANTOMJS_BINARY = os.path.join(settings.NODE_MODULES_ROOT, 'phantomjs-prebuilt/bin/phantomjs')
CACHE_PATH = os.path.join(settings.BASE_DIR, '.phantomjs_cache')


def before_all(context):
    # See if these help performance.
    # service_args = ['--disk-cache=true', '--disk-cache-path={}'.format(CACHE_PATH)]
    context.driver = webdriver.PhantomJS(executable_path=PHANTOMJS_BINARY)
    context.driver.maximize_window()
    context.url_kwargs = {}
    # context.fixtures = ['dev_fixtures.json']


def after_all(context):
    context.driver.quit()
    context.driver = None


def before_scenario(context, scenario):
    # site = Site.objects.get_current()
    # site.name = 'localhost'
    # site.domain = context.get_url().split('http://')[1]
    # site.save()
    pass
