#!/usr/bin/env python3

import argparse
import json
import logging

import elasticsearch
import numpy as np
import pandas as pd
import tensorflow_hub as hub


def insert(es, index, model, df):
    for category, examples in df[~df.category.isin(['question', 'other'])].groupby('category'):
        centroid = np.mean(model(examples['input']).numpy(), axis=0)

        payload = {
            'category': category,
            'centroid': centroid.tolist(),
        }

        es.index(index=index, body=payload)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Inserts a classification record into Elasticsearch')

    parser.add_argument('--host', type=str, required=True,
                        help='the Elasticsearch host')

    parser.add_argument('--port', type=int, default=9200,
                        help='the Elasticsearch port')

    parser.add_argument('--index', type=str, required=True,
                        help='the index name')

    parser.add_argument('--file', type=str, required=True,
                        help='the name of the CSV file')

    parser.add_argument('--timeout', type=int, default=300,
                        help='the Elasticsearch timeout')

    parser.add_argument('--model', type=str, required=True,
                        help='the model name to use for the sentence embeddings. See https://tfhub.dev/google/collections/universal-sentence-encoder/1')

    args = parser.parse_args()

    df = pd.read_csv(args.file)

    model = hub.load(args.model)

    nodes = [f'{args.host}:{args.port}']
    es = elasticsearch.Elasticsearch(nodes, timeout=args.timeout)

    insert(es, args.index,  model, df)
