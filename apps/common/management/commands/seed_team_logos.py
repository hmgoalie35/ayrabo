import os

from django.core.files import File
from django.core.management import BaseCommand

from teams.models import Team


class Command(BaseCommand):
    help = 'Seed team logos'

    def add_arguments(self, parser):
        parser.add_argument('path', help='Full path to a folder containing team logos.')

    def _get_file_name(self, team, files):
        for _file in files:
            file_name = os.path.splitext(_file)[0]
            if team.slug.startswith(file_name):
                return _file
        return None

    def handle(self, *args, **options):
        path = os.path.expanduser(options.get('path'))

        if not os.path.exists(path):
            self.stdout.write('{} does not exist'.format(path))
            exit(1)

        files = os.listdir(path)
        teams = Team.objects.all()
        count = 0
        for team in teams:
            file_name = self._get_file_name(team, files)
            if file_name and not team.logo:
                full_path = os.path.join(path, file_name)
                self.stdout.write('Seeding {} with {}'.format(team.name, full_path))
                with open(full_path, 'rb') as f:
                    # The original file is stored in the logo field. A receiver from easy_thumbnails catches when this
                    # field is updated and generates thumbnails. We can alternatively do team.logo.get_thumbnail(...)
                    # after saving the team (if we disable the receiver).
                    team.logo = File(f)
                    team.save()
                    count += 1
        self.stdout.write('Seeded {} out of {} logos'.format(count, teams.count()))
