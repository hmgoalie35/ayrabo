#!/usr/bin/python3.6
import argparse
import time
from datetime import datetime
from urllib.parse import urljoin

import requests


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('env', choices=('dev', 'qa', 'staging', 'prod'))
    return parser


def print_msg(msg):
    print('[{}] {}'.format(datetime.now(), msg))


def main():
    parser = get_parser()
    args = vars(parser.parse_args())
    env = args.get('env')
    base_urls = {
        'dev': 'http://localhost:8000',
        'qa': 'https://192.168.1.188',
        'staging': None,
        'prod': None
    }
    base_url = base_urls.get(env)
    if not base_url:
        print('{} not configured'.format(env))
        exit(1)
    url = urljoin(base_url, 'health-check')
    downtime_start = None
    downtime_end = None
    session = requests.Session()
    while True:
        response = session.get(url, verify=False)
        status_code = response.status_code
        if response.ok:
            print_msg('SUCCESS')
            if downtime_start:
                downtime_end = datetime.now()
                break
            time.sleep(1)
        else:
            print_msg('ERROR {} {}'.format(status_code, response.reason))
            if not downtime_start:
                downtime_start = datetime.now()
    if downtime_start and downtime_end:
        print('Total downtime: {}'.format(downtime_end - downtime_start))
    print('Exiting...')


if __name__ == '__main__':
    main()
