import re

from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from sports.models import Sport


def validate_height(height):
    """
    Validates that param height conforms to the following format: 5' 7"
    The first number can be any number 1-9, followed by a ' and then a space
    The second number(s) can be any number 0-9 or 10 or 11 followed by a "
    :param height: The height to check
    :raises ValidationError if height does not follow the formatting
    """
    regex = re.compile('''^[1-9]'( ([0-9]|1[0-1])")?$''')
    if re.match(regex, height) is None:
        raise ValidationError('Invalid format, please use the following format: 5\' 7\"')


class UserProfile(models.Model):
    """
    Model used to store additional information for a user
    """
    GENDERS = [('Male', 'Male'), ('Female', 'Female')]

    MIN_WEIGHT = 1
    MAX_WEIGHT = 400

    user = models.OneToOneField(User)
    gender = models.CharField(max_length=128, choices=GENDERS, verbose_name='Gender')
    birthday = models.DateField(verbose_name='Birthday')
    height = models.CharField(max_length=8, validators=[validate_height], verbose_name='Height',
                              help_text='Use the following format: 5\' 7\"')
    weight = models.SmallIntegerField(verbose_name='Weight',
                                      validators=[MinValueValidator(MIN_WEIGHT), MaxValueValidator(MAX_WEIGHT)],
                                      help_text='Round to the nearest whole number')
    # settings.LANGUAGE_CODE is en-us, while LANGUAGES only contains en, so default to regular en instead of en-us
    language = models.CharField(max_length=128, choices=LANGUAGES, default='en', verbose_name='Language')
    timezone = models.CharField(max_length=128, choices=settings.COMMON_TIMEZONES, default=settings.TIME_ZONE,
                                verbose_name='Timezone')

    def __str__(self):
        return self.user.email
