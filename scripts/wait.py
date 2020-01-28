#!/usr/bin/env python3

import argparse
import json
import logging
import time

import elasticsearch
import numpy as np


def wait(es):
    while not es.ping():
        print('waiting for elasticsearch...')
        time.sleep(1)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Inserts a record into Elasticsearch')

    parser.add_argument('--host', type=str, required=True,
                        help='the Elasticsearch host')

    parser.add_argument('--port', type=int, default=9200,
                        help='the Elasticsearch port')

    parser.add_argument('--timeout', type=int, default=300,
                        help='the Elasticsearch timeout')

    args = parser.parse_args()

    nodes = [f'{args.host}:{args.port}']
    es = elasticsearch.Elasticsearch(nodes, timeout=args.timeout)

    wait(es)
