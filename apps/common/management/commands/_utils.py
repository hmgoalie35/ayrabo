def get_or_create(cls, get_kwargs, create_kwargs, exclude=None):
    exclude = exclude or []
    created = False
    try:
        obj = cls.objects.get(**get_kwargs)
    except cls.DoesNotExist:
        obj = cls(**create_kwargs)
        created = True

    if created:
        # This can throw ValidationError
        obj.full_clean(exclude=exclude)
        obj.save()

    return obj, created


def print_status(stdout, obj, created=False, updated=False):
    if created:
        status = 'Created'
    elif updated:
        status = 'Updated'
    else:
        status = 'Skipped'
    stdout.write(f'{status} {obj}')
