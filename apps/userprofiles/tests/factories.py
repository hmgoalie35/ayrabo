import datetime
import random

from django.conf import settings
from factory import Faker, LazyFunction, SubFactory, django

from userprofiles.models import UserProfile


def generate_height():
    return '%s\' %s\"' % (random.randint(1, 8), random.randint(0, 11))


def generate_birthday():
    return datetime.date.today().strftime('%Y-%m-%d')


class UserProfileFactory(django.DjangoModelFactory):
    user = SubFactory('users.tests.UserFactory', userprofile=None)
    gender = Faker('random_element', elements=[gender[0] for gender in UserProfile.GENDERS])
    birthday = LazyFunction(generate_birthday)
    height = LazyFunction(generate_height)
    weight = Faker('random_int', min=UserProfile.MIN_WEIGHT, max=UserProfile.MAX_WEIGHT)
    # see django.conf.global_settings.LANGUAGES for all available languages
    language = 'en'
    # see COMMON_TIMEZONES in the settings file for all available timezones
    timezone = settings.TIME_ZONE

    class Meta:
        model = UserProfile
