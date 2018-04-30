
FINAL_ROUND = 5
PREFLOP = 1
FLOP = 2
TURN = 3
RIVER = 4

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
        self.decision_root = {
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
            'strategy' : {}
        }

    def init_strategy(self):
        strategy = {}
        for i in range(len(self.cards) - 2):
            for j in range(i + 1, len(self.cards) - i - 1):
                strategy[i][j] = 1

        return strategy

    def make_decision_tree(self, decision_node):
        if decision_node['is_leaf'] :
            return decision_node

        if decision_node['need_to_call'] < decision_node['my_chip_stacks']:
            new_role = decision_node['role'] % 2
            for i in self.bet_size:
                bet_size = round(decision_node['pot'] * i)
                node_bet = self.make_new_action_node(new_role,
                                                     decision_node['stacks' + OOP],
                                                     decision_node['stacks' + IP],
                                                     decision_node['round'],
                                                     bet_size - decision_node['need_to_call'],
                                                     decision_node['pot'] + bet_size)
                node_bet['stacks' + decision_node['role']] = node_bet['stacks' + decision_node['role']] - bet_size
                decision_node['bet'][bet_size] = self.make_decision_tree(node_bet)

        if decision_node['need_to_call'] > 0:
            if decision_node['role'] == OOP:
                stacks_OOP = decision_node['stacks' + OOP] - decision_node['need_to_call']
                stacks_IP = decision_node['stacks' + IP]
            else:
                stacks_OOP = decision_node['stacks' + OOP]
                stacks_IP = decision_node['stacks' + IP] - decision_node['need_to_call']
            nodes = self.make_next_round_nodes(decision_node['round'],
                                               stacks_OOP,
                                               stacks_IP,
                                               decision_node['pot'] + decision_node['need_to_call'])
            for key in nodes:
                decision_node['call'][key] = self.make_decision_tree(nodes[key])

        if decision_node['need_to_call'] == 0:
            if decision_node['role'] == IP:
                nodes = self.make_next_round_nodes(decision_node['round'],
                                                 decision_node['stacks' + OOP],
                                                 decision_node['stacks' + IP],
                                                 decision_node['pot'] + decision_node['need_to_call'])
                for key in nodes:
                    decision_node['call'][key] = self.make_decision_tree(nodes[key])

            else:
                node = self.make_new_action_node(decision_node['role'] % 2,
                                                 decision_node['stacks' + OOP],
                                                 decision_node['stacks' + IP],
                                                 decision_node['round'],
                                                 0,
                                                 decision_node['pot'])
                decision_node['call'][0] = self.make_decision_tree(node)

        decision_node['fold'] = self.make_leaf_node()

        return decision_node


    def make_leaf_node(self):
        return {
            'is_leaf' : True,
        }

    def make_new_action_node(self, role, stacks_OOP, stacks_IP, round, need_to_call, pot, table_cards):
        return {
            'role': role,
            'stacks' + OOP : stacks_OOP,
            'stacks' + IP : stacks_IP,
            'table_cards': table_cards,
            'round': round,
            'need_to_call': need_to_call,
            'pot': pot,
        }

    def make_next_round_nodes(self, round, stacks_OOP, stacks_IP, pot, table_cards):
        nodes = {}
        round += 1
        if round == FINAL_ROUND:
            nodes[0] = self.make_leaf_node()
        elif round == FLOP:
            for i in range(len(self.cards) - 2):
                for j in range(i + 1, len(self.cards) - i - 1):
                    for k in range(len(j + 1, self.cards) - j - 1):
                        table_cards.append(self.cards[i])
                        table_cards.append(self.cards[j])
                        table_cards.append(self.cards[k])
                        nodes[str(table_cards)] = self.make_new_action_node(OOP,
                                                         stacks_OOP,
                                                         stacks_IP,
                                                         round,
                                                         0,
                                                         pot,
                                                         table_cards)
        elif round == TURN or round == RIVER:
            for i in self.cards:
                if i not in table_cards:
                    table_cards.append(i)
                    nodes[str(table_cards)] = self.make_new_action_node(OOP,
                                                                        stacks_OOP,
                                                                        stacks_IP,
                                                                        round,
                                                                        0,
                                                                        pot,
                                                                        table_cards)


        return nodes
