import json
import os
import re

from behave import *
from django.apps import apps
from django.conf import settings
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.ui import WebDriverWait

from ayrabo.utils.testing import string_to_kwargs_dict, get_user
from users.models import User


def find_element(context, element_to_find, multiple=False):
    """
    Given an element's id, class name, name, etc. try to find that element on the page

    :param multiple: Whether to return multiple elements or not
    :param context: The testing context (contains the driver, django test runner, etc)
    :param element_to_find: The id, name, etc of the element to be located
    :return: A selenium WebElement.
    """

    methods_to_find_by = ['id', 'class_name', 'css_selector', 'link_text', 'name', 'partial_link_text', 'tag_name',
                          'xpath']
    for method in methods_to_find_by:
        find_function = 'find_elements_by_{}' if multiple else 'find_element_by_{}'
        find_function = find_function.format(method)
        try:
            # NOTE: This might be an array of elements if `multiple` is specified.
            e = getattr(context.driver, find_function)(element_to_find)
            if not multiple or len(e) > 0:
                return e
        except (NoSuchElementException, WebDriverException):
            pass
    raise NoSuchElementException('{element} does not exist on the page'.format(element=element_to_find))


def navigate_to_page(context, url, url_kwargs=None):
    """
    Navigates to a url. Prepends the hostname and port. Url can be a url name, etc.

    :param context: The context for the current step definition
    :param url_kwargs: Any kwargs needed to successfully reverse the url
    :param url: The url to navigate to
    """
    if url_kwargs is None:
        url_kwargs = {}
    context.driver.get(context.get_url(url, **url_kwargs))


def get_first_obj_for_model(model_class, model_kwargs):
    """
    Given a model class name and any kwargs to filter by, return the first object in the resulting queryset

    :param model_class: The model to retrieve
    :param model_kwargs: Any kwargs the could be passed to the filter() function for the given model
    :return: An object of type model_class
    """
    if '.' not in model_class:
        raise Exception('You must specify the model class as <app_name>.<model_class> i.e. "sports.SportRegistration"')
    cls = apps.get_model(model_class)
    kwargs = string_to_kwargs_dict(model_kwargs)
    qs = cls.objects.filter(**kwargs)
    return qs.first()


"""

Page navigation and testing correct page

"""


@step('I am on the "(?P<url>[^"]*)" page')
def step_impl(context, url):
    navigate_to_page(context, url)


@step('I am on the "(?P<url>[^"]*)" page with kwargs "(?P<url_kwargs>[^"]*)"')
def step_impl(context, url, url_kwargs):
    kwargs = string_to_kwargs_dict(url_kwargs)
    navigate_to_page(context, url, kwargs)


@step('I go to the "(?P<url>[^"]*)" page')
def step_impl(context, url):
    navigate_to_page(context, url)


@step('I should be on the "(?P<url>.*)" page')
def step_impl(context, url):
    current_url = context.driver.current_url
    # Check for query params and discard if exist
    if '?' in current_url:
        current_url = current_url.split('?')[0]
    context.test.assertEqual(current_url, context.get_url(url))


@step('I should be on the "(?P<url>.*)" page with kwargs "(?P<url_kwargs>[^"]*)"')
def step_impl(context, url, url_kwargs):
    kwargs = string_to_kwargs_dict(url_kwargs)
    context.test.assertEqual(context.driver.current_url, context.get_url(url, **kwargs))


@step('I am on the absolute url page for "(?P<model_class>.*)" and "(?P<kwarg_data>.*)"')
def step_impl(context, model_class, kwarg_data):
    obj = get_first_obj_for_model(model_class, kwarg_data)
    navigate_to_page(context, obj.get_absolute_url())


@step('I go to the absolute url page for "(?P<model_class>.*)" and "(?P<kwarg_data>.*)"')
def step_impl(context, model_class, kwarg_data):
    obj = get_first_obj_for_model(model_class, kwarg_data)
    navigate_to_page(context, obj.get_absolute_url())


@step('I should be on the absolute url page for "(?P<model_class>.*)" and "(?P<kwarg_data>.*)"')
def step_impl(context, model_class, kwarg_data):
    obj = get_first_obj_for_model(model_class, kwarg_data)
    url_to_check = context.get_url(obj.get_absolute_url())
    context.test.assertEqual(url_to_check, context.driver.current_url)


@step('I am on the "(?P<model_class>[^"]*)" "(?P<model_kwargs>[^"]*)" "(?P<url_or_url_name>[^"]*)" page with url kwargs "(?P<url_kwargs>[^"]*)"')  # noqa
def step_impl(context, model_class, model_kwargs, url_or_url_name, url_kwargs):
    url_kwargs_dict = string_to_kwargs_dict(url_kwargs)
    obj = get_first_obj_for_model(model_class, model_kwargs)
    for key, val in url_kwargs_dict.items():
        try:
            url_kwargs_dict[key] = getattr(obj, val)
        except AttributeError as e:
            print(e)

    navigate_to_page(context, url_or_url_name, url_kwargs_dict)


