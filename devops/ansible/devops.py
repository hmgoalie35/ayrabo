#!/usr/bin/python3

import argparse


def get_parser():
    parser = argparse.ArgumentParser()
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
    print(parser)


if __name__ == '__main__':
    main()
