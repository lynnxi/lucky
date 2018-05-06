set1 = set(['a1', 'b2', 'c3'])
set2 = set(['b2', 'a1', 'c3'])
print (set1, set2)
print (set1 == set2)
pass


node_r = {
    'bet': {},
    'call': {},
    'fold': {},
    'role': 1,
    'stacks': 0,
    'stacks': 0,
    'table_cards': [],
    'round': 0,
    'need_to_call': 0,
    'pot': 0,
    'ev': 0,
    'is_leaf': False,
}

class node(object):
    def __init__(self):
        self.bet = {}
        self.call = {}



i = 0
def make_decision_tree(node):
    global i
    if i == 3:
        return 1

    print (i)
    i += 1
    node['bet'] = make_decision_tree({'bet':{}})
    return node
    print (node)


make_decision_tree(node_r)
print(node_r)