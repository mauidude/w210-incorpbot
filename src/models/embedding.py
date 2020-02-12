

class Model(object):
    def __init__(self, model):
        self.model = model

    def embedding(self, sentence):
        return self.model([sentence])[0].numpy()
