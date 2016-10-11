import os
import re

from behave import *
from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Q
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait


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


def string_to_kwargs_dict(string):
    """
    Given a string of the form "a=b, c=d" returns a dictionary of key-value pairs. i.e {'a': 'b', 'c': 'd'}
    The purpose is so the return dictionary can be used with ** to pass kwargs to functions.
    :param string: A string of the form "a=b, c=d"
    :return: A dictionary of key value pairs. The key is derived from the left side of = and the value is from the right
    side
    """
    ret_val = {}
    for kwarg in string.split(', '):
        val = kwarg.strip().split('=')
        for i in range(len(val) - 1):
            ret_val[val[i]] = val[i + 1]
    return ret_val


@step('I am on the "(?P<url>.*)" page')
def step_impl(context, url):
    context.driver.get(context.get_url(url))


@step('I go to the "(?P<url>[^"]*)" page')
def step_impl(context, url):
    the_step = 'given I am on the "{url}" page\n'.format(url=url)
    context.execute_steps(the_step)


@step('I should be on the page for "(?P<model_class>.*)" and "(?P<kwarg_data>.*)"')
def step_impl(context, model_class, kwarg_data):
    if '.' not in model_class:
        raise Exception('You must specify the model class as <app_name>.<model_class> i.e. "sports.SportRegistration"')
    cls = apps.get_model(model_class)
    kwargs = string_to_kwargs_dict(kwarg_data)
    qs = cls.objects.filter(**kwargs)
    obj = qs.first()
    context.test.assertEqual(context.get_url(obj.get_absolute_url()), context.driver.current_url)


@step('I should be on the "(?P<model_class>[^"]*)" "(?P<model_kwargs>[^"]*)" "(?P<url_or_url_name>[^"]*)" page with url kwargs "(?P<url_kwargs>[^"]*)"')
def step_impl(context, model_class, model_kwargs, url_or_url_name, url_kwargs):
    cls = apps.get_model(model_class)
    model_kwargs_dict = string_to_kwargs_dict(model_kwargs)
    url_kwargs_dict = string_to_kwargs_dict(url_kwargs)
    qs = cls.objects.filter(**model_kwargs_dict)
    obj = qs.first()

    for key, val in url_kwargs_dict.items():
        try:
            url_kwargs_dict[key] = getattr(obj, val)
        except AttributeError as e:
            print(e)

    context.test.assertEqual(context.get_url(url_or_url_name, **url_kwargs_dict), context.driver.current_url)


@step('I am on the page for "(?P<model_class>.*)" and "(?P<kwarg_data>.*)"')
def step_impl(context, model_class, kwarg_data):
    if '.' not in model_class:
        raise Exception('You must specify the model class as <app_name>.<model_class> i.e. "sports.SportRegistration"')
    cls = apps.get_model(model_class)
    kwargs = string_to_kwargs_dict(kwarg_data)
    qs = cls.objects.filter(**kwargs)
    obj = qs.first()
    context.driver.get(context.get_url(obj.get_absolute_url()))


@step('I am on the "(?P<model_class>[^"]*)" "(?P<model_kwargs>[^"]*)" "(?P<url_or_url_name>[^"]*)" page with url kwargs "(?P<url_kwargs>[^"]*)"')
def step_impl(context, model_class, model_kwargs, url_or_url_name, url_kwargs):
    cls = apps.get_model(model_class)
    model_kwargs_dict = string_to_kwargs_dict(model_kwargs)
    url_kwargs_dict = string_to_kwargs_dict(url_kwargs)
    qs = cls.objects.filter(**model_kwargs_dict)
    obj = qs.first()
    for key, val in url_kwargs_dict.items():
        try:
            url_kwargs_dict[key] = getattr(obj, val)
        except AttributeError as e:
            print(e)

    context.driver.get(context.get_url(url_or_url_name, **url_kwargs_dict))


@step('I go to the "(?P<model_class>[^"]*)" "(?P<model_kwargs>[^"]*)" "(?P<url_or_url_name>[^"]*)" page with url kwargs "(?P<url_kwargs>[^"]*)"')
def step_impl(context, model_class, model_kwargs, url_or_url_name, url_kwargs):
    cls = apps.get_model(model_class)
    model_kwargs_dict = string_to_kwargs_dict(model_kwargs)
    url_kwargs_dict = string_to_kwargs_dict(url_kwargs)
    qs = cls.objects.filter(**model_kwargs_dict)
    obj = qs.first()
    for key, val in url_kwargs_dict.items():
        try:
            url_kwargs_dict[key] = getattr(obj, val)
        except AttributeError as e:
            print(e)

    context.driver.get(context.get_url(url_or_url_name, **url_kwargs_dict))


@step('The current url should contain "(?P<text>.*)"')
def step_impl(context, text):
    context.test.assertIn(text, context.driver.current_url)


@step('I fill in "(?P<element>.*)" with "(?P<value>.*)"')
def step_impl(context, element, value):
    the_element = find_element(context, element)
    the_element.clear()
    the_element.send_keys(value)


@step('I press "(?P<element>[^"]*)"')
def step_impl(context, element):
    the_element = find_element(context, element)
    the_element.click()


@step('I press "(?P<element>[^"]*)" which opens "(?P<modal_id>.*)"')
def step_impl(context, element, modal_id):
    """
    Waits for the given modal to be clickable (i.e. displayed and clickable)
    """
    the_element = find_element(context, element)
    the_element.click()
    WebDriverWait(context.driver, 10).until(
            expected_conditions.element_to_be_clickable((By.ID, modal_id)),
    )


@step('I wait for any ajax calls to finish')
def step_impl(context):
    WebDriverWait(context.driver, 30).until(lambda driver: driver.execute_script("return jQuery.active === 0"))


@step('I press "(?P<prefix>[^"]*)" with kwargs "(?P<kwargs>[^"]*)"')
def step_impl(context, prefix, kwargs):
    element_selector = prefix + str(context.url_kwargs[kwargs])
    element = find_element(context, element_selector)
    element.click()


@step('I should be on the "(?P<url>.*)" page')
def step_impl(context, url):
    current_url = context.driver.current_url
    # Check for query params and discard if exist
    if '?' in current_url:
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


@step('I select (?P<num_selections>\d+) [a-zA-Z]+ from "(?P<element>[^"]*)"')
def step_impl(context, num_selections, element):
    the_element = Select(find_element(context, element))
    for i in range(0, int(num_selections)):
        the_element.select_by_index(i)


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


@step('"(?P<element>.*)" should (?P<negate>not )?be visible')
def step_impl(context, element, negate):
    the_element = find_element(context, element)
    WebDriverWait(context.driver, 10).until(
            expected_conditions.visibility_of_element_located((By.ID, element)),
    )
    is_displayed = the_element.is_displayed()
    if negate:
        is_displayed = not is_displayed
    context.test.assertTrue(is_displayed)


@step('"(?P<element>.*)" should be (?P<prefix>dis|en)abled')
def step_impl(context, element, prefix):
    the_element = find_element(context, element)
    result = the_element.is_enabled()
    if prefix == 'dis':
        result = not result
    context.test.assertTrue(result)


@step('I wait for "(?P<element>[^"]*)" to be visible')
def step_impl(context, element):
    WebDriverWait(context.driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, element)))
