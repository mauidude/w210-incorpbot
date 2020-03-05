#!/usr/bin/env python3

import argparse
import json
import logging

from ..elastic import get_client


def create_index(es, name, cfg):
    es.indices.create(index=name, body=cfg, ignore=400)
    logging.info(f'index {name} created')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Create an index in ElasticSearch')

    parser.add_argument('--host', type=str, required=True,
                        help='the Elasticsearch host')

    parser.add_argument('--port', type=int, default=9200,
                        help='the Elasticsearch port')

    parser.add_argument('--name', type=str, required=True,
                        help='the index name')

    parser.add_argument('--file', type=str, required=True,
                        help='the name of the JSON index file')

    parser.add_argument('--timeout', type=int, default=300,
                        help='the Elasticsearch timeout')

    args = parser.parse_args()

    with open(args.file) as f:
        index_cfg = json.load(f)
    es = get_client(args.host, args.port, timeout=args.timeout)
    create_index(es, args.name,  index_cfg)
