
FINAL_ROUND = 4
OOP = 0
IP = 1
class Holdem(object):
    def __init__(self):
        self.cards = []
        values = "23456789TJQKA"
        suites = "CDHS"
        for x in values:
            for y in suites:
                self.cards.append(x + y)
        self.bet_size = [0.3, 0.5, 0.7, 1, 1.5, 10]
        self.roles = ['oop', 'ip']
        self.deccision_root = {
            'bet' : {},
            'call' : {},
            'fold' : {},
            'role' : OOP,
            'stacks' + OOP : 0,
            'stacks' + IP : 0,
            'table_cards' : [],
            'round' : 0,
            'need_to_call' : 0,
            'pot' : 0,
            'ev' : 0,
            'is_leaf' : False,
        }

    def make_decision_tree(self, deccision_node):
        if deccision_node['is_leaf'] :
            return
        if deccision_node['need_to_call'] < deccision_node['my_chip_stacks']:
            new_role = deccision_node['role'] % 2
            node_bet = self.make_new_action_node(new_role,
                                                 deccision_node['stacks' + OOP],
                                                 deccision_node['stacks' + IP],
                                                 deccision_node['round'],
                                                 bet_size - deccision_node['need_to_call'],
                                                 deccision_node['pot'] + bet_size)
            node_bet['stacks' + deccision_node['role']] = node_bet['stacks' + deccision_node['role']] - bet_size
            deccision_node['bet'] = self.make_decision_tree(node_bet)

        if deccision_node['need_to_call'] > 0:
            node = self.make_next_round_node(deccision_node['round'],
                                             deccision_node['stacks' + OOP],
                                             deccision_node['stacks' + IP],
                                             deccision_node['pot'] + deccision_node['need_to_call'])
            node['stacks' + deccision_node['role']] = node['stacks' + deccision_node['role']] - deccision_node['need_to_call']
            deccision_node['call'] = self.make_decision_tree(node)

        if deccision_node['need_to_call'] == 0:
            if deccision_node['role'] == IP:
                node = self.make_next_round_node(deccision_node['round'],
                                                 deccision_node['stacks' + OOP],
                                                 deccision_node['stacks' + IP],
                                                 deccision_node['pot'] + deccision_node['need_to_call'])
                node['stacks' + deccision_node['role']] = node['stacks' + deccision_node['role']] - deccision_node['need_to_call']
                deccision_node['call'] = self.make_decision_tree(node)

            else:
                node = self.make_new_action_node(deccision_node['role'] % 2,
                                                 deccision_node['stacks' + OOP],
                                                 deccision_node['stacks' + IP],
                                                 deccision_node['round'],
                                                 0,
                                                 deccision_node['pot'])
                deccision_node['call'] = self.make_decision_tree(node)


        deccision_tree['fold'] = self.make_leaf_node()


    def make_leaf_node(self):
        return {
            'is_leaf' : True,
        }

    def make_new_action_node(self, role, stacks_OOP, stacks_IP, round, need_to_call, pot):
        return {
            'role': role,
            'stacks' + OOP : stacks_OOP,
            'stacks' + IP : stacks_IP,
            'table_cards': [],
            'round': round,
            'need_to_call': need_to_call,
            'pot': pot,
        }

    def make_next_round_node(self, round, stacks_OOP, stacks_IP, pot):
        if round == FINAL_ROUND:
            node = self.make_leaf_node()
        else:
            node = self.make_new_action_node(OOP,
                                             stacks_OOP,
                                             stacks_IP,
                                             round + 1,
                                             0,
                                             pot)

        return node
