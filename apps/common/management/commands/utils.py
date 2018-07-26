from django.core.exceptions import ValidationError
from django.db import IntegrityError


def get_object(cls, **kwargs):
    try:
        return cls.objects.get(**kwargs)
    except cls.DoesNotExist:
        return None


def create_object(cls, exclude=None, **kwargs):
    exclude = exclude or []
    created = False
    try:
        instance = cls(**kwargs)
        instance.full_clean(exclude=exclude)
        instance.save()
        created = True
    except (IntegrityError, ValidationError):
        instance = get_object(cls, **kwargs)
    return instance, created


def print_status(stdout, obj, created=False, updated=False):
    if created:
        status = 'Created'
    elif updated:
        status = 'Updated'
    else:
        status = 'Skipped'
    stdout.write('{} {}'.format(status, obj))
