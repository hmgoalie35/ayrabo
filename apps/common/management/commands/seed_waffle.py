from django.core.management import BaseCommand
from waffle.models import Switch

from common.management.commands._utils import get_or_create, print_status


class Command(BaseCommand):
    help = 'Seeds waffle flags, switches, samples'

    def make_waffles(self, cls, waffles):
        for waffle in waffles:
            # We are going to use `name` as the unique identifier to make sure duplicates aren't created.
            obj, created = get_or_create(cls, get_kwargs={'name': waffle.get('name')}, create_kwargs=waffle)
            print_status(self.stdout, obj, created)

    def handle(self, *args, **options):
        switches = [
            {
                'name': 'sport_registrations',
                'active': False,
                'note': 'Specifies if the user should be prompted to create sport registrations.'
            },
            {
                'name': 'player_update',
                'active': False,
                'note': 'Specifies if the user can update the players associated with their account.'
            },
            {
                'name': 'coach_update',
                'active': False,
                'note': 'Specifies if the user can update the coaches associated with their account.'
            }
        ]

        self.make_waffles(Switch, switches)
