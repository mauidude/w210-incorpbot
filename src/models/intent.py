import numpy as np


class Model(object):
    def __init__(self, model, elastic, index, verbose=False):
        self.model = model
        self.elastic = elastic
        self.index = index
        self.verbose = verbose

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
                print(f'Input: "{text}" - result {score}: {category}')

            return category
