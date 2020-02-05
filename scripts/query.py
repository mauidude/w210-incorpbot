#!/usr/bin/env python3

import argparse
import collections
import json
import logging
import math

import elasticsearch
import torch
from nltk.tokenize import sent_tokenize
from sentence_transformers import SentenceTransformer
from torch.utils.data import DataLoader, SequentialSampler
from transformers import (AlbertConfig, AlbertForQuestionAnswering,
                          AlbertTokenizer, BertConfig,
                          BertForQuestionAnswering, BertTokenizer,
                          DistilBertConfig, DistilBertForQuestionAnswering,
                          DistilBertTokenizer, XLMConfig,
                          XLMForQuestionAnswering, XLMTokenizer, XLNetConfig,
                          XLNetForQuestionAnswering, XLNetTokenizer,
                          squad_convert_examples_to_features)
from transformers.data.metrics.squad_metrics import (
    compute_predictions_logits, get_final_text)
from transformers.data.processors.squad import SquadExample, SquadResult

MODEL_CLASSES = {
    "bert": (BertConfig, BertForQuestionAnswering, BertTokenizer),
    # "roberta": (RobertaConfig, RobertaForQuestionAnswering, RobertaTokenizer),
    # "xlnet": (XLNetConfig, XLNetForQuestionAnswering, XLNetTokenizer),
    # "xlm": (XLMConfig, XLMForQuestionAnswering, XLMTokenizer),
    # "distilbert": (DistilBertConfig, DistilBertForQuestionAnswering, DistilBertTokenizer),
    "albert": (AlbertConfig, AlbertForQuestionAnswering, AlbertTokenizer),
}


def cli(*args, **kwargs):
    while True:
        user_input = input('Enter your query:\n')
        answer = query(user_input, *args, **kwargs)
        print('Answer: ', answer)


def query(q,
          es,
          index,
          sent_model,
          config,
          tokenizer,
          model,
          max_seq_length,
          doc_stride,
          max_query_length,
          model_type,
          do_lower_case,
          n_best_size,
          max_answer_length,
          device,
          verbose_logging):

    embeddings = sent_model.encode([q])

    query = {
        'from': 0,
        'size': 10,
        'query': {
            'script_score': {
                'query': {
                    'match_all': {}
                },
                'script': {
                    'source': "cosineSimilarity(params.query_vector, doc['max_embeddings']) + 1.0",
                    'params': {
                        'query_vector': embeddings[0].tolist()
                    }
                }
            }
        }
    }

    results = es.search(index=index, body=query)
    print(
        f"found {results['hits']['total']['value']} results in {results['took']} ms")

    for i, result in enumerate(results['hits']['hits']):
        document = result['_source']
        score = result['_score']

        if verbose_logging:
            print(f'Result {i} {score}:')
            print(document['text'])
            print('-' * 50)

    context = '\n'.join([
        result['_source']['text']
        for result in results['hits']['hits']
    ])

    example_id = '55555'
    example = SquadExample(example_id,
                           q,
                           context,
                           None,
                           None,
                           None,
                           )

    features, dataset = squad_convert_examples_to_features(
        [example], tokenizer, max_seq_length, doc_stride, max_query_length, False, return_dataset='pt')

    sampler = SequentialSampler(dataset)
    dataloader = DataLoader(dataset, sampler=sampler, batch_size=1)

    all_results = []
    for batch in dataloader:
        model.eval()
        batch = tuple(t.to(device) for t in batch)

        with torch.no_grad():
            inputs = {
                "input_ids": batch[0],
                "attention_mask": batch[1],
                "token_type_ids": batch[2],
            }

            example_index = batch[3]

            outputs = model(**inputs)
            outputs = [output.detach().cpu().tolist()
                       for output in outputs]
            start_logits, end_logits = outputs

            unique_id = int(features[example_index].unique_id)

            squad_result = SquadResult(
                unique_id, start_logits[0], end_logits[0])

            all_results.append(squad_result)

    predictions = compute_predictions_logits(
        [example],
        features,
        all_results,
        n_best_size,
        max_answer_length,
        do_lower_case,
        '/tmp/pred.out',
        '/tmp/nbest.out',
        '/tmp/null.out',
        True,
        False,
        0,
    )

    return predictions[example_id]


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

    parser.add_argument('--sent_model_name', type=str, default='bert-base-nli-stsb-mean-tokens',
                        help='the model name to use for the sentence embeddings. See https://github.com/UKPLab/sentence-transformers#english-pre-trained-models')

    parser.add_argument('--model_name_or_path', type=str, default='https://storage.googleapis.com/w210-incorpbot/models/squad-1.0/',
                        help='the path to the Q&A model')

    parser.add_argument('--cache_dir', default='', type=str,
                        help='where to store the pretrained model after downloading')

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
        help="The total number of n-best predictions to generate in the nbest_predictions.json output file.",
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

    nodes = [f'{args.host}:{args.port}']
    es = elasticsearch.Elasticsearch(nodes, timeout=args.timeout)

    sent_model = SentenceTransformer(args.sent_model_name)

    config_class, model_class, tokenizer_class = MODEL_CLASSES[args.model_type]
    config = config_class.from_pretrained(
        args.model_name_or_path,
        cache_dir=args.cache_dir if args.cache_dir else None,
    )
    tokenizer = tokenizer_class.from_pretrained(
        args.model_name_or_path,
        do_lower_case=args.do_lower_case,
        cache_dir=args.cache_dir if args.cache_dir else None,
    )
    model = model_class.from_pretrained(
        args.model_name_or_path,
        from_tf=bool(".ckpt" in args.model_name_or_path),
        config=config,
        cache_dir=args.cache_dir if args.cache_dir else None,
    )

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    cli(es,
        args.index,
        sent_model,
        config,
        tokenizer,
        model,
        args.max_seq_length,
        args.doc_stride,
        args.max_query_length,
        args.model_type,
        args.do_lower_case,
        args.n_best_size,
        args.max_answer_length,
        device,
        args.verbose_logging)
