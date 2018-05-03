from multiprocessing import Process, Queue
import os
from core.Eyes import Eyes
from core.Hands import Hands
from core.Brain import Brain

from tools import pymouse

if __name__=='__main__':
    eyes = Eyes()
    hands = Hands()
    brain = Brain()

    qin = Queue(50)
    qout = Queue(50)

    eyes.qin = qin
    hands.qout = qout
    brain.qin = qin
    brain.qout = qout

    peyes = Process(target=eyes.start)
    phands = Process(target=hands.start)
    pbrain = Process(target=brain.start)

    print('Eyes start', end = '         ')
    peyes.start()
    print('Done')

    print('Hands start', end = '         ')
    phands.start()
    print('Done')

    pbrain.start()
    print('Lucky start.')