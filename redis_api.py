import os.path
import random
import string
import time
import os

from  multiprocessing import Pool
import multiprocessing

import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
from tornado.options import define, options

from concurrent.futures import ThreadPoolExecutor 
from usefull_modules import log_validation
from usefull_modules import Logging
from tornado.concurrent import run_on_executor
from bson import json_util 

import momoko
import motor
import json

from RedisWrapper import RedisWrapper
from  LogParser import LogParser

define("port", default=8888, help="run on the given port", type=int)
REDIS_CHANNELS = ["diplom"] 


class BaseReqHandler(tornado.web.RequestHandler):
    def initialize(self, **kwarg):
        # self.logger = kwarg['logger']
        pass

    def compute_etag(self):
        return None

class RedisApi(BaseReqHandler):

    @property
    def redis_con(self):
        return self.application.redis

    def publish_task(self, channel, client):
        self.redis_con.publish(channel, client)

class StatusApi(RedisApi):
   def get(self, task_id):
        if len(task_id) < 1:
            raise tornado.web.HTTPError(400)
        for key in self.redis_con.scan_iter(match='{0}*'.format(str(task_id))):
            if self.redis_con.get(key).lower() == 'queued':
                self.write('Queued')
                self.finish()
                return
        else:
            self.write("Done")
            self.finish()
            return
        raise tornado.web.HTTPError(404)


class Publisher(RedisApi):

    def post(self, client_name):
        if len(client_name) < 1:
            raise tornado.web.HTTPError(403)
        try:
            task_id = client_name +"_" +str(time.time()).replace('.', '')
            for channel in REDIS_CHANNELS:
                self.publish_task(channel, task_id)
                self.redis_con.set(task_id + "_" + channel, 'queued')
            self.write(task_id)
        except Exception as e:
            raise tornado.web.HTTPError(500)


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/add/", Publisher),
            (r"/status/(.*)", StatusApi)
        ]
        tornado.web.Application.__init__(self, handlers, debug=True)

def main():
    app = Application()
    app.redis = RedisWrapper()
    http_server = tornado.httpserver.HTTPServer()
    http_server.listen(options.port)
    loop_event = tornado.ioloop.IOLoop.instance()
    loop_event.start()


if __name__ == "__main__":
    main()
