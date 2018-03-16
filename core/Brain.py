import cv2
import numpy as np
import os
import time
from matplotlib import pyplot as plt
from PIL import Image, ImageFilter, ImageGrab

class Brain(object):
    def __init__(self):
        self.poker_identify = '../pics/pokermaster_identify.png'
        self.is_find_table = False
        self.position_config = {'table_card' : [127, 470, 437, 560]}
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

        if count >= 1:
            cv2.imshow('Detected', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

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

    def start(self, q):
         while True:
             s = q.get(True)
             print('get a sth from eyes')
             if self.is_find_table == False :
                if self.find_table(s) :
                    print('find a table')
                    self.is_find_table = True
             else:
                 self.check_table_card(s)
                 print ('table stage', self.game_stage, 'cards on table', self.cards_on_table)