FROM python:3.7

RUN pip3 install --no-cache-dir torch==1.4.0 pymagnitude==0.1.120

ENV MODEL_CACHE=/root/.cache/torch

# download sentence transformer model
ENV SENTENCE_TRANSFORMERS_MODEL=bert-base-nli-stsb-mean-tokens
WORKDIR ${MODEL_CACHE}/sentence_transformers/
RUN curl -O   \
    https://public.ukp.informatik.tu-darmstadt.de/reimers/sentence-transformers/v0.2/${SENTENCE_TRANSFORMERS_MODEL}.zip && \
    unzip -d public.ukp.informatik.tu-darmstadt.de_reimers_sentence-transformers_v0.2_${SENTENCE_TRANSFORMERS_MODEL}.zip ${SENTENCE_TRANSFORMERS_MODEL}.zip && \
    rm -rf ${SENTENCE_TRANSFORMERS_MODEL}.zip

WORKDIR ${MODEL_CACHE}/incorpbot/
ENV INCORPBOT_MODEL=squad-1.0
RUN curl -O https://storage.googleapis.com/w210-incorpbot/models/${INCORPBOT_MODEL}.zip && \
    unzip -d ${INCORPBOT_MODEL} ${INCORPBOT_MODEL} && \
    rm -rf ${INCORPBOT_MODEL}.zip

WORKDIR ${MODEL_CACHE}/glove/
ENV GLOVE_MODEL=glove.6B.100d.magnitude
RUN curl -O http://magnitude.plasticity.ai/glove/medium/${GLOVE_MODEL}

WORKDIR /user/src/app

COPY requirements.txt ./
RUN pip3 install --no-cache-dir -r requirements.txt

# install nltk tokenizer
RUN python3 -c "import nltk; nltk.download('punkt')"

COPY data ./

COPY . .
