import sys
import errno
import os
import time
import signal

import tornado.ioloop

from RedisWrapper import RedisWrapper
from Master import Master
from usefull_modules import LogValidator as LV
from shutil import copyfile


REDIS_CHANNELS = ['from_validator_to_preprocessing']

def valid_line(line):
    if LV.LogValidator.validate(line):
        return line
    else:
        return None

def validate_file(name):
    with open(name) as fobj:
        lines = fobj.readlines()
    master = Master()
    results = master.do(lines, valid_line)
    print(results)
    print(any(results))
    answer = any(results)
    return answer


class ValidatorService(object):
    def __init__(self, redis_connector, workers, method, channel='from_api_to_validator'):
        self.redis = redis_connector
        self.subscriber = self.redis.new_subscriber(channel)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.workers = workers
        self.method = method

    def loop(self):
        data = next(self.subscriber.listen())
        print(data)
        while True:
            print('VALIDATOR START')
            data = next(self.subscriber.listen())
            print(data)
            task = data.get('data').decode('utf8')
            result = self.workers.do([task], self.method)
            print("VALIDATOR RESULT {0}".format(result))
            if not result:
                self.redis.set_value(task.split("/")[-1], 'file is not valid')
            self.redis.set_value(task, 'valid_file')
            for channel in REDIS_CHANNELS:
                print("VALIDATOR public {}".format(channel))
                print(channel)
                status = self.redis.publish_message("./validate/" + task.split("/")[-1], channel)
                print("VALIDATOR public status {}".format(status))
            print('complete {0}'.format(task))
            with open("./validate/" + task.split("/")[-1], "w") as fobj:
                pass
            copyfile(task, "./validate/" + task.split("/")[-1])


    def start_loop(self):
        # self.app._shutting_down = False
        self.ioloop.add_callback(self.loop)
        self.ioloop.start()

    def stop_loop(self, shutdown=False):
        self.ioloop.stop()


if __name__ == '__main__':
    with open("./pids/validator.pid", "w") as fobj:
        fobj.write(str(os.getpid()))
    workers = Master()
    redis_connctor = RedisWrapper()
    worker = Validator(redis_connctor, workers, validate_file)
    worker.start_loop()