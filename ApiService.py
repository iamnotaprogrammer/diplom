import os.path
import random
import string
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
from tornado.concurrent import run_on_executor
from bson import json_util 

import momoko
import motor
import json

import redis

executor = ThreadPoolExecutor(20)

from  LogParser import LogParser
define("host", default="0.0.0.0", help="run on th given host", type=str)
define("port", default=8000, help="run on the given port", type=int)

store_dir = "upload"

REDIS_CHANNEL = "from_api_to_validator"


class RedisApi(tornado.web.RequestHandler):
    _executor = ThreadPoolExecutor(20)

    @property
    def redis_con(self):
        return self.application.redis

    @run_on_executor(executor="_executor")
    def add_task(self):
        # try:
            f = self.request.files[list(self.request.files.keys())[0]][0]
            print(f)
            file_name = f['filename'].replace(".", "")
            original_fname = ''.join([ random.choice(file_name) for i in file_name])
            # extension = os.path.splitext(original_fname)[1]
            # fname = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(6))
            # final_filename = fname + extension
            final_filename = original_fname
            output_file = open("uploads/" + final_filename, 'wb')
            output_file.write(f['body'])
            output_file.close()
            result = "uploads/" + final_filename
            self.redis_con.publish(REDIS_CHANNEL, result)
            self.redis_con.set(result, 'qeued')
            print(" ADD TASK {0}".format(final_filename))
            return original_fname
        # except:
        #     return None


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/?", IndexHandler),
            (r"/upload/?", UploadHandler),
            (r"/rules/jsons/(.*)/?", DownloadHandler)
        ]
        settings = {'host':"localhost", 'port':6379, 'max_connections':10}
        self.pool = redis.ConnectionPool(**settings)
        self.redis = redis.StrictRedis(connection_pool=self.pool)
        ioloop = tornado.ioloop.IOLoop.instance()
        tornado.web.Application.__init__(self, handlers, debug=True)


class DownloadHandler(RedisApi):

    def get(self, filename):
        print(filename)
        answer = self.redis_con.get(filename)
        if not answer:
            raise tornado.web.HTTPError(500)
        print(answer)
        self.set_status(200)
        if answer.decode('utf8').lower() == 'done':
            with open('./jsons/{}'.format(filename)) as f:
                data = f.read()
            print("data {} ".format(data))
            if len(data) > 2:
                response = {'status':1, 'data':data}
            else:
                response = {'status':0}
            self.finish(response)
        else:
            self.finish({'status':0})


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class UploadHandler(RedisApi):

    @property
    def mongo(self):
        return self.application.mongo

    @property
    def postgres(self):
        return self.application.postgres

    @tornado.gen.coroutine
    def post(self):
        result = yield self.add_task()
        if not result:
            raise tornado.web.HTTPError(500)
        response = {'url': r'/rules/jsons/',
                    'request_id': result}
        self.finish(response)

def main():
    print("START")
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    loop_event = tornado.ioloop.IOLoop.instance()
    loop_event.start()
    print("STOP")


if __name__ == "__main__":

    main()

