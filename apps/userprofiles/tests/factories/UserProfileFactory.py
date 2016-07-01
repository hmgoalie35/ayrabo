import datetime
import random

import factory
import factory.fuzzy
from django.conf import settings
from factory.django import DjangoModelFactory

from userprofiles.models import UserProfile


def generate_height():
    return '%s\' %s\"' % (random.randint(1, 8), random.randint(0, 11))


def generate_birthday():
    return '{year}-{month}-{day}'.format(year=datetime.datetime.now().year, month=datetime.datetime.now().month,
                                         day=datetime.datetime.now().day)


class UserProfileFactory(DjangoModelFactory):
    class Meta:
        model = UserProfile

    user = factory.SubFactory('accounts.tests.factories.UserFactory.UserFactory', userprofile=None)
    # 1 signifies having only the Player role
    roles_mask = 1
    gender = factory.fuzzy.FuzzyChoice(['male', 'female'])
    birthday = factory.LazyFunction(generate_birthday)
    height = factory.LazyFunction(generate_height)
    weight = factory.fuzzy.FuzzyInteger(1, 399)
    # see django.conf.global_settings.LANGUAGES for all available languages
    language = 'en'
    # see COMMON_TIMEZONES in the settings file for all available timezones
    timezone = settings.TIME_ZONE
    is_complete = True
