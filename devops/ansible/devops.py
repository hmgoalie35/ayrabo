#!/usr/bin/python3

import argparse
import datetime
import os
import subprocess

BASE_COMMAND = ['ansible-playbook']
VAULT_PASSWORD_FILE = os.path.expanduser('~/ansible-vault.txt')
SERVER_TYPES = ['dev', 'qa', 'staging', 'prod']
MODES = ['deploy', 'maintenance', 'provision', 'rollback', 'db_backup', 'db_restore', 'dev']
ANSIBLE_ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
HOSTS_DIR = os.path.join(ANSIBLE_ROOT_DIR, 'hosts')


class Devops(object):
    """
    A wrapper around using ansible-playbook [options] on the command line all of the time.
    """

    def __init__(self):
        self.args = {}
        self.playbook = None
        self.inventory_file = None
        self.deployment_version = None
        self.server_type = None
        self.mode = None
        self.tags = None
        self.verbosity = None

    def get_parser(self):
        parser = argparse.ArgumentParser(description='Wrapper around using ansible-playbook on the command line')
        parser.add_argument('-m', '--mode', required=True, choices=MODES, help='What would you like to do?')
        parser.add_argument('-s', '--server', required=True, choices=SERVER_TYPES,
                            help='The type of server to work with')
        parser.add_argument('-d', '--deployment_version', default='master',
                            help='Branch name, SHA hash, release version')
        parser.add_argument('-t', '--tags', help='Only run plays tagged with these values')
        parser.add_argument('-v', '--verbosity', action='count', help='Specify verbosity for ansible-playbook')
        return parser

    def _build_command(self):
        command = BASE_COMMAND
        command.append(self.playbook)
        command.append('-i')
        command.append(self.inventory_file)

        if self.mode == 'dev':
            if self.tags == 'install_dependencies':
                command.append('-K')
            if self.tags:
                command.append('-t')
                command.append(self.tags)
        if self.mode in ['provision', 'deploy']:
            command.append('-K')
            command.append('--vault-password-file')
            command.append(VAULT_PASSWORD_FILE)
            command.append('--extra-vars')
            command.append('deployment_version={}'.format(self.deployment_version))
            command.append('--extra-vars')
            command.append('server_type={}'.format(self.server_type))
        if self.verbosity:
            command.append('-{}'.format('v' * self.verbosity))
        return command

    def init(self):
        """
        TODO:
            1. Maintenance mode
            2. Deploying arbitrary branches (collect static, migrate, etc.) to arbitrary servers
            3. Rollback
            4. DB backups/restores
            5. Applying new nginx conf (Just need to run web role...)
            6. If deployment, enforce development version being specified, etc.
        """
        parser = self.get_parser()
        self.args = vars(parser.parse_args())
        self.server_type = self.args.get('server')
        self.deployment_version = self.args.get('deployment_version')
        self.mode = self.args.get('mode')
        self.tags = self.args.get('tags')
        self.verbosity = self.args.get('verbosity')
        self.inventory_file = os.path.join(HOSTS_DIR, self.server_type)
        self.playbook = os.path.join(ANSIBLE_ROOT_DIR, '{}.yml'.format(self.mode))

        command = self._build_command()

        print('Running "{}"\n'.format(' '.join(command)))
        start_time = datetime.datetime.now()
        result = subprocess.run(command)
        end_time = datetime.datetime.now()
        print('Return Code: {}'.format(result.returncode))
        print('Stdout: {}'.format(result.stdout))
        print('-' * 15)
        print('Stderr: {}'.format(result.stderr))

        time_difference = end_time - start_time
        print('\nTook: {}'.format(time_difference))


if __name__ == '__main__':
    Devops().init()
