import logging
import os
import time
import uuid

import elasticsearch
import numpy as np
import spacy
import tensorflow_hub as hub
from flask import Flask
from flask_socketio import SocketIO, emit
from redis import Redis

from src import geo, ir
from src.conversation import Manager
from src.elastic import get_client
from src.models import intent, qa

logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")


configs = {
    'ELASTIC_HOST': None,
    'ELASTIC_USER': '',
    'ELASTIC_PASSWORD': '',
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
    'INTENT_THRESHOLD': 0.4,
    'REDIS_HOST': None,
    'REDIS_PORT': 6379
}

app.logger.info('loading configs...')
for cfg, default in configs.items():
    val = os.environ.get(cfg, default)
    configs[cfg] = val
    if val is None:
        raise Exception(f'missing environment variable {cfg}')

if configs['ELASTIC_USER'] == '':
    configs['ELASTIC_USER'] = None
if configs['ELASTIC_PASSWORD'] == '':
    configs['ELASTIC_PASSWORD'] = None

app.logger.info('initializing redis client...')
redis = Redis(host=configs['REDIS_HOST'],
              port=int(configs['REDIS_PORT']), db=0)

app.logger.info('initializing conversation manager...')
conv_mgr = Manager(redis)

app.logger.info('initializing elasticsearch client...')
es = get_client(configs['ELASTIC_HOST'], configs['ELASTIC_PORT'],
                timeout=int(configs['ELASTIC_TIMEOUT']),
                username=configs['ELASTIC_USER'],
                password=configs['ELASTIC_PASSWORD'])

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

# geo resolver
geo_resolver = geo.Resolver(nlp)

app.logger.info(configs)


def supported_states():
    states = list(geo.states.values())
    states.sort()

    if len(states) == 1:
        states = states[0]
    else:
        states = ', '.join(states[0:-1])
        if len(states) > 1:
            states += f', and {states[-1]}'

    return states


def handle_greeting(cid, text):
    return np.random.choice([
        'Hello!',
        'Howdy! Welcome to Incorpbot!',
        'Welcome! What can I help you with?'
    ])


def handle_help(cid, text):
    response = [np.random.choice([
        'Ask me a question about your legal needs!',
        "I'm here to help you with your legal questions! Ask away!"
    ])]

    response.append(
        f'I can answer questions about the following states: {supported_states()}')

    return response


def handle_other(cid, text):
    return np.random.choice([
        "Hmmm... I don't think I can help you with that.",
        'I am not sure I understand.'
    ])


def handle_unsupported_state(state):
    return np.random.choice([
        f'Unfortunately, I cannot answer questions about {state} right now. I currently only have information on {supported_states()}.'
    ])


def handle_state_smalltalk(state):
    text = np.random.choice([
        f'I have never been to {state} but hope to one day! Now, let me find your answer...',
        f'I hear {state} is beautiful this time of year! One second, while I check on that...'
    ])

    emit('conversation:response', {'message': text})


def handle_question(cid, text):
    state = geo_resolver.resolve_state(text)
    us_state = None

    if state:
        app.logger.info(f'detected state: {state}')

        # tuple will be (XXX, True) if supported
        if state[1]:
            us_state = state[0]

            # if we had a pending question, use that as the input to the model
            prev = conv_mgr.get(cid, key='pending_question')
            if prev:
                text = prev
                conv_mgr.delete_key(cid, 'pending_question')

                handle_state_smalltalk(us_state)

        # unsupported state
        else:
            return handle_unsupported_state(state[0])

    # if US state was not mentioned in current input,
    # see if it's in the conversation state
    if not us_state:
        us_state = conv_mgr.get(cid, key='state')
        if not us_state:
            # mark current input as pending
            conv_mgr.update(cid, {'pending_question': text})

            return np.random.choice([
                'In order to best answer your question, can you please let me know which state you are in? ',
                'I would be happy to help you but first can you please tell me which state you are in? '
            ])

    else:
        # update conversation with their state
        conv_mgr.update(cid, {'state': us_state})

    app.logger.info(f'{cid} using state {us_state}')

    # retrieve docs
    context = retriever.retrieve(text, state=us_state)

    # pass context to model
    answer = qa_model.find_answer(text,
                                  context,
                                  full_sentence=True,
                                  n_best_size=int(configs['N_BEST_SIZE']),
                                  max_answer_length=int(configs['MAX_ANSWER_LENGTH']))

    if not answer:
        return handle_other(cid, text)

    return answer


def handle_sendoff(cid, text):
    return np.random.choice([
        'Thanks for visiting!',
        'Bye!',
        'Come back soon!'
    ])


def handle_thanks(cid, text):
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
    emit('conversation:welcome', {
         'message': 'Welcome to Incorpbot! Begin by asking me a question.',
         'conversation_id': str(uuid.uuid4()),
         })

    emit('conversation:response', {
        'message': '''
            Here you can find answers to topics like:
            <ul>
                <li>Incorporation</li>
                <li>Business Licenses</li>
                <li>Business Structures</li>
                <li>Intellectual Property</li>
                <li>Taxes</li>
                <li>And much more!</li>
            </ul>
            ''',
        'html': True
    })

    emit('conversation:response:end')


@socketio.on('conversation:message')
def conversation_message(payload):
    msg = payload['message']
    cid = payload['conversation_id']

    intent = intent_model.classify(msg)
    app.logger.info(f'{cid} sent "{msg}" - classified as {intent}')

    response = intent_responses[intent](cid, msg)
    if not isinstance(response, list):
        response = [response]

    for r in response:
        emit('conversation:response', {'message': r})

    emit('conversation:response:end')


if __name__ == '__main__':
    socketio.run(app)
