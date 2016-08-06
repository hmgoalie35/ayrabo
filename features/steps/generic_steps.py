import os
import re

from behave import *
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Q
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


def find_element(context, element_to_find):
    """
    Given an element's id, class name, name, etc. try to find that element on the page
    :param context: The testing context (contains the driver, django test runner, etc)
    :param element_to_find: The id, name, etc of the element to be located
    :return: A selenium WebElement. API available at https://selenium-python.readthedocs.io/api.html#module-selenium.webdriver.remote.webelement
    """
    methods_to_find_by = [By.ID, By.CLASS_NAME, By.CSS_SELECTOR, By.LINK_TEXT, By.NAME, By.PARTIAL_LINK_TEXT,
                          By.TAG_NAME, By.XPATH]
    for method in methods_to_find_by:
        try:
            element = context.driver.find_element(method, element_to_find)
            return element
        except NoSuchElementException:
            pass
        except WebDriverException:
            pass
    raise NoSuchElementException('{element} does not exist on the page'.format(element=element_to_find))


@given('I am on the "(?P<url>.*)" page')
def step_impl(context, url):
    context.driver.get(context.get_url(url))


@step('I go to the "(?P<url>[^"]*)" page')
def step_impl(context, url):
    step = 'given I am on the "{url}" page\n'.format(url=url)
    context.execute_steps(step)


@step('The current url should contain "(?P<text>.*)"')
def step_impl(context, text):
    context.test.assertIn(text, context.driver.current_url)


@step('I fill in "(?P<element>.*)" with "(?P<value>.*)"')
def step_impl(context, element, value):
    the_element = find_element(context, element)
    the_element.clear()
    the_element.send_keys(value)


@step('I press "(?P<element>.*)"')
def step_impl(context, element):
    the_element = find_element(context, element)
    the_element.click()


@step('I should be on the "(?P<url>.*)" page')
def step_impl(context, url):
    current_url = context.driver.current_url
    # Check for query params and discard if exist
    if '?' in context.driver.current_url:
        current_url = current_url.split('?')[0]
    context.test.assertEqual(current_url, context.get_url(url))


@step('I should see "(?P<text>.*)"')
def step_impl(context, text):
    context.test.assertIn(text, str(context.driver.page_source))


@step('I should not see "(?P<text>.*)"')
def step_impl(context, text):
    context.test.assertNotIn(text, str(context.driver.page_source))


@step('A user account should exist for "(?P<username_or_email>.*)"')
def step_impl(context, username_or_email):
    context.test.assertIsInstance(User.objects.get(Q(username=username_or_email) | Q(email=username_or_email)), User)


@step('"(?P<text>.*)" should show up (?P<num>.*) times?')
def step_impl(context, text, num):
    # findall returns a list of all matches
    num_matches = len(re.findall(text, context.driver.page_source))
    context.test.assertEqual(int(num), num_matches)


@step('I select "(?P<select_option>[^"]*)" from "(?P<element>[^"]*)"')
def step_impl(context, select_option, element):
    success = False
    the_element = Select(find_element(context, element))
    try:
        the_element.select_by_value(select_option)
        success = True
    except NoSuchElementException:
        pass

    try:
        the_element.select_by_visible_text(select_option)
        success = True
    except NoSuchElementException:
        pass

    try:
        the_element.select_by_index(int(select_option))
        success = True
    except TypeError:
        pass
    except ValueError:
        pass
    except NoSuchElementException:
        pass

    if not success:
        raise NoSuchElementException(
                'Cannot locate {select_option} by value, visible text or index'.format(select_option=select_option))


@step('"(?P<element>.*)" should not have the option "(?P<option_text>.*)"')
def step_impl(context, element, option_text):
    the_element = Select(find_element(context, element))
    options = the_element.options
    text_dne = True
    for option in options:
        if option.text == option_text:
            text_dne = False
            break
    context.test.assertTrue(text_dne)

@step('I upload "(?P<file_name>.*)" into "(?P<element>.*)"')
def step_impl(context, file_name, element):
    the_element = find_element(context, element)
    file_path = os.path.join(settings.BASE_DIR, 'static', 'csv_examples', 'testing', file_name)
    the_element.send_keys(file_path)


@step('"(?P<element>.*)" should be visible')
def step_impl(context, element):
    the_element = find_element(context, element)
    context.test.assertTrue(the_element.is_displayed())


@step('"(?P<element>.*)" should not be visible')
def step_impl(context, element):
    the_element = find_element(context, element)
    context.test.assertFalse(the_element.is_displayed())


@step('"(?P<element>.*)" should be (?P<prefix>dis|en)abled')
def step_impl(context, element, prefix):
    the_element = find_element(context, element)
    result = the_element.is_enabled()
    if prefix == 'dis':
        result = not result
    context.test.assertTrue(result)
