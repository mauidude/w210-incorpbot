import pickle
import re
from urllib.request import urlopen

import numpy as np
import pandas as pd
from nltk import word_tokenize
from pymagnitude import *
from scipy import sparse


def is_url(path):
    return re.match('^https?:', path)


class Model(object):
    def __init__(self, model_path_or_url, embedding_model_path_or_url, tokenizer=word_tokenize):
        self.tokenizer = word_tokenize

        if is_url(embedding_model_path_or_url):
            self.embedding_model = Magnitude(
                MagnitudeUtils.download_model(embedding_model_path_or_url))
        else:
            self.embedding_model = Magnitude(embedding_model_path_or_url)

        # get model
        if is_url(model_path_or_url):
            model_data = urlopen(model_path_or_url)
        else:
            model_data = open(model_path_or_url, 'rb')

        self.label_encoder, self.model = pickle.load(model_data)
        model_data.close()

    def featurize(self, df):
        # TODO: maybe add other features
        return self._avg_word_embeddings(df)

    def classify(self, text, return_label_name=False):
        df = pd.DataFrame({'input': [text]})
        x = self.featurize(df)

        predicted = self.model.predict(x)
        if return_label_name:
            return self.label_encoder.inverse_transform(predicted)[0]

        return predicted[0]

    def _avg_word_embeddings(self, df):
        vectors = []
        for text in df.input.values:
            tokens = self.tokenizer(text)
            vectors.append(np.average(
                self.embedding_model.query(tokens), axis=0))

        return np.array(vectors)