@step('I go to the "(?P<model_class>[^"]*)" "(?P<model_kwargs>[^"]*)" "(?P<url_or_url_name>[^"]*)" page with url kwargs "(?P<url_kwargs>[^"]*)"')  # noqa
def step_impl(context, model_class, model_kwargs, url_or_url_name, url_kwargs):
    url_kwargs_dict = string_to_kwargs_dict(url_kwargs)
    obj = get_first_obj_for_model(model_class, model_kwargs)
    for key, val in url_kwargs_dict.items():
        try:
            url_kwargs_dict[key] = getattr(obj, val)
        except AttributeError as e:
            print(e)

    navigate_to_page(context, url_or_url_name, url_kwargs_dict)


@step('I should be on the "(?P<model_class>[^"]*)" "(?P<model_kwargs>[^"]*)" "(?P<url_or_url_name>[^"]*)" page with url kwargs "(?P<url_kwargs>[^"]*)"')  # noqa
def step_impl(context, model_class, model_kwargs, url_or_url_name, url_kwargs):
    url_kwargs_dict = string_to_kwargs_dict(url_kwargs)
    obj = get_first_obj_for_model(model_class, model_kwargs)
    for key, val in url_kwargs_dict.items():
        try:
            url_kwargs_dict[key] = getattr(obj, val)
        except AttributeError as e:
            print(e)

    context.test.assertEqual(context.get_url(url_or_url_name, **url_kwargs_dict), context.driver.current_url)


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


@step('I wait for a page refresh')
def step_impl(context):
    old_page = context.driver.find_element_by_tag_name('body')

    def check_for_refresh(driver):
        new_page = driver.find_element_by_tag_name('body')
        return new_page.id != old_page.id

    WebDriverWait(context.driver, 15).until(check_for_refresh)


@step('I press "(?P<prefix>[^"]*)" with kwargs "(?P<kwargs>[^"]*)"')
def step_impl(context, prefix, kwargs):
    element_selector = prefix + str(context.url_kwargs[kwargs])
    element = find_element(context, element_selector)
    element.click()


@step('I should see "(?P<text>.*)"')
def step_impl(context, text):
    context.test.assertIn(text, str(context.driver.page_source))


@step('The page should contain "(?P<text>.*)"')
def step_impl(context, text):
    bodyText = find_element(context, 'body').text
    context.test.assertIn(text, bodyText)


@step('I should not see "(?P<text>.*)"')
def step_impl(context, text):
    context.test.assertNotIn(text, str(context.driver.page_source))


@step('A user account should exist for "(?P<username_or_email>.*)"')
def step_impl(context, username_or_email):
    context.test.assertIsInstance(get_user(username_or_email), User)


@step('"(?P<text>.*)" should show up (?P<num>\d+) times?')
def step_impl(context, text, num):
    # findall returns a list of all matches
    num_matches = len(re.findall(text, context.driver.page_source))
    context.test.assertEqual(int(num), num_matches)


@step('I (?P<deselect>de)?select "(?P<select_option>[^"]*)" from "(?P<element>[^"]*)"')
def step_impl(context, deselect, select_option, element):
    success = False
    the_element = Select(find_element(context, element))
    try:
        if deselect:
            the_element.deselect_by_value(select_option)
        else:
            the_element.select_by_value(select_option)
        success = True
    except NoSuchElementException:
        pass

    try:
        if deselect:
            the_element.deselect_by_visible_text(select_option)
        else:
            the_element.select_by_visible_text(select_option)
        success = True
    except NoSuchElementException:
        pass

    try:
        if deselect:
            the_element.deselect_by_index(int(select_option))
        else:
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
    # NOTE: If this is failing, make sure the html element actually supports the disabled attribute.
    the_element = find_element(context, element)
    result = the_element.is_enabled()
    if prefix == 'dis':
        result = not result
    context.test.assertTrue(result)


@step('I wait for "(?P<element>[^"]*)" to be visible')
def step_impl(context, element):
    WebDriverWait(context.driver, 10).until(expected_conditions.visibility_of_element_located((By.ID, element)))


@step('I wait for "(?P<element>[^"]*)" to be removed')
def step_impl(context, element):
    # For some reason the find_element method w/ multiple=True isn't working.
    elements = context.driver.find_elements_by_css_selector(element)
    WebDriverWait(context.driver, 10).until(expected_conditions.staleness_of(elements[1]))


@step('"(?P<element>[^"]*)" should have value "(?P<value>[^"]*)"')
def step_impl(context, element, value):
    the_element = find_element(context, element)
    context.test.assertEqual(value, the_element.get_property("value"))


@step('"(?P<element>[^"]*)" should contain text "(?P<text>[^"]*)"')
def step_impl(context, element, text):
    the_element = find_element(context, element)
    element_text = the_element.text
    split_text = [t.strip() for t in text.split(',')]
    for t in split_text:
        context.test.assertIn(t, element_text)


@step('"(?P<element>[^"]*)" should not exist on the page')
def step_impl(context, element):
    with context.test.assertRaises(NoSuchElementException):
        find_element(context, element)


@step('"(?P<element>[^"]*)" should exist on the page')
def step_impl(context, element):
    find_element(context, element)


@step('The "(?P<attribute>[^"]*)" attribute for "(?P<element>[^"]*)" should have values "(?P<values>[^"]*)"')
def step_impl(context, attribute, element, values):
    the_element = find_element(context, element)
    attribute_values = the_element.get_attribute(attribute)
    context.test.assertEqual(attribute_values, values)


@step('I view the console logs')
def step_impl(context):
    logs = context.driver.get_log('browser')
    print(json.dumps(logs, indent=2))
