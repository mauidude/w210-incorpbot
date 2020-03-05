#!/usr/bin/env python3

import argparse
import logging

import elasticsearch
import spacy
import tensorflow_hub as hub

from ..elastic import get_client
from ..ir import Retriever
from ..models.qa import MODEL_CLASSES, Model


def cli(retriever, model, args):
    while True:
        user_input = input('Enter your query:\n')
        context = retriever.retrieve(user_input)
        answer = qa_model.find_answer(user_input,
                                      context,
                                      n_best_size=args.n_best_size,
                                      max_answer_length=args.max_answer_length)

        print('Answer: ', answer)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description='Queries Elasticsearch')

    parser.add_argument('--host', type=str, required=True,
                        help='the Elasticsearch host')

    parser.add_argument('--port', type=int, default=9200,
                        help='the Elasticsearch port')

    parser.add_argument('--index', type=str, required=True,
                        help='the index name')

    parser.add_argument('--timeout', type=int, default=300,
                        help='the Elasticsearch timeout')

    parser.add_argument('--model_type', type=str, default='bert',
                        help='Model type selected in the list: ' +
                        ', '.join(MODEL_CLASSES.keys()),
                        )

    parser.add_argument('--spacy_model', type=str, required=True,
                        help='the spacy model to use')

    parser.add_argument('--sentence_embedding_model', type=str, required=True,
                        help='sentence embedding model to use')

    parser.add_argument('--model_name_or_path', type=str, default='https://storage.googleapis.com/w210-incorpbot/models/squad-2.0/',
                        help='the path to the Q&A model')

    parser.add_argument('--cache_dir', default='', type=str,
                        help='where to store the pretrained model after downloading')

    parser.add_argument('--version_2_with_negative', action='store_true',
                        help='If true, the SQuAD examples contain some that do not have an answer.')

    parser.add_argument('--null_score_diff_threshold', type=float, default=0.0,
                        help="If null_score - best_non_null is greater than the threshold predict null.")

    parser.add_argument(
        "--max_seq_length",
        default=384,
        type=int,
        help="The maximum total input sequence length after WordPiece tokenization. Sequences "
        "longer than this will be truncated, and sequences shorter than this will be padded.",
    )
    parser.add_argument(
        "--doc_stride",
        default=128,
        type=int,
        help="When splitting up a long document into chunks, how much stride to take between chunks.",
    )
    parser.add_argument(
        "--max_query_length",
        default=64,
        type=int,
        help="The maximum number of tokens for the question. Questions longer than this will "
        "be truncated to this length.",
    )
    parser.add_argument(
        "--do_lower_case", action="store_true", help="Set this flag if you are using an uncased model."
    )
    parser.add_argument(
        "--n_best_size",
        default=20,
        type=int,
    )
    parser.add_argument(
        "--max_answer_length",
        default=30,
        type=int,
        help="The maximum length of an answer that can be generated. This is needed because the start "
        "and end predictions are not conditioned on one another.",
    )
    parser.add_argument(
        "--verbose_logging",
        action='store_true',
        help="Logs retrieved results from Elasticsearch",
    )

    args = parser.parse_args()

    es = get_client(args.host, args.port, timeout=args.timeout)

    sent_embedding_model = hub.load(args.sentence_embedding_model)

    # retriever for fetching relevant documents from elastic search
    retriever = Retriever(es, sent_embedding_model, args.index)

    nlp = spacy.load(args.spacy_model)

    # qa model for finding best answer for a question in a context paragraph
    qa_model = Model(args.model_name_or_path,
                     nlp,
                     model_type=args.model_type,
                     do_lower_case=args.do_lower_case,
                     max_seq_length=args.max_seq_length,
                     doc_stride=args.doc_stride,
                     max_query_length=args.max_query_length,
                     null_score_diff_threshold=args.null_score_diff_threshold,
                     version_2_with_negative=args.version_2_with_negative,
                     )

    cli(retriever, qa_model, args)
