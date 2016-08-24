import fileinput
import os
import re
import shutil

from django.core.management.base import BaseCommand, CommandError
from rest_framework.settings import api_settings


def check_user_input(new_version):
    if new_version == '' or new_version is None:
        raise CommandError('Invalid version %s' % new_version)
    if 'v' not in new_version:
        new_version = 'v' + new_version
    if new_version in api_settings.ALLOWED_VERSIONS:
        raise CommandError(
                '%s already exists and overwriting it is probably not a good idea. Choose another version not in %s' % (
                    new_version, api_settings.ALLOWED_VERSIONS))
    return new_version


class Command(BaseCommand):
    help = 'Generate a new api version from scratch or based off of an existing version'
    requires_system_checks = True

    def add_arguments(self, parser):
        parser.add_argument('new_version', help='The new api version to generate')
        parser.add_argument('--base_version', default=api_settings.DEFAULT_VERSION,
                            choices=api_settings.ALLOWED_VERSIONS,
                            help='The api version to base the new api version off of')

    def handle(self, *args, **options):
        new_version = options['new_version'].strip()
        new_version = check_user_input(new_version)
        base_version = options['base_version'].strip()

        api_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        new_version_path = os.path.join(api_path, new_version)
        base_version_path = os.path.join(api_path, base_version)

        if not os.path.exists(base_version_path):
            raise CommandError('Base version path %s does not exist' % base_version_path)
        if os.path.exists(new_version_path):
            raise CommandError('New version path %s already exists' % new_version_path)

        shutil.copytree(base_version_path, new_version_path)

        for root, directories, filenames in os.walk(new_version_path):
            for directory in directories:
                if base_version in directory:
                    os.rename(os.path.join(root, directory), os.path.join(root, new_version))

            for file in filenames:
                # Examine file contents
                with fileinput.FileInput(os.path.join(root, file), inplace=True) as the_file:
                    try:
                        for line in the_file:
                            upper_result = re.subn(base_version.upper(), new_version.upper(), line)
                            lower_result = re.subn(base_version.lower(), new_version.lower(), line)
                            if upper_result[1] > 0:
                                print(upper_result[0], end='')
                            else:
                                print(lower_result[0], end='')
                    except UnicodeDecodeError:
                        pass

                # Examine file name
                if base_version in file:
                    extension = str(file.split('.')[1])
                    os.rename(os.path.join(root, file), os.path.join(root, new_version + '.' + extension))
