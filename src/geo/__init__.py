# mapping from canonical name to elastic search name
states = {
    'california': 'California'
}


def lookup(state):
    if state.lower() in states:
        return (states[state.lower()], True)

    return (state.title(), False)


class Resolver(object):
    def __init__(self, nlp):
        self.nlp = nlp

    def resolve_state(self, text):
        ''' resolve_state returns a tuple where the first item is the geo political entity
        and the second item is whether or not it is a supported state'''

        doc = self.nlp(text)

        candidates = [
            lookup(ent.text) for ent in doc.ents
            if ent.label_ == 'GPE'
        ]

        if not candidates:
            return None

        # get first state that is supported
        for c in candidates:
            if c[1]:
                return c

        # if none are supported, just return first unsupported
        return candidates[0]
