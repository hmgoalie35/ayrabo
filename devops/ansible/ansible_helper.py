#!/usr/bin/python

import argparse
import os


def valid_input(prompt):
    input_value = None
    while input_value is None or input_value == '':
        input_value = input(prompt + ": ").strip()
    return input_value


def create_dir(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)


def create_file(file_path):
    open(file_path, 'w').close()


def create_role(role_path):
    create_dir(role_path)

    dirs_to_create = ['tasks', 'handlers', 'templates', 'files', 'vars', 'defaults', 'meta']

    for directory in dirs_to_create:
        dir_path = os.path.join(role_path, directory)
        create_dir(dir_path)

        if directory == 'templates':
            create_file(os.path.join(dir_path, 'default_template.j2'))
        elif directory == 'files':
            pass
        else:
            create_file(os.path.join(dir_path, 'main.yml'))


# TODO add in default files in group_vars for each new role (end in .yml)
def main():
    parser = argparse.ArgumentParser(description="Autogenerate directory structure for ansible")
    parser.add_argument('mode', choices=['startproject', 'startrole'],
                        help="Create a new ansible playbook, or just add a new role to an existing playbook")
    parser.add_argument('--dir', '-d', required=True, help="The directory that will contain the ansible files/folders")
    parser.add_argument('--name', '-n', required=False, help="The name of the role to create")
    args = vars(parser.parse_args())

    root_dir = args['dir']
    role_name = args['name']

    root_dir = os.path.abspath(os.path.expanduser(root_dir))
    roles_dir = os.path.join(root_dir, 'roles')

    if args['mode'] == 'startrole':
        if role_name is None:
            print("Role name must be specified when running startrole")
            exit(1)
        elif not os.path.exists(roles_dir):
            print("You need to already have run startproject before creating roles")
            exit(1)

    create_dir(root_dir)

    if args['mode'] == 'startproject':
        dirs_to_create = ['group_vars', 'host_vars']

        for directory in dirs_to_create:
            print("Add in files named after your {} accordingly".format(
                'groups' if directory == 'group_vars' else 'hosts'))

            create_dir(os.path.join(root_dir, directory))

        print("Creating master playbook file: site.yml")
        create_file(os.path.join(root_dir, 'site.yml'))

        print("Creating hosts file")
        create_file(os.path.join(root_dir, 'hosts'))

        create_dir(roles_dir)

    role_path = os.path.join(roles_dir, role_name)

    print("Creating role: %s" % role_name)
    create_role(role_path)

    print("Done")


if __name__ == '__main__':
    main()
