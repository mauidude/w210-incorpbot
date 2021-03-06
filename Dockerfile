FROM pytorch/pytorch

RUN apt-get update && apt-get install -y curl unzip gcc g++
RUN pip install --no-cache-dir tensorflow==2.1.0 spacy==2.2.3

ENV MODEL_CACHE=/root/.cache/torch

WORKDIR ${MODEL_CACHE}/use/
ENV USE_MODEL=use4
RUN curl -o ${USE_MODEL}.tar.gz https://storage.googleapis.com/tfhub-modules/google/universal-sentence-encoder/4.tar.gz && \
    tar -xf ${USE_MODEL}.tar.gz && \
    rm -rf ${USE_MODEL}.tar.gz

ENV SPACY_MODEL=en_core_web_lg
RUN python -m spacy download ${SPACY_MODEL}

WORKDIR ${MODEL_CACHE}/incorpbot/
ENV INCORPBOT_MODEL=squad-2.0
RUN curl -O https://storage.googleapis.com/w210-incorpbot/models/${INCORPBOT_MODEL}.zip && \
    unzip -d ${INCORPBOT_MODEL} ${INCORPBOT_MODEL} && \
    rm -rf ${INCORPBOT_MODEL}.zip

WORKDIR /user/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY data ./

COPY . .

CMD ["flask", "run", "--host=0.0.0.0"]
