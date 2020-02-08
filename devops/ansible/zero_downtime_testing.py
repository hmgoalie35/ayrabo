#!/usr/bin/python3.6
import argparse
import time
from datetime import datetime
from urllib.parse import urljoin

import requests
from requests import RequestException


DEV = 'dev'
QA = 'qa'
STAGE = 'stage'
PROD = 'prod'

ENVS = [DEV, QA, STAGE, PROD]


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('env', choices=ENVS)
    return parser


def print_msg(level, msg):
    print(f'[{datetime.now()}] {level}: {msg}')


def handle_downtime(downtime_start, msg):
    print_msg('ERROR', msg)
    if not downtime_start:
        downtime_start = datetime.now()
    return downtime_start


def main():
    parser = get_parser()
    args = vars(parser.parse_args())
    env = args.get('env')
    base_urls = {
        DEV: 'http://localhost:8000',
        QA: 'https://192.168.1.210',
        STAGE: None,
        PROD: None,
    }
    base_url = base_urls.get(env)
    if not base_url:
        print(f'{env} not configured')
        exit(1)

    url = urljoin(base_url, 'health-check/')
    downtime_start = None
    downtime_end = None
    session = requests.Session()
    while True:
        time.sleep(0.5)

        try:
            response = session.get(url, verify=False)
        except RequestException as e:
            downtime_start = handle_downtime(downtime_start, str(e))
            continue

        status_code = response.status_code
        if response.ok:
            print_msg('SUCCESS', status_code)
            if downtime_start:
                downtime_end = datetime.now()
                break
        else:
            downtime_start = handle_downtime(downtime_start, f'{status_code} {response.reason}')

    if downtime_start and downtime_end:
        print(f'Downtime start: {downtime_start}')
        print(f'Downtime end: {downtime_end}')
        print(f'Total downtime: {downtime_end - downtime_start}')


if __name__ == '__main__':
    main()
