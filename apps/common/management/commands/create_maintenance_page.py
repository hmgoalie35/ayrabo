import os

from django.core.management import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Creates the maintenance page'

    def add_arguments(self, parser):
        parser.add_argument('--dir', required=True, help='Directory where the maintenance file should be written.')
        parser.add_argument('--file', default='maintenance.html', help='Name of the maintenance file.')

    def handle(self, *args, **options):
        directory = options.get('dir')
        maintenance_file = options.get('file')
        if '.' in directory:
            self.stdout.write('The directory specified must be a path.')
            exit(1)
        if not maintenance_file.endswith('.html'):
            self.stdout.write('The maintenance file must be an html file.')
            exit(1)

        if not os.path.exists(directory):
            os.mkdir(directory)

        template = render_to_string('common/maintenance.html').strip()
        with open(os.path.join(directory, maintenance_file), 'w') as f:
            f.write(template)
