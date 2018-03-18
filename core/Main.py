from multiprocessing import Process, Queue
import os
from Eyes import Eyes
from Brain import Brain

if __name__=='__main__':
    eyes = Eyes()
    brain = Brain()
    q = Queue(50)
    _eyes = Process(target=eyes.start, args=(q,))
    _brain = Process(target=brain.start, args=(q,))
    print('Eyes start', end = '         ')
    _eyes.start()
    print('Done')
    _brain.start()
    print('Lucky start.')