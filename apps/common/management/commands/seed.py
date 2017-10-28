from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand

from sports.models import Sport

SPORTS = ['Ice Hockey', 'Baseball']
SITE_NAME = 'escoresheet.com'


class Command(BaseCommand):
    help = 'Configures the project with sports, etc.'

    def handle(self, *args, **options):
        # TODO Create leagues/teams, seasons... Cron job for seasons?
        for sport in SPORTS:
            obj, created = Sport.objects.get_or_create(name=sport)
            obj.clean()
            print('{}: Created: {}'.format(obj, created))

        try:
            site = Site.objects.get(name='example.com')
            site.domain = SITE_NAME
            site.name = SITE_NAME
            print('Updating default site...')
            site.save()
        except Site.DoesNotExist:
            pass
