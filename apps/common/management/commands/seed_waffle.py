from django.core.management import BaseCommand
from waffle.models import Switch

from common.management.commands.utils import create_object, get_object, print_status


class Command(BaseCommand):
    help = 'Seeds waffle flags, switches, samples'

    def handle(self, *args, **options):
        switches = [
            {
                'name': 'sport_registrations',
                'active': False,
                'note': 'Specifies if the user should be prompted to create sport registrations.'
            }
        ]

        # TODO Handle updates to switches, however there are 2 issues. 1. If the switches are modified via the admin,
        # this will overwrite those changes. This file should be the ultimate authority. 2. After first run, the
        # switches will always be updated. Consider adding a command line flag (which probably isn't the best because
        # we need to remember to deploy with the flag enabled)
        for switch in switches:
            created = False
            # We are going to use `name` as the unique identifier to make sure duplicates aren't created.
            obj = get_object(Switch, name=switch.get('name'))
            if obj is None:
                obj = create_object(Switch, **switch)
                created = True
            print_status(self.stdout, obj, created)
