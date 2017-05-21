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
from bson.objectid import ObjectId
import motor
import json
import momoko

import uuid
import logging
logging.basicConfig(filename='./logs/api', level=logging.INFO)

import redis

executor = ThreadPoolExecutor(20)


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
    def add_task_to_channel(self):
        f = self.request.files[list(self.request.files.keys())[0]][0]
        original_fname = str(uuid.uuid4())
        output_file = open("uploads/" + original_fname, 'wb')
        output_file.write(f['body'])
        output_file.close()
        stat_parameters = self.request.body
        self.redis_con.set(stat_parameters+"_parameters", json.dumps(json.loads(self.request.body).get(
                'query_parameters', '')))
        result = "uploads/" + original_fname
        self.redis_con.publish(REDIS_CHANNEL, result)
        self.redis_con.set(result, 'qeued')
        logging.debug(" ADD TASK {0}".format(original_fname))
        return original_fname


class Application(tornado.web.Application):

    def __init__(self):
        handlers = [
            (r"/?", IndexHandler),
            (r"/upload/?", UploadHandler),
            (r"/rules/jsons/(.*)/?", DownloadHandler)
        ]
        redis_settings = {'host': "localhost", 'port': 6379, 'max_connections': 10}

        self.pool = redis.ConnectionPool(**redis_settings)
        self.redis = redis.StrictRedis(connection_pool=self.pool)

        mongo_settings = "mongodb://localhost:27017"
        self.mongo = motor.MotorClient(mongo_settings)

        tornado.web.Application.__init__(self, handlers, debug=True)

class ProjectDataHandler(RedisApi):

    @property
    def mongo(self):
        return self.application.mongo


    def is_valid_client_data(self, data):
        valid_keys = ['parameters_log', 'parameters_stat']
        for key in data:
            if key not in valid_keys:
                raise tornado.web.HTTPError(400)


    # {parameters: [""]}
    def get(self, project_id):
        if len(project_id) < 2:
            raise tornado.web.HTTPError(400)

        cursor = self.mongo.db.project.find({"_id": ObjectId(project_id)})

        data = json.loads(self.request.body, encoding='utf8')
        self.is_valid_data(data)

        parameters_stat = data.get('parameters_stat', '')
        parameters_log = data.get('parameters_log', '')











    # def delete(self):
    #     client =
    #     future = client.db.sessions.insert(data)
    #     result = yield future


class DownloadHandler(RedisApi):

    def get(self, filename):
        logging.debug(filename)
        answer = self.redis_con.get(filename)
        if not answer:
            raise tornado.web.HTTPError(500)
        logging.debug(answer)
        self.set_status(200)
        if answer.decode('utf8').lower() == 'done':
            with open('./jsons/{}'.format(filename)) as f:
                data = f.read()
            logging.debug("data {} ".format(data))
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
        result = yield self.add_task_to_channel()
        if not result:
            raise tornado.web.HTTPError(500)
        response = {'url': r'/rules/jsons/',
                    'request_id': result}
        self.finish(response)


def main():
    logging.debug("START")
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    loop_event = tornado.ioloop.IOLoop.instance()
    loop_event.start()
    logging.debug("STOP")



if __name__ == "__main__":
    main()