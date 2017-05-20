import redis
import algorithms.Apriori
from multiprocessing import Pool


apriori = Apriori()

class Master(object):

    def __init__(self, count_worker):
        self.pool = Pool(processes=4)

    def run(self, data):
        self.pool.map(f, ())



