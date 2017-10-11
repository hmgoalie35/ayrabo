import datetime
import random

import factory
from django.conf import settings
from factory import django, Faker

from userprofiles.models import UserProfile


def generate_height():
    return '%s\' %s\"' % (random.randint(1, 8), random.randint(0, 11))


def generate_birthday():
    return '{year}-{month}-{day}'.format(year=datetime.datetime.now().year, month=datetime.datetime.now().month,
                                         day=datetime.datetime.now().day)


class UserProfileFactory(django.DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory('accounts.tests.factories.UserFactory.UserFactory', userprofile=None)
    gender = Faker('random_element', elements=['male', 'female'])
    birthday = factory.LazyFunction(generate_birthday)
    height = factory.LazyFunction(generate_height)
    weight = Faker('random_int', min=UserProfile.MIN_WEIGHT, max=UserProfile.MAX_WEIGHT)
    # see django.conf.global_settings.LANGUAGES for all available languages
    language = 'en'
    # see COMMON_TIMEZONES in the settings file for all available timezones
    timezone = settings.TIME_ZONE
