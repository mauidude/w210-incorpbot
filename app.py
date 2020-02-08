import logging
import os
import pickle
import random
import time

import elasticsearch
import numpy as np
from flask import Flask
from flask_socketio import SocketIO, emit
from sentence_transformers import SentenceTransformer

from src import ir
from src.models import intent, qa

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


configs = {
    'ELASTIC_HOST': None,
    'ELASTIC_PORT': '9200',
    'ELASTIC_TIMEOUT': '300',
    'SENT_MODEL_NAME': 'bert-base-nli-stsb-mean-tokens',
    'MODEL_TYPE': 'bert',
    'MODEL_NAME_OR_PATH': 'https://storage.googleapis.com/w210-incorpbot/models/squad-1.0/',
    'ELASTIC_INDEX': 'documents',
    'MAX_SEQ_LENGTH': 384,
    'DOC_STRIDE': 128,
    'MAX_QUERY_LENGTH': 64,
    'MODEL_TYPE': 'bert',
    'DO_LOWER_CASE': True,
    'N_BEST_SIZE': 20,
    'MAX_ANSWER_LENGTH': 30,
    'VERBOSE_LOGGING': True,
    'INTENT_MODEL': 'https://storage.googleapis.com/w210-incorpbot/models/intent/intent_model.pkl',
    'WORD_EMBEDDING_MODEL': 'glove/medium/glove.6B.100d.magnitude'
}

for cfg, default in configs.items():
    val = os.environ.get(cfg, default)
    configs[cfg] = val
    if val is None:
        raise Exception(f'missing environment variable {cfg}')


# intent mdoel for classifying user's intent so we properly respond to their input
intent_model = intent.Model(
    configs['INTENT_MODEL'], configs['WORD_EMBEDDING_MODEL'])

nodes = [f"{configs['ELASTIC_HOST']}:{configs['ELASTIC_PORT']}"]
es = elasticsearch.Elasticsearch(
    nodes, timeout=int(configs['ELASTIC_TIMEOUT']))

# sentence model for getting sentence embeddings during retrieval
sent_model = SentenceTransformer(configs['SENT_MODEL_NAME'])

# retriever for fetching relevant documents from elastic search
retriever = ir.Retriever(es, sent_model, configs['ELASTIC_INDEX'])

# qa model for finding best answer for a question in a context paragraph
qa_model = qa.Model(configs['MODEL_NAME_OR_PATH'],
                    model_type=configs['MODEL_TYPE'],
                    do_lower_case=bool(configs['DO_LOWER_CASE']),
                    max_seq_length=int(configs['MAX_SEQ_LENGTH']),
                    doc_stride=int(configs['DOC_STRIDE']),
                    max_query_length=int(configs['MAX_QUERY_LENGTH']),
                    )


def handle_greeting(text):
    return np.random.choice([
        'Hello!',
        'Howdy! Welcome to Incorpbot!',
        'Welcome! What can I help you with?'
    ])


def handle_help(text):
    return np.random.choice([
        'Ask me a question about your legal needs!',
    ])


def handle_other(text):
    return np.random.choice([
        "Hmmm... I don't think I can help you with that.",
        'I am not sure I understand.'
    ])


def handle_question(text):
    context = retriever.retrieve(text)

    return qa_model.find_answer(text,
                                context,
                                n_best_size=int(configs['N_BEST_SIZE']),
                                max_answer_length=int(configs['MAX_ANSWER_LENGTH']))


def handle_sendoff(text):
    return np.random.choice([
        'Thanks for visiting!',
        'Bye!',
        'Come back soon!'
    ])


def handle_thanks(text):
    return np.random.choice([
        'Glad to be of service!',
        'Thank you for letting me help!'
    ])


intent_responses = [
    handle_greeting,
    handle_help,
    handle_other,
    handle_question,
    handle_sendoff,
    handle_thanks
]


@socketio.on('conversation:new')
def conversation_new():
    emit('conversation:response', {
         'message': 'Welcome to Incorpbot! Begin by asking me a question.'})


@socketio.on('conversation:message')
def conversation_mesage(payload):
    msg = payload['message']
    intent = intent_model.classify(msg)
    response = intent_responses[intent](msg)

    emit('conversation:response', {'message': response})


if __name__ == '__main__':
    socketio.run(app)
