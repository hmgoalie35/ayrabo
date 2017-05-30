#!/usr/bin/python3

import argparse
import os
import subprocess

BASE_COMMAND = ['ansible-playbook']
VAULT_PASSWORD_FILE = os.path.expanduser('~/ansible-vault.txt')
SERVER_TYPES = ['qa', 'staging', 'prod']
MODES = ['deploy', 'maintenance', 'provision', 'rollback', 'db_backup', 'db_restore']


class Devops(object):
    """
    A wrapper around using ansible-playbook [options] on the command line all of the time.
    """

    def __init__(self):
        self.args = {}
        self.sudo_required = False
        self.vault_required = False

    def get_parser(self):
        parser = argparse.ArgumentParser(description='Wrapper around using ansible-playbook on the command line')
        parser.add_argument('mode', choices=MODES, help='What would you like to do?')
        parser.add_argument('server_type', choices=SERVER_TYPES, help='The type of server to work with')
        parser.add_argument('-d', '--deployment_version', help='Branch name, SHA hash, release version')
        return parser

    def init(self):
        """
        TODO:
            1. Maintenance mode
            2. Deploying arbitrary branches (collect static, migrate, etc.) to arbitrary servers
            3. Rollback
            4. DB backups/restores
            5. Applying new nginx conf (Just need to run web role...)
        """
        parser = self.get_parser()
        self.args = vars(parser.parse_args())
        server_type = self.args.get('server_type')
        deployment_version = self.args.get('deployment_version')
        mode = self.args.get('mode')
        inventory_file = 'hosts/{}'.format(server_type)
        playbook = '{}.yml'.format(mode)

        if mode in ['provision', 'deploy']:
            self.sudo_required = True
        if mode in ['provision', 'deploy']:
            self.vault_required = True

        command = BASE_COMMAND
        command.append(playbook)
        command.append('-i')
        command.append(inventory_file)
        if self.sudo_required:
            command.append('-K')
        if self.vault_required:
            command.append('--vault-password-file')
            command.append(VAULT_PASSWORD_FILE)

        command.append('--extra-vars')
        command.append('deployment_version={}'.format(deployment_version))
        command.append('--extra-vars')
        command.append('server_type={}'.format(server_type))

        print('Running {}...\n\n'.format(' '.join(command)))
        result = subprocess.run(command)
        print('Return Code: {}'.format(result.returncode))
        print('Stdout: {}'.format(result.stdout))
        print('-' * 15)
        print('Stderr: {}'.format(result.stderr))


if __name__ == '__main__':
    Devops().init()
