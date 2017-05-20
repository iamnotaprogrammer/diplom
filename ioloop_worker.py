
# from std.logger.const import *
# import std.logger

# from std.fault import Fault
# from worker import Worker

import sys
import errno
import os
import time
import signal

import tornado.ioloop

from RedisWrapper import RedisWrapper
from Master import Master


class IOLoopWorker(object):
    def __init__(self, redis_connector, workers, channel='from_api_to_validator'):
        self.redis = redis_connector
        self.subscriber = self.redis.new_subscribe(channel)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.workers = workers

    def loop(self):
        data = next(self.subscriber.listen())
        while True:
            data = next(self.subscriber.listen())
            task = data.get('data').decode('utf8')
            self.workers.do([task])


    def start_loop(self):
        # self.app._shutting_down = False
        self.ioloop.add_callback(self.loop)
        self.ioloop.start()

    def stop_loop(self, shutdown=False):
        self.ioloop.stop()


if __name__ == '__main__':
    workers = Master(10, print)
    redis_connctor = RedisWrapper()
    worker = IOLoopWorker(redis_connctor, workers)
    worker.start_loop()