import numpy
import pygame, sys
import os
import time
import random

from tools import pymouse

class Hands(object):

    def __init__(self):
        self.mouse = pymouse.PyMouse()
        self.qout = False

    def click(self, x, y):
        self.mouse.move(x, y)
        self.mouse.click(x, y)

    def start(self):
        step = 1

        ex = 520
        ey = 520
        while True:
            sx, sy = self.mouse.position()

            if ex - sx == 0 and ey - sy == 0 :
                break

            if ex - sx > 0:
                x = sx + step
            elif ex - sx < 0:
                x = sx - step

            if ey - sy > 0:
                y = sy + step
            elif ey - sy < 0:
                y = sy - step

            self.mouse.move(x, y)
            time.sleep(0.001)