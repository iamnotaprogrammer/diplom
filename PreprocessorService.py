import sys
import errno
import os
import time
import signal

import tornado.ioloop

from RedisWrapper import RedisWrapper
from Master import Master


REDIS_CHANNELS = ['from_preprocessing_to_sesssion_generator']
Valid_Methods = ["GET" , "POST"]
Valid_Status = ["201", "200"]



def preprocessing(line):
    for valid_method in Valid_Methods:
        if valid_method in line:
            break
    else:
        return None
    for valid_status in Valid_Status:
        if valid_status in line:
            break
    else:
        return None
    return line

def preprocesse_file(name):
    with open(name) as fobj:
        lines = fobj.readlines()
    pool = Master()
    results = [x for x in pool.do(lines, preprocessing) if (x is not None) and (len(x) > 2)]
    with open("./preprocessing/"+ name.split("/")[-1], "w") as file:
        file.write(" \n".join(results))
    return "./preprocessing/"+ name.split("/")[-1]


class PeprocessService(object):
    def __init__(self, redis_connector, workers, method, channel='from_validator_to_preprocessing'):
        self.redis = redis_connector
        self.subscriber = self.redis.new_subscriber(channel)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.workers = workers
        self.method = method

    def loop(self):
        data = next(self.subscriber.listen())
        print(data)
        while True:
            print("Preprocessing start")
            data = next(self.subscriber.listen())
            print(data)
            task = data.get('data').decode('utf8')
            result = list(self.workers.do([task], self.method))[0]
            if not result:
                self.redis.set_value(task, 'preprocesse_file problem')
                print("preprocesse_file problem {} ".format(task))
            self.redis.set_value(result, 'preprocessfile_file')
            for channel in REDIS_CHANNELS:
                print("Preprocessing public {}".format(channel))
                print(channel)
                self.redis.publish_message(result, channel)
            print('complete {0}'.format(result))


    def start_loop(self):
        # self.app._shutting_down = False
        self.ioloop.add_callback(self.loop)
        self.ioloop.start()

    def stop_loop(self, shutdown=False):
        self.ioloop.stop()


if __name__ == '__main__':
    with open("./pids/preprocessing.pid", "w") as fobj:
        fobj.write(str(os.getpid()))
    
    workers = Master()
    redis_connetor = RedisWrapper()
    worker = PeprocessService(redis_connetor, workers, preprocesse_file)
    worker.start_loop()