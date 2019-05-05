import os

from behave import use_step_matcher
from django.conf import settings
from selenium import webdriver


use_step_matcher('re')

CHROMEDRIVER_BINARY = os.path.join(settings.NODE_MODULES_DIR, 'chromedriver/bin/chromedriver')
FIREFOX_BINARY = os.path.join(settings.NODE_MODULES_DIR, 'geckodriver/bin/geckodriver')


def chrome():
    options = webdriver.ChromeOptions()
    options.headless = True
    return webdriver.Chrome(executable_path=CHROMEDRIVER_BINARY, options=options)


def firefox():
    options = webdriver.FirefoxOptions()
    options.headless = True
    return webdriver.Firefox(executable_path=FIREFOX_BINARY, options=options)


def before_all(context):
    context.fixtures = ['sites.json']
    context.driver = chrome()
    context.driver.maximize_window()


def after_all(context):
    context.driver.quit()
    context.driver = None
