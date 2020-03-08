#!/usr/bin/env python3

import argparse
import glob
import json
import logging

import spacy
import tensorflow_hub as hub

from ..elastic import get_client
from ..models.embedding import Model


def insert(es, index, model, nlp, data):
    state = data['state']

    for page in data['pages']:
        source = page['source']

        for paragraph in page['paragraphs']:
            doc = nlp(paragraph)

            for sentence in doc.sents:
                embeddings = model.embedding(sentence.text)

                payload = {
                    'text': paragraph,
                    'state': state,
                    'source': source,
                    'universal_sentence_embeddings': embeddings.tolist()
                }

                es.index(index=index, body=payload)


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

    parser.add_argument('--model', type=str, required=True,
                        help='the model name to use for the sentence embeddings. See https://tfhub.dev/google/collections/universal-sentence-encoder/1')

    parser.add_argument('--spacy_model', type=str, required=True)

    args = parser.parse_args()

    model = Model(hub.load(args.model))
    nlp = spacy.load(args.spacy_model)

    es = get_client(args.host, args.port, timeout=args.timeout)

    for filename in glob.glob(args.file):
        logging.info(f'importing {filename}')

        with open(filename) as f:
            index_cfg = json.load(f)
            insert(es, args.index,  model, nlp, index_cfg)
