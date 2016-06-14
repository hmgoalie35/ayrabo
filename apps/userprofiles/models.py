import re

from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

MIN_WEIGHT = 0
MAX_WEIGHT = 400


def validate_height(height):
    regex = re.compile('''^[1-9]'( ([0-9]|1[0-1])")?$''')
    if re.match(regex, height) is None:
        raise ValidationError('Invalid format, please use the following format: 5\' 7\"')


def validate_weight(weight):
    if weight <= MIN_WEIGHT or weight > MAX_WEIGHT:
        raise ValidationError('Weight must be greater than zero and less than 400')


class UserProfile(models.Model):
    GENDERS = [('male', 'Male'), ('female', 'Female')]

    user = models.OneToOneField(User)
    gender = models.CharField(max_length=128, choices=GENDERS, verbose_name='Gender')
    birthday = models.DateField(verbose_name='Birthday')
    height = models.CharField(max_length=8, validators=[validate_height], verbose_name='Height',
                              help_text='Use the following format: 5\' 7\"')
    weight = models.SmallIntegerField(verbose_name='Weight', validators=[validate_weight],
                                      help_text='Round to the nearest whole number')
    # settings.LANGUAGE_CODE is en-us, while LANGUAGES only contains en, so default to regular en instead of en-us
    language = models.CharField(max_length=128, choices=LANGUAGES, default='en', verbose_name='Language')
    timezone = models.CharField(max_length=128, choices=settings.COMMON_TIMEZONES, default=settings.TIME_ZONE,
                                verbose_name='Timezone')

    def __str__(self):
        return self.user.email
