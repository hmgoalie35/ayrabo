import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Creates the tests directory structure for a given app'

    @staticmethod
    def remove_file(file_path):
        try:
            os.remove(file_path)
        except FileNotFoundError:
            pass

    @staticmethod
    def create_file(file_path, default_content=None):
        with open(file_path, 'w') as my_file:
            if default_content is not None:
                my_file.write(default_content)

    @staticmethod
    def create_module(file_path):
        try:
            os.mkdir(file_path)
            # create __init__.py to make the directory a python module
            init_file_path = os.path.join(file_path, '__init__.py')
            open(init_file_path, 'w').close()
        except FileExistsError:
            pass

    def add_arguments(self, parser):
        parser.add_argument('app')

    def handle(self, *args, **options):
        app = options['app']
        app_path = os.path.join(settings.BASE_DIR, 'apps', app)
        if not os.path.exists(app_path):
            raise CommandError('{app_path} is not a valid app or the path does not exist'.format(app_path=app_path))

        # Delete the default tests.py file django creates
        test_file_path = os.path.join(app_path, 'tests.py')
        self.remove_file(test_file_path)

        # Create tests module
        tests_module_path = os.path.join(app_path, 'tests')
        self.create_module(tests_module_path)

        # Create test_models file
        test_models_file_path = os.path.join(tests_module_path, 'test_models.py')
        self.create_file(test_models_file_path, 'from django.test import TestCase\n')

        # Create test_views file
        test_views_file_path = os.path.join(tests_module_path, 'test_views.py')
        self.create_file(test_views_file_path, 'from django.test import TestCase\n')

        # Create factories module
        factories_module_path = os.path.join(tests_module_path, 'factories')
        self.create_module(factories_module_path)
