import cv2
import numpy as np
import os
import time
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract'
from matplotlib import pyplot as plt
from PIL import Image, ImageFilter, ImageGrab

class Brain(object):
    def __init__(self):
        self.poker_identify = '../pics/pokermaster_identify.png'
        self.btn_pic = '../pics/BTN.png'
        self.bet_pic = '../pics/BET.png'
        self.call_pic = '../pics/CALL.png'
        self.fold_pic = '../pics/FOLD.png'
        self.check_pic = '../pics/CHECK.png'
        self.is_find_table = False
        self.position_config = {
            'table_card' : [127, 470, 437, 560],
            'players' : {
                's12': {
                    'a' : [190, 15, 390, 200],
                    'name' : [60, 15, 160, 47],
                    'money' : [70, 120, 145, 145],
                    'bet' : [20, 145, 95, 170],
                },
                's6':{
                    'a': [135, 595, 440, 880],
                    'name': [115, 125, 215, 147],
                    'money': [125, 220, 205, 245],
                    'bet': [110, 90, 220, 120],
                },
            },
            'pot': [311, 263, 411, 307]
        }
        values = "23456789TJQKA"
        suites = "CDHS"
        self.img = {}
        self.card_images = {}
        for x in values:
            for y in suites:
                name = "../pics/" + x + y + ".png"
                if os.path.exists(name):
                    self.img[x + y.upper()] = Image.open(name)
                    self.card_images[x + y.upper()] = cv2.cvtColor(np.array(self.img[x + y.upper()]), cv2.COLOR_BGR2RGB)
                else:
                    print("Card template File not found: " + str(x) + str(y) + ".png")

        self.action_images = {
            'bet': cv2.cvtColor(np.array(Image.open('../pics/BET.png')), cv2.COLOR_BGR2RGB),
            'call': cv2.cvtColor(np.array(Image.open('../pics/CALL.png')), cv2.COLOR_BGR2RGB),
            'check': cv2.cvtColor(np.array(Image.open('../pics/CHECK.png')), cv2.COLOR_BGR2RGB),
            'fold': cv2.cvtColor(np.array(Image.open('../pics/FOLD.png')), cv2.COLOR_BGR2RGB),
        }

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
            cv2.rectangle(img, pt, (pt[0] + w, pt[1] + h), (7,249,151), 2)
            count += 1
            points.append(pt)

        #if count >= 1:
        #    cv2.imshow('Detected', img)
        #    cv2.waitKey(0)
        #    cv2.destroyAllWindows()

        return count, points, best_fit, min_val

    def find_table(self, screenshot):
        cont, points, best_fit, min_val = self.match_template(screenshot, Image.open(self.poker_identify))

        return cont >= 1

    def check_table_card(self, screenshot):
        self.cards_on_table = []
        table_card_position = self.position_config['table_card']
        table_card_img = screenshot.crop((table_card_position[0], table_card_position[1],
                                    table_card_position[2], table_card_position[3]))

        #cv2.imshow('Detected', np.array(table_card_img))
        #cv2.waitKey(0)
        #cv2.destroyAllWindows()
        for key, template in self.card_images.items():
            count, points, best_fit, min_val = self.match_template(table_card_img, template)
            if count >= 1:
                self.cards_on_table.append(key)

        self.game_stage = ''

        if len(self.cards_on_table) < 1:
            self.game_stage = "PreFlop"
        elif len(self.cards_on_table) == 3:
            self.game_stage = "Flop"
        elif len(self.cards_on_table) == 4:
            self.game_stage = "Turn"
        elif len(self.cards_on_table) == 5:
            self.game_stage = "River"

    def check_player_status(self, screenshot):
        self.players = {'s12' : {}, 's6' : {}}
        player_position_s6 = self.position_config['players']['s6']['a']
        player_position_s12 = self.position_config['players']['s12']['a']
        player_position_s6_name = self.position_config['players']['s6']['name']
        player_position_s12_name = self.position_config['players']['s12']['name']
        player_position_s6_money = self.position_config['players']['s6']['money']
        player_position_s12_money = self.position_config['players']['s12']['money']

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

        self.players['s12']['name'] = 's12';
        self.players['s6']['name'] = 's6';
        self.players['s12']['money'] = pytesseract.image_to_string(s12_money);
        self.players['s6']['money'] = pytesseract.image_to_string(s6_money);

        cont, points, best_fit, min_val = self.match_template(s6_img, Image.open(self.btn_pic))
        if cont >= 1:
            self.players['s6']['btn'] = True
            self.players['s12']['btn'] = False

        for key, template in self.action_images.items():
            count, points, best_fit, min_val = self.match_template(s6_img, template)
            if count >= 1:
                self.players['s6']['action'] = key
                if key == 'bet':
                    self.check_betsize(s6_img, 's6')
                break

        for key, template in self.action_images.items():
            count, points, best_fit, min_val = self.match_template(s12_img, template)
            if count >= 1:
                self.players['s12']['action'] = key
                if key == 'bet':
                    self.check_betsize(s12_img, 's12')
                break

    def check_betsize(self, screenshot, player):
        bet_size_position = self.position_config['players'][player]['bet']

        img = screenshot.crop((bet_size_position[0], bet_size_position[1],
                               bet_size_position[2], bet_size_position[3]))

        # cv2.imshow('Detected', np.array(img))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        self.players[player]['betsize'] = pytesseract.image_to_string(img);

    def check_pot(self, screenshot):
        pot_postion = self.position_config['pot']
        img = screenshot.crop((pot_postion[0], pot_postion[1],
                               pot_postion[2], pot_postion[3]))

        # cv2.imshow('Detected', np.array(img))
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        self.pot = pytesseract.image_to_string(img);


    def start(self, q):
         while True:
             s = q.get(True)
             # print('get a sth from eyes')
             if self.is_find_table == False :
                if self.find_table(s) :
                    print('find a table')
                    self.is_find_table = True
             else:
                 self.check_table_card(s)
                 print ('table stage', self.game_stage, 'cards on table', self.cards_on_table)
                 self.check_player_status(s)
                 print ('players', self.players)
                 self.check_pot(s)
                 print ('pot', self.pot)