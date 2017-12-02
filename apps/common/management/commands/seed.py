from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand
from django.db import IntegrityError

from common.models import GenericChoice
from sports.models import Sport


SPORTS = ['Ice Hockey', 'Baseball']
GENERIC_CHOICES = {
    'Ice Hockey': [
        {'short_value': 'exhibition', 'long_value': 'Exhibition'},
        {'short_value': 'league', 'long_value': 'League'}
    ]
}
SITE_NAME = 'escoresheet.com'


class Command(BaseCommand):
    help = 'Configures the project with sports, etc.'

    def print_status(self, obj, created):
        self.stdout.write('{} {}'.format('Created' if created else 'Skipped', obj))

    def handle(self, *args, **options):

        self.stdout.write('Updating default site name...')
        try:
            site = Site.objects.get(name='example.com')
            site.domain = SITE_NAME
            site.name = SITE_NAME
            site.save()
        except Site.DoesNotExist:
            pass
        print()

        # TODO Create leagues/teams, seasons... Cron job for seasons?
        self.stdout.write('Seeding sports...')
        sports = []
        for sport in SPORTS:
            obj, created = Sport.objects.get_or_create(name=sport)
            obj.full_clean()
            sports.append(obj)
            self.print_status(obj, created)
        print()

        self.stdout.write('Seeding generic sport choices...')
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
