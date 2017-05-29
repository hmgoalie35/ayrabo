#!/usr/bin/python3

import argparse
import os

BASE_COMMAND = 'ansible-playbook -i {inventory} {playbook}'
VAULT_PASSWORD_FILE = os.path.expanduser('~/ansible-vault.txt')


def get_parser():
    parser = argparse.ArgumentParser(description='Wrapper around using ansible-playbook on the command line')
    parser.add_argument()
    return parser


def main():
    """
    A wrapper around using ansible-playbook [options] on the command line all of the time.

    TODO:
        1. Maintenance mode
        2. Deploying arbitrary branches (collect static, migrate, etc.) to arbitrary servers
        3. Rollback
        4. DB backups/restores
        5. Applying new nginx conf (Just need to run web role...)
    """
    parser = get_parser()

    sudo_required = False
    vault_required = False
    env = None
    inventory_file = 'devops/ansible/{env}/{env}'.format(env=env)
    playbook = 'devops/ansible/{env}/{env}'.format(env=env)
    command = BASE_COMMAND.format(inventory=inventory_file, playbook=playbook)
    if sudo_required:
        command += ' -K'
    if vault_required:
        command += ' --vault-password-file={}'.format(VAULT_PASSWORD_FILE)

    print(parser, command)


if __name__ == '__main__':
    main()
