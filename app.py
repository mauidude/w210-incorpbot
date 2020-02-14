import logging
import os
import time

import elasticsearch
import numpy as np
import spacy
import tensorflow_hub as hub
from flask import Flask
from flask_socketio import SocketIO, emit

from src import ir
from src.models import intent, qa

logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


configs = {
    'ELASTIC_HOST': None,
    'ELASTIC_PORT': '9200',
    'ELASTIC_TIMEOUT': '300',
    'SENTENCE_EMBEDDING_MODEL': None,
    'SPACY_MODEL': None,
    'MODEL_TYPE': 'bert',
    'MODEL_NAME_OR_PATH': 'https://storage.googleapis.com/w210-incorpbot/models/squad-2.0/',
    'ELASTIC_INDEX': 'documents',
    'ELASTIC_INTENT_INDEX': 'classes',
    'MAX_SEQ_LENGTH': 384,
    'DOC_STRIDE': 128,
    'MAX_QUERY_LENGTH': 64,
    'MODEL_TYPE': 'bert',
    'DO_LOWER_CASE': True,
    'N_BEST_SIZE': 20,
    'MAX_ANSWER_LENGTH': 30,
    'VERBOSE_LOGGING': True,
    'NULL_SCORE_DIFF_THRESHOLD': 0,
    'VERSION_2_WITH_NEGATIVE': True,
    'INTENT_THRESHOLD': 0.4
}

app.logger.info('loading configs...')
for cfg, default in configs.items():
    val = os.environ.get(cfg, default)
    configs[cfg] = val
    if val is None:
        raise Exception(f'missing environment variable {cfg}')

app.logger.info('initializing elasticsearch client...')
nodes = [f"{configs['ELASTIC_HOST']}:{configs['ELASTIC_PORT']}"]
es = elasticsearch.Elasticsearch(
    nodes, timeout=int(configs['ELASTIC_TIMEOUT']))

app.logger.info('loading sentence embedding model...')
sent_embedding_model = hub.load(configs['SENTENCE_EMBEDDING_MODEL'])

# retriever for fetching relevant documents from elastic search
app.logger.info('initializing retriever...')
retriever = ir.Retriever(es, sent_embedding_model, configs['ELASTIC_INDEX'])

# intent mdoel for classifying user's intent so we properly respond to their input
app.logger.info('initializing intent model...')
intent_model = intent.Model(
    sent_embedding_model, es, configs['ELASTIC_INTENT_INDEX'], float(configs['INTENT_THRESHOLD']))

# nlp utilities
nlp = spacy.load(configs['SPACY_MODEL'])

# qa model for finding best answer for a question in a context paragraph
app.logger.info('initializing QA model...')
qa_model = qa.Model(configs['MODEL_NAME_OR_PATH'],
                    nlp,
                    model_type=configs['MODEL_TYPE'],
                    do_lower_case=bool(configs['DO_LOWER_CASE']),
                    max_seq_length=int(configs['MAX_SEQ_LENGTH']),
                    doc_stride=int(configs['DOC_STRIDE']),
                    max_query_length=int(configs['MAX_QUERY_LENGTH']),
                    version_2_with_negative=bool(
                        configs['VERSION_2_WITH_NEGATIVE']),
                    null_score_diff_threshold=float(
                        configs['NULL_SCORE_DIFF_THRESHOLD']),
                    )

app.logger.info(configs)


def handle_greeting(text):
    return np.random.choice([
        'Hello!',
        'Howdy! Welcome to Incorpbot!',
        'Welcome! What can I help you with?'
    ])


def handle_help(text):
    return np.random.choice([
        'Ask me a question about your legal needs!',
        "I'm here to help you with your legal questions! Ask away!"
    ])


def handle_other(text):
    return np.random.choice([
        "Hmmm... I don't think I can help you with that.",
        'I am not sure I understand.'
    ])


def handle_question(text):
    context = retriever.retrieve(text)

    answer = qa_model.find_answer(text,
                                  context,
                                  full_sentence=True,
                                  n_best_size=int(configs['N_BEST_SIZE']),
                                  max_answer_length=int(configs['MAX_ANSWER_LENGTH']))

    if not answer:
        return handle_other(text)

    return answer


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


intent_responses = {
    'greeting': handle_greeting,
    'help': handle_help,
    'question': handle_question,
    'sendoff': handle_sendoff,
    'thanks': handle_thanks
}


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
