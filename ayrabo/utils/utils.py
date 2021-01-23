"""
A module to store useful helper functions used throughout the code base
"""
import os

from django.core import mail
from django.shortcuts import render
from django.utils.crypto import get_random_string
from django.utils.deconstruct import deconstructible


def remove_form_placeholders(field_list):
    """
    Django all-auth by default adds in annoying placeholders, so remove them from all fields in the given list

    :param field_list: A list of fields to have placeholders removed
    """
    for field_name in field_list:
        attributes = field_list.get(field_name).widget.attrs
        if 'placeholder' in attributes:
            attributes.pop('placeholder')


def add_autofocus_to_field(field):
    field.widget.attrs['autofocus'] = 'true'


def set_fields_disabled(read_only_fields, field_list):
    """
    Given a list of form fields, sets them to disabled so the HTML form being rendered shows them as disabled.
    Django will also ignore any POST data that has the field's name attribute in it (in the case of tampering)

    __all__ can be specified to disable all fields.

    :param read_only_fields: The fields to mark as disabled
    :param field_list: The list of fields of the form
    """
    if '__all__' in read_only_fields:
        read_only_fields = [field for field in field_list]

    for field in read_only_fields:
        the_field = field_list.get(field, None)
        if the_field is not None:
            the_field.disabled = True


def send_sport_not_configured_email(sport_name, view_cls):
    """
    Email the configured admins alerting them a sport was not configured properly.

    :param sport_name: Name of the sport that has been misconfigured
    :param view_cls: The Django view that caused the exception
    """
    mail.mail_admins(
        f'{sport_name} misconfigured',
        f'{sport_name} misconfigured on the {view_cls.request.path} ({view_cls.__class__.__name__}) page.'
    )


def send_season_not_configured_email(obj_name, view_cls):
    """
    Email the configured admins alerting them a season does not exist when it should.

    :param obj_name: Name of the object (generally team or league) that does not have an associated season.
    :param view_cls: The Django view that could not compute a season
    """
    mail.mail_admins(
        f'Season for {obj_name} misconfigured',
        f'Season for {obj_name} misconfigured on the {view_cls.request.path} ({view_cls.__class__.__name__}) page.'
    )


def handle_sport_not_configured(request, cls, e):
    """
    If a sport is not configured correctly, show an error page to the user and email site admins.

    :param request: The request
    :param cls: The view class the exception occurred in.
    :param e: The exception
    """
    send_sport_not_configured_email(e.sport, cls)
    return render(request, 'misconfigurations/base.html', {'message': e.message})


def get_namespace_for_role(role):
    """
    Given a role, returns the correct url namespace

    :param role: The role
    :return: The namespace for `role` or `None` if the role DNE.
    """
    mappings = {
        'Player': 'players',
        'Coach': 'coaches',
        'Referee': 'referees',
        'Manager': 'managers',
        'Scorekeeper': 'scorekeepers'
    }
    return mappings.get(role, None)


@deconstructible
class UploadTo(object):
    def __init__(self, path):
        self.path = path

    def __call__(self, instance, filename):
        parts = os.path.splitext(filename)
        unique_filename = '{}{}'.format(get_random_string(12), parts[1])
        return os.path.join(self.path, unique_filename)

    def __eq__(self, other):
        return self.path == other.path


def chunk(iterable, n):
    """
    Yield successive n-sized chunks from the iterable
    """
    for i in range(0, len(iterable), n):
        yield iterable[i:i + n]


def pluralize(text, count, suffix):
    return text if count == 1 else f'{text}{suffix}'


def timedelta_to_hours_minutes_seconds(td):
    total_seconds = td.total_seconds()
    hours, remaining = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remaining, 60)
    return hours, minutes, seconds
