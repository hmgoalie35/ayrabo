from django.core.management import BaseCommand
from django.template.loader import render_to_string


class Command(BaseCommand):
    help = 'Creates the maintenance page'

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='Name of the maintenance file.')

    def handle(self, *args, **options):
        maintenance_file = options.get('file')
        if not maintenance_file.endswith('.html'):
            self.stdout.write('The maintenance file must be an html file.')
            exit(1)

        template = render_to_string('common/maintenance.html').strip()
        with open(maintenance_file, 'w') as f:
            f.write(template)
