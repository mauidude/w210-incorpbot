import logging
import os
import time

import elasticsearch
import torch
from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from sentence_transformers import SentenceTransformer

from scripts.query import MODEL_CLASSES, query

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
    'VERBOSE_LOGGING': True
}

for cfg, default in configs.items():
    val = os.environ.get(cfg, default)
    configs[cfg] = val
    if val is None:
        raise Exception(f'missing environment variable {cfg}')


nodes = [f"{configs['ELASTIC_HOST']}:{configs['ELASTIC_PORT']}"]
es = elasticsearch.Elasticsearch(
    nodes, timeout=int(configs['ELASTIC_TIMEOUT']))

sent_model = SentenceTransformer(configs['SENT_MODEL_NAME'])

config_class, model_class, tokenizer_class = MODEL_CLASSES[configs['MODEL_TYPE']]

model_name_or_path = configs['MODEL_NAME_OR_PATH']
config = config_class.from_pretrained(
    model_name_or_path,
    cache_dir=None
)

tokenizer = tokenizer_class.from_pretrained(
    model_name_or_path,
    do_lower_case=bool(configs['DO_LOWER_CASE']),
    cache_dir=None,
)

model = model_class.from_pretrained(
    model_name_or_path,
    from_tf=bool(".ckpt" in model_name_or_path),
    config=config,
    cache_dir=None,
)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


@socketio.on('conversation:new')
def conversation_new():
    emit('conversation:response', {
         'message': 'Welcome to Incorpbot! Begin by asking me a question.'})


@socketio.on('conversation:message')
def conversation_mesage(payload):
    answer = query(payload['message'],
                   es,
                   configs['ELASTIC_INDEX'],
                   sent_model,
                   config,
                   tokenizer,
                   model,
                   int(configs['MAX_SEQ_LENGTH']),
                   int(configs['DOC_STRIDE']),
                   int(configs['MAX_QUERY_LENGTH']),
                   configs['MODEL_TYPE'],
                   bool(configs['DO_LOWER_CASE']),
                   int(configs['N_BEST_SIZE']),
                   int(configs['MAX_ANSWER_LENGTH']),
                   device,
                   bool(configs['VERBOSE_LOGGING'])
                   )

    emit('conversation:response', {'message': answer})


if __name__ == '__main__':
    socketio.run(app)
