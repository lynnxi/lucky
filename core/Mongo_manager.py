'''
Functions that are used to log and analyse present and past pokergames
'''
import datetime
import os
import sys


import numpy as np
from pymongo import MongoClient


class MongoManager(object):
    def __init__(self):
        self.mongoclient = MongoClient('mongodb://127.0.0.1:27017/lucky')
        self.mongodb = self.mongoclient.lucky

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(MongoManager, cls).__new__(cls)
        return cls.instance

    def find(self, param):
        ret = {}
        try:
            cursor = self.mongodb.node.find(param)
            ret = cursor.next()
        except:
            pass
        return ret

    def save(self, data):
        id = self.mongodb.node.save(data)
        return id



