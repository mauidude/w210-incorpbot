

class Retriever(object):
    def __init__(self, elastic, embedding_model, index, max_records=10, verbose=False):
        self.elastic = elastic
        self.embedding_model = embedding_model
        self.max_records = max_records
        self.index = index
        self.verbose = verbose

    def retrieve(self, text):
        # get sentence embeddings
        embeddings = self.embedding_model([text])[0].numpy()

        query = {
            'from': 0,
            'size': self.max_records,
            'query': {
                'script_score': {
                    'query': {
                        'match_all': {}
                    },
                    'script': {
                        'source': f"cosineSimilarity(params.query_vector, doc['universal_sentence_embeddings']) + 1.0",
                        'params': {
                            'query_vector': embeddings.tolist()
                        }
                    }
                }
            }
        }

        results = self.elastic.search(index=self.index, body=query)
        print(
            f"found {results['hits']['total']['value']} results in {results['took']} ms")

        for i, result in enumerate(results['hits']['hits']):
            document = result['_source']
            score = result['_score']

            if self.verbose:
                print(f'Result {i} {score}:')
                print(document['text'])
                print('-' * 50)

        # concatenate top N results to use as context paragraph in QA model
        context = '\n'.join([
            result['_source']['text']
            for result in results['hits']['hits']
        ])

        return context
