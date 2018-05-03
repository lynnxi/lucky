class Node(object):
    def __init__(self):

        self.id = 0
        self.pid = 0
        self.bet = 0
        self.call = 0
        self.fold = 0

        self.data = {
            'role': OOP,
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
                self.strategy[x + y] = {'bet' : 1, 'call' : 1, 'fold' : 1}

    def get_strategy(self, card):
        return self.strategy[card]

    def find_node(info):
        return Node()

    def build_node():
        return Node()
