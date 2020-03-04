import json


class Manager(object):
    def __init__(self, redis):
        self.redis = redis

    def get(self, cid, key=None):
        state = self.redis.get(cid)
        payload = {}
        if state:
            payload = json.loads(state)

        if key:
            return payload.get(key, None)

        return payload

    def set(self, cid, state):
        self.redis.set(cid, json.dumps(state))

    def update(self, cid, state):
        current = self.get(cid)
        current.update(state)

        self.set(cid, current)

    def delete_key(self, cid, key):
        current = self.get(cid)
        del current[key]

        self.set(cid, current)
