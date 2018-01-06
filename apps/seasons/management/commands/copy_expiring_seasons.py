import datetime
from datetime import date

from django.core.management.base import BaseCommand

from seasons.models import Season

EXPIRATION_DAYS = 30


class Command(BaseCommand):
    help = 'Creates new seasons based off of seasons that are about to expire.'

    def handle(self, *args, **options):
        today = date.today()
        one_year = datetime.timedelta(days=365)
        copied = 0
        skipped = 0
        seasons = Season.objects.filter(end_date__lte=today + datetime.timedelta(days=EXPIRATION_DAYS))
        for s in seasons:
            start_date = s.end_date
            end_date = s.end_date + one_year
            if Season.objects.filter(start_date__year=start_date.year, end_date__year=end_date.year,
                                     league=s.league).exists():
                skipped += 1
            else:
                old_teams = s.teams.all()

                # Create a copy
                s.pk = None
                s.start_date = start_date
                s.end_date = end_date
                s.save()
                s.teams.set(old_teams)
                copied += 1

        total = seasons.count()
        status = 'SUCCESS' if copied + skipped == total else 'FAILURE'
        msg = '[{}] Total: {} Copied: {} Skipped: {} {}'.format(datetime.datetime.now(), total, copied, skipped, status)
        self.stdout.write(msg)
