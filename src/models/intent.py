import numpy as np


class Model(object):
    def __init__(self, model, elastic, index, threshold, verbose=False):
        self.model = model
        self.elastic = elastic
        self.index = index
        self.verbose = verbose
        self.threshold = threshold

    def classify(self, text):
        embeddings = self.model([text])[0].numpy()

        query = {
            'from': 0,
            'size': 1,
            'query': {
                'script_score': {
                    'query': {
                        'match_all': {}
                    },
                    'script': {
                        'source': "cosineSimilarity(params.query_vector, doc['centroid'])",
                        'params': {
                            'query_vector': embeddings.tolist()
                        }
                    }
                }
            }
        }

        results = self.elastic.search(index=self.index, body=query)

        for result in results['hits']['hits']:
            document = result['_source']
            score = result['_score']
            category = document['category']

            if self.verbose:
                print(f'input: "{text}" - result {score}: {category}')

            # score from elasticsearch is 1 if they are close and 0 if they are not
            # so invert it:
            score = 1 - score

            # if score is above threshold (too far from any other classes),
            # we will assume it is a question
            if score > self.threshold:
                return 'question'

            return category
