import cv2
import numpy as np
import os
import time
import pytesseract
import random
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
from matplotlib import pyplot as plt
from PIL import Image, ImageFilter, ImageGrab


PREFLOP = 1
FLOP = 2
TURN = 3
RIVER = 4
S6 = 1
S12 = 2
CHECK = 1
BET = 2
CALL = 3
FOLD = 4

round_desc = {
    PREFLOP : 'Preflop',
    FLOP : 'Flop',
    TURN : 'Turn',
    RIVER : 'River',
}
player_desc = {
    S6: 's6',
    S12 : 's12',
}
action_desc = {
    CHECK : 'Check',
    BET : 'Bet',
    CALL : 'Call',
    FOLD : 'Fold',
}

round_card_no = {
    PREFLOP: 0,
    FLOP: 3,
    TURN: 4,
    RIVER: 5,
}

PATH_PIC = 'pics'

class Brain(object):
    def __init__(self):
        self.poker_identify = PATH_PIC + '/pokermaster_identify.png'
        self.btn_pic =  PATH_PIC + '/BTN.png'
        self.bet_pic = PATH_PIC + '/BET.png'
        self.call_pic = PATH_PIC + '/CALL.png'
        self.fold_pic = PATH_PIC + '/FOLD.png'
        self.check_pic = PATH_PIC + '/CHECK.png'
        self.is_find_table = False
        self.players_seq = [S6, S12]
        self.action_on = S12
        self.btn = False
        self.bb = False
        self.hands_num = 0
        self.round_last_action = False
        self.game_stage = PREFLOP
        self.hands_history = [{PREFLOP: [], FLOP: [], TURN: [], RIVER: []}]
        self.position_config = {
            'table_card' : [127, 470, 470, 560],
            'players' : {
                S12: {
                    'a' : [190, 15, 390, 200],
                    'name' : [60, 15, 160, 47],
                    'money' : [70, 120, 145, 145],
                    'bet' : [20, 145, 95, 170],
                },
                S6:{
                    'a': [135, 595, 440, 880],
                    'name': [115, 125, 215, 147],
                    'money': [125, 220, 205, 245],
                    'bet': [110, 90, 220, 120],
                },
            },
            'pot': [311, 263, 411, 307],
            'button': {
                '1/3' :[],
                '1/2' :[],
                '2/3' :[],
                '1' : [],
                '1.5': [],
                'allin': [],
                'check': [],
                'fold': [],
                'call': []
            }
        }
        values = "23456789TJQKA"
        suites = "CDHS"
        self.img = {}
        self.card_images = {}
        for x in values:
            for y in suites:
                name = PATH_PIC + '/' + x + y + '.png'
                if os.path.exists(name):
                    self.img[x + y.upper()] = Image.open(name)
                    self.card_images[x + y.upper()] = cv2.cvtColor(np.array(self.img[x + y.upper()]), cv2.COLOR_BGR2RGB)
                else:
                    print("Card template File not found: " + str(x) + str(y) + ".png")

        self.action_images = {
            BET: cv2.cvtColor(np.array(Image.open(PATH_PIC + '/BET.png')), cv2.COLOR_BGR2RGB),
            CALL: cv2.cvtColor(np.array(Image.open(PATH_PIC + '/CALL.png')), cv2.COLOR_BGR2RGB),
            CHECK: cv2.cvtColor(np.array(Image.open(PATH_PIC + '/CHECK.png')), cv2.COLOR_BGR2RGB),
            FOLD: cv2.cvtColor(np.array(Image.open(PATH_PIC + '/FOLD.png')), cv2.COLOR_BGR2RGB),
        }

        self.node = {}

        self.qin = False
        self.qout = False
        self.hands = False


    def set_hands(self, hands):
        self.hands = hands

    def match_template(self, screenshot, template):
        _template = cv2.cvtColor(np.array(template), cv2.COLOR_BGR2GRAY)
        #cv2.imshow('tmp', _template)
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        w, h = _template.shape[::-1]
        img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_BGR2GRAY)
        method = eval('cv2.TM_CCOEFF_NORMED')
        # Apply template Matching
        res = cv2.matchTemplate(img, _template, method)
        loc = np.where(res >= 0.97)

        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

        # If the method is TM_SQDIFF or TM_SQDIFF_NORMED, take minimum
        if method in [cv2.TM_SQDIFF, cv2.TM_SQDIFF_NORMED]:
            best_fit = min_loc
        else:
            best_fit = max_loc

        count = 0
        points = []
        for pt in zip(*loc[::-1]):
            #cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (7,249,151), 2)
            count += 1
            points.append(pt)

        #if count >= 1:
        #    cv2.imshow('Detected', img)
        #    cv2.waitKey(0)
        #    cv2.destroyAllWindows()

        return count, points, best_fit, min_val

    def find_table(self, screenshot):
        count, points, best_fit, min_val = self.match_template(screenshot, Image.open(self.poker_identify))

        return count >= 1

    def check_table_card(self, screenshot):
        self.cards_on_table = []
        table_card_position = self.position_config['table_card']
        table_card_img = screenshot.crop((table_card_position[0], table_card_position[1],
                                    table_card_position[2], table_card_position[3]))

        # cv2.imshow('Detected', np.array(table_card_img))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        for key, template in self.card_images.items():
            count, points, best_fit, min_val = self.match_template(table_card_img, template)
            if count >= 1:
                self.cards_on_table.append(key)

        # self.game_stage = PREFLOP
        #
        # if len(self.cards_on_table) < 1:
        #     self.game_stage = PREFLOP
        # elif len(self.cards_on_table) == 3:
        #     self.game_stage = FLOP
        # elif len(self.cards_on_table) == 4:
        #     self.game_stage = TURN
        # elif len(self.cards_on_table) == 5:
        #     self.game_stage = RIVER

    def check_player_on_action(self, screenshot, player):
        position_a = self.position_config['players'][player]['a']
        position_money = self.position_config['players'][player]['money']

        imga = screenshot.crop((position_a[0], position_a[1],
                                position_a[2], position_a[3]))

        imgm = screenshot.crop((position_money[0], position_money[1],
                             position_money[2], position_money[3]))
        # cv2.imshow('Detected', np.array(s12_img))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        #
        # cv2.imshow('Detected', np.array(s6_img))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        #
        # cv2.imshow('Detected', np.array(s12_money))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        #
        # cv2.imshow('Detected', np.array(s6_money))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        #self.players[player]['name'] = player;
        self.players[player]['money'] = pytesseract.image_to_string(imgm);

        action = False
        bet_size = False
        for key, template in self.action_images.items():
            count, points, best_fit, min_val = self.match_template(imga, template)
            if count >= 1:
                self.players[player]['action'] = key
                action = key
                if key == BET:
                    bet_size = self.check_betsize(imga, player)
                break

        return action, bet_size

    def check_player_status(self, screenshot):
        self.players = {S12 : {}, S6 : {}}
        player_position_s6 = self.position_config['players'][S6]['a']
        player_position_s12 = self.position_config['players'][S12]['a']
        player_position_s6_name = self.position_config['players'][S6]['name']
        player_position_s12_name = self.position_config['players'][S12]['name']
        player_position_s6_money = self.position_config['players'][S6]['money']
        player_position_s12_money = self.position_config['players'][S12]['money']

        s12_img = screenshot.crop((player_position_s12[0], player_position_s12[1],
                                   player_position_s12[2], player_position_s12[3]))
        s6_img = screenshot.crop((player_position_s6[0], player_position_s6[1],
                                  player_position_s6[2], player_position_s6[3]))

        s12_name = s12_img.crop((player_position_s12_name[0], player_position_s12_name[1],
                                    player_position_s12_name[2], player_position_s12_name[3]))
        s6_name = s6_img.crop((player_position_s6_name[0], player_position_s6_name[1],
                                   player_position_s6_name[2], player_position_s6_name[3]))

        s12_money = s12_img.crop((player_position_s12_money[0], player_position_s12_money[1],
                                     player_position_s12_money[2], player_position_s12_money[3]))
        s6_money = s6_img.crop((player_position_s6_money[0], player_position_s6_money[1],
                                    player_position_s6_money[2], player_position_s6_money[3]))


        # cv2.imshow('Detected', np.array(s12_img))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        #
        # cv2.imshow('Detected', np.array(s6_img))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        #
        # cv2.imshow('Detected', np.array(s12_money))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        #
        # cv2.imshow('Detected', np.array(s6_money))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        self.players[S12]['name'] = 's12';
        self.players[S6]['name'] = 's6';
        self.players[S12]['money'] = pytesseract.image_to_string(s12_money);
        self.players[S6]['money'] = pytesseract.image_to_string(s6_money);

        count, points, best_fit, min_val = self.match_template(s6_img, Image.open(self.btn_pic))
        if count >= 1:
            if self.btn != S6 and len(self.cards_on_table) == round_card_no[PREFLOP]:
                self.new_hand(S6, S12)
        else:
            if self.btn != S12 and len(self.cards_on_table) == round_card_no[PREFLOP]:
                self.new_hand(S12, S6)


        for key, template in self.action_images.items():
            count, points, best_fit, min_val = self.match_template(s6_img, template)
            if count >= 1:
                self.players[S6]['action'] = key
                if key == BET:
                    self.check_betsize(s6_img, S6)
                break

        for key, template in self.action_images.items():
            count, points, best_fit, min_val = self.match_template(s12_img, template)
            if count >= 1:
                self.players[S12]['action'] = key
                if key == BET:
                    self.check_betsize(s12_img, S12)
                break

    def new_hand(self, btn, bb):
        self.hands_num += 1
        self.players_seq = [bb, btn]
        self.hands_history.insert(self.hands_num, {PREFLOP: [], FLOP: [], TURN: [], RIVER: []})
        self.btn = btn
        self.bb = bb
        self.game_stage = PREFLOP
        self.round_last_action = False

    def check_betsize(self, screenshot, player):
        bet_size_position = self.position_config['players'][player]['bet']

        img = screenshot.crop((bet_size_position[0], bet_size_position[1],
                               bet_size_position[2], bet_size_position[3]))

        # cv2.imshow('Detected', np.array(img))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
        #while true:
        bet_size = pytesseract.image_to_string(img);
        #    if (bet_size.isdigit()):
        #        break;

        self.players[player]['betsize'] = bet_size;
        return bet_size

    def check_pot(self, screenshot):
        pot_postion = self.position_config['pot']
        img = screenshot.crop((pot_postion[0], pot_postion[1],
                               pot_postion[2], pot_postion[3]))

        # cv2.imshow('Detected', np.array(img))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        self.pot = pytesseract.image_to_string(img);


    def get_action_from_strategy(self, strategy):
        r = random.random()
        if r < strategy['bet'] :
            action = 'bet'
        elif r < strategy['bet'] + strategy['call'] and r >= strategy['bet'] :
            action = 'call'
        elif r < strategy['bet'] + strategy['call'] + strategy['fold'] and r >= strategy['bet'] + strategy['call'] :
            action = 'call'

        return action

    def do_action(self, info):
        node = Node.find_node(info['npid'], info['oacttion'])
        strategy = node.get_strategy(info['mycard'])
        action = self.get_action_from_strategy(strategy)
        self.node = next_node()





    def start(self):
         i = 0
         while True:
             s = self.qin.get(True)
             # print('get a sth from eyes')
             if self.is_find_table == False :
                if self.find_table(s) :
                    print('find a table')
                    self.is_find_table = True
             else:
                 self.check_table_card(s)
                 self.check_player_status(s)
                 if self.btn == False:
                     continue
                 # if self.game_stage == PREFLOP:
                 #     if len(self.hands_history[self.hands_num][self.game_stage]) == 0:
                 #        self.action_on = self.btn
                 # else:
                 #     if len(self.hands_history[self.hands_num][self.game_stage]) == 0:
                 #        self.action_on = self.bb
                 #
                 # action, bet_size = self.check_player_on_action(s, self.action_on)
                 # if action:
                 #     action_data = {'palyer': player_desc[self.action_on], 'action': action_desc[action], 'bet_size': bet_size}
                 #     self.hands_history[self.hands_num][self.game_stage].append(action_data)
                 #     self.action_on = self.players_seq[(self.players_seq.index(self.action_on) + 1) % 2]
                 #     self.check_pot(s)
                 #     print (
                 #     'table stage', round_desc[self.game_stage], 'cards on table', self.cards_on_table, 'action', action_data, 'pot', self.pot)
                 if self.game_stage == PREFLOP:
                     if len(self.hands_history[self.hands_num][self.game_stage]) == 0:
                        self.action_on = self.btn
                     action, bet_size = self.check_player_on_action(s, self.action_on)
                     if action == False :
                         continue

                     action_data = {'palyer': player_desc[self.action_on], 'action': action_desc[action],
                                    'bet_size': bet_size}
                     self.hands_history[self.hands_num][self.game_stage].append(action_data)
                     self.action_on = self.players_seq[(self.players_seq.index(self.action_on) + 1) % 2]
                     self.check_pot(s)
                     print (
                         'table stage', round_desc[self.game_stage], 'cards on table', self.cards_on_table,
                         'action', action_data, 'pot', self.pot)

                     if action == BET:
                         self.round_last_action = BET
                     elif action == CALL and self.round_last_action == BET:
                         self.game_stage = FLOP
                         self.round_last_action = False
                     elif action == CHECK:
                         self.game_stage = FLOP
                         self.round_last_action = False
                 else:
                     if len(self.cards_on_table) < round_card_no[self.game_stage]:
                         continue
                     if len(self.hands_history[self.hands_num][PREFLOP]) == 0:
                         continue
                     if len(self.hands_history[self.hands_num][self.game_stage]) == 0:
                        self.action_on = self.bb
                     action, bet_size = self.check_player_on_action(s, self.action_on)

                     if action == False :
                         continue

                     action_data = {'palyer': player_desc[self.action_on], 'action': action_desc[action],
                                    'bet_size': bet_size}
                     self.hands_history[self.hands_num][self.game_stage].append(action_data)
                     self.action_on = self.players_seq[(self.players_seq.index(self.action_on) + 1) % 2]
                     self.check_pot(s)
                     print (
                         'table stage', round_desc[self.game_stage], 'cards on table', self.cards_on_table,
                         'action', action_data, 'pot', self.pot)

                     if action == BET:
                         self.round_last_action = BET
                     elif action == CALL:
                         self.game_stage = TURN if self.game_stage == FLOP else RIVER
                         self.round_last_action = False
                     elif action == CHECK:
                         if self.round_last_action == CHECK:
                             self.game_stage = TURN if self.game_stage == FLOP else RIVER
                             self.round_last_action = False
                         else:
                             self.round_last_action = CHECK



