import multiprocessing
# from  multiprocessing import Pool
from concurrent.futures import ProcessPoolExecutor as Pool
import sys
import os
import random

class Master(object):
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance:
            return cls.instance
        cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, count=None, work=None):
        self.pool = Pool(count)
        self._f = work

    def do(self, data, method=None):
        if not hasattr(method, '__call__'):
            try:
                raise Exception('{}'.format(sys._getframe().f_code.co_name))
            except:
                raise Exception("{} {} {} {}".format(sys._getframe().f_code.co_name, *sys.exc_info()))
        if not method:
            return self.pool.map(self._f, data)
        return self.pool.map(method, data)

master = Master(multiprocessing.cpu_count())
# with open("./pids/"+ str(random.randint(0, 100)), "w") as fobj :
#     fobj.write(str(os.getpid()))
if __name__ == '__main__':
    master = Master()
    master2 = Master()
    print(master)
    print(master2)