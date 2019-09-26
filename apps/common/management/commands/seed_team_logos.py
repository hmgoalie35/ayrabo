from pathlib import Path

from django.core.files import File
from django.core.management.base import BaseCommand, CommandError

from teams.models import Team


class Command(BaseCommand):
    help = 'Seed team logos'

    def add_arguments(self, parser):
        parser.add_argument('path', help='Full path to a folder containing team logos')

    def _get_file_path(self, team, files):
        for f in files:
            if team.slug.startswith(f.stem):
                return f
        return None

    def handle(self, *args, **options):
        path = Path(options.get('path')).expanduser()

        if not path.exists():
            raise CommandError(f'{path.absolute()} does not exist')

        files = list(path.iterdir())
        teams = Team.objects.all()
        count = 0
        for team in teams:
            file_path = self._get_file_path(team, files)
            if file_path and not team.logo:
                self.stdout.write(f'Seeding {team.name} with {file_path.name}')
                with file_path.open('rb') as f:
                    # The original file is stored in the logo field. A receiver from easy_thumbnails catches when this
                    # field is updated and generates thumbnails. We can alternatively do team.logo.get_thumbnail(...)
                    # after saving the team (if we disable the receiver).
                    team.logo = File(f)
                    team.save()
                    count += 1
        self.stdout.write(f'Seeded {count} out of {teams.count()} logos')
