import re

from django.conf import settings
from django.conf.global_settings import LANGUAGES
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models

MIN_WEIGHT = 0
MAX_WEIGHT = 400


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


def validate_weight(weight):
    """
    Checks to see if weight is between MIN_WEIGHT and MAX_WEIGHT
    :param weight: The weight to check
    :raises ValidationError if weight > MIN_WEIGHT or weight <= MAX_WEIGHT
    """
    if weight <= MIN_WEIGHT or weight > MAX_WEIGHT:
        raise ValidationError('Weight must be greater than zero and less than 400')


class UserProfile(models.Model):
    """
    Model used to store additional information for a user
    """
    GENDERS = [('male', 'Male'), ('female', 'Female')]

    ROLES = ['Player', 'Coach', 'Referee', 'Manager']

    user = models.OneToOneField(User)
    roles_mask = models.SmallIntegerField(default=0, verbose_name='Roles Mask')
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
    # This will be used to check if the appropriate player, coach, referee, manager objects have been created
    # after the initial userprofile creation. It will be False if the aforementioned objects have
    # not been created, True otherwise
    is_complete = models.BooleanField(default=False, verbose_name='Is Profile Complete')

    def set_roles(self, roles, append=False):
        """
        Given a list of roles (taken from ROLES) creates a mask (int) that represents the roles currently valid for the
        user
        :param append: Set to True to indicate you want to append roles to any existent roles, set to False to overwrite
        any existing roles with roles
        :param roles: The role(s) to add
        """

        assert type(roles) == list

        # & performs an intersection and will omit any roles that are misspelled or DNE
        valid_roles = set(roles) & set(self.ROLES)
        accumulator = 0
        for role in valid_roles:
            accumulator += 2 ** self.ROLES.index(role)
        if append:
            self.roles_mask += accumulator
        else:
            self.roles_mask = accumulator
        self.save()

    @property
    def roles(self):
        """
        Converts the role mask (int) to the actual roles (strings)
        :return: A list containing all of the roles associated with the user
        """
        return [role for role in self.ROLES if (self.roles_mask & 2 ** self.ROLES.index(role)) != 0]

    def has_role(self, role):
        """
        Checks to see if the current user has the specified role
        :param role: The role to check for (case insensitive)
        :return: True if the user has the current role, False otherwise
        """
        return role.title() in self.roles or role in self.roles

    def __str__(self):
        return self.user.email
