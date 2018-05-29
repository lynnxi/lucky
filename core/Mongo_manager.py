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

    def find(self, param):
        ret = {}
        try:
            cursor = self.mongodb.node.find(param)
            ret = cursor.next()
        except:
            pass
        return ret

    def save(self, data):
        result = self.mongodb.node.insert_one(data)

    def update(self, data):
        try:
            del data['_id']
        except:
            pass
        ret = self.mongodb.lucky.update_one(
            {"id": data['id']},
            {"$set": strategy}
        )


