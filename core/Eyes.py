import cv2
import numpy
import pygame, sys
import os
import time
from pygame.locals import *
from PIL import Image, ImageFilter, ImageGrab

class Eyes(object):

    def __init__(self):
        self.width = 600
        self.height = 980
        self.x = 300
        self.y = 50
        self.x2 = self.x + self.width
        self.y2 = self.y + self.height

        self.qin = False

    def set_window(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (self.x, self.y)
        pygame.init()
        DISPLAY = pygame.display.set_mode((self.width, self.height), 0, 32)

        WHITE = (255, 255, 255)

        DISPLAY.fill(WHITE)

    def take_screenshot(self):
        return ImageGrab.grab((self.x, self.y, self.x2, self.y2))

    def start(self):
        self.set_window()
        while True:
            self.qin.put(self.take_screenshot())
            time.sleep(1)
