#!/usr/bin/env python3

import argparse
import json
import logging

import elasticsearch

import numpy as np
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer


def insert(es, index, model, data):
    state = data['state']

    for page in data['pages']:
        source = page['source']

        for paragraph in page['paragraphs']:
            sentences = sent_tokenize(paragraph)
            embeddings = model.encode(sentences)

            # convert to numpy array
            embeddings = np.array(embeddings)

            max_embeddings = np.max(embeddings, axis=0)
            avg_embeddings = np.mean(embeddings, axis=0)

            data = {
                'text': paragraph,
                'state': state,
                'source': source,
                'avg_embeddings': avg_embeddings.tolist(),
                'max_embeddings': max_embeddings.tolist(),
            }

            es.index(index=index, body=data)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Inserts a record into Elasticsearch')

    parser.add_argument('--host', type=str, required=True,
                        help='the Elasticsearch host')

    parser.add_argument('--port', type=int, default=9200,
                        help='the Elasticsearch port')

    parser.add_argument('--index', type=str, required=True,
                        help='the index name')

    parser.add_argument('--file', type=str, required=True,
                        help='the name of the JSON file')

    parser.add_argument('--timeout', type=int, default=300,
                        help='the Elasticsearch timeout')

    parser.add_argument('--model', type=str, default='bert-base-nli-stsb-mean-tokens',
                        help='the model name to use for the sentence embeddings. See https://github.com/UKPLab/sentence-transformers#english-pre-trained-models')

    args = parser.parse_args()

    with open(args.file) as f:
        index_cfg = json.load(f)

    nodes = [f'{args.host}:{args.port}']
    es = elasticsearch.Elasticsearch(nodes, timeout=args.timeout)

    model = SentenceTransformer(args.model)

    insert(es, args.index,  model, index_cfg)
