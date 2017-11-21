#!/usr/bin/python3.6

import time

import requests

SITE_URL = 'https://192.168.1.88/'


def print_msg(msg):
    print()
    print('#' * 10)
    print(msg)
    print('#' * 10)
    print()


def main():
    while True:
        resp = requests.get(SITE_URL, verify=False)
        if resp.ok:
            print_msg('SUCCESS')
            time.sleep(3)
        else:
            print_msg('ERROR: {} {}'.format(resp.status_code, resp.reason))
            break
    print('Exiting...')


if __name__ == '__main__':
    main()
