class Node(object):
    def __init__(self, entries={}):
        if entries :
            self._dict_.update(entries)
        else:
            self.sub_nid = {}
            self.event = {}
            self.data = {
                'role': OOP,
                'btn' : '',
                'stacks' + OOP: 0,
                'stacks' + IP: 0,
                'table_cards': [],
                'round': 0,
                'need_to_call': 0,
                'pot': 0,
                'ev': 0,
                'is_leaf': False,
            }

            self.strategy = {}
            values = "23456789TJQKA"
            suites = "CDHS"
            for x in values:
                for y in suites:
                    self.strategy[x + y] = {
                        '0.3' : 0.125,
                        '0.5': 0.125,
                        '0.7': 0.125,
                        '1': 0.125,
                        '1.5': 0.125,
                        '0': 0.125, #allin
                        'check' : 0.125,
                        'call' : 0.125,
                        'fold' : 0.125,
                    }

            self._id = self.save()
            self.nid = self._id

    def get_strategy(self, card):
        return self.strategy[card]

    def save(self):
        mongo = MongoManager()
        return mongo.save(self._dict_)

    def find(nid):
        mongo = MongoManager()
        ret = mongo.find({'_id' : nid})
        return Node(ret)