from django.core.management.base import BaseCommand

from sports.models import Sport
from django.contrib.sites.models import Site

SPORTS = ['Ice Hockey', 'Baseball']


class Command(BaseCommand):
    help = 'Configures the project with sports, etc.'

    def handle(self, *args, **options):
        for sport in SPORTS:
            obj, created = Sport.objects.get_or_create(name=sport)
            obj.clean()
            print('{}: Created: {}'.format(obj, created))

        try:
            site = Site.objects.get(name='example.com')
            site.domain = 'escoresheet.com'
            site.name = 'escoresheet.com'
            print('Updating default site...')
            site.save()
        except Site.DoesNotExist:
            pass
