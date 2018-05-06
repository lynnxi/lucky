class Event(object):
    def __init__(self, data):
        self.data = data
        self.id = json.dumps(data)


