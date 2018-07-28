from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import IntegrityError
from django.db.models import Q

from common.management.seed_data.data import GENERIC_CHOICES, GENERIC_PENALTY_CHOICES, SPORTS
from common.models import GenericChoice
from penalties.models import GenericPenaltyChoice
from sports.models import Sport
from common.management.commands.utils import create_object


class Command(BaseCommand):
    help = 'Top level seed command that calls other seed commands. Seeds initial data for the site.'

    def print_status(self, obj, created):
        self.stdout.write('{} {}'.format('Created' if created else 'Skipped', obj))

    def handle(self, *args, **options):
        site_domain = 'ayrabo.com'
        site_name = 'ayrabo'

        self.stdout.write('Updating default site name...')
        try:
            site = Site.objects.get(Q(name='example.com') | Q(name='escoresheet.com'))
            site.domain = site_domain
            site.name = site_name
            site.save()
        except Site.DoesNotExist:
            pass
        self.stdout.write('\n')

        # TODO Create leagues/teams, seasons... Cron job for seasons?
        self.stdout.write('Seeding sports...')
        sports = []
        for sport in SPORTS:
            obj, created = create_object(Sport, exclude=['slug'], name=sport)
            sports.append(obj)
            self.print_status(obj, created)
        self.stdout.write('\n')

        self.stdout.write('Seeding generic sport choices...')
        # TODO Can probably iterate over keys for `GENERIC_CHOICES` and do a lookup in a hash table to get the actual
        # sport object.
        for sport in sports:
            choices = GENERIC_CHOICES.get(sport.name, [])
            for choice in choices:
                choice.update({'content_object': sport})
                try:
                    obj = GenericChoice.objects.create(**choice)
                    created = True
                except IntegrityError:
                    obj = choice.get('long_value')
                    created = False
                self.print_status(obj, created)
        self.stdout.write('\n')

        self.stdout.write('Seeding generic penalty choices...')
        # See TODO above
        for sport in sports:
            choices = GENERIC_PENALTY_CHOICES.get(sport.name, [])
            for choice in choices:
                choice.update({'content_object': sport})
                try:
                    obj = GenericPenaltyChoice.objects.create(**choice)
                    created = True
                except IntegrityError:
                    obj = choice.get('name')
                    created = False
                self.print_status(obj, created)
        self.stdout.write('\n')

        self.stdout.write('Seeding waffle switches, flags, samples...')
        call_command('seed_waffle')
        self.stdout.write('\n')
