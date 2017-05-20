import sys
import errno
import os
import time
import signal

import tornado.ioloop
import tornado
import tornado.web
from RedisWrapper import RedisWrapper
from Master import Master
from usefull_modules import LogValidator as LV

REDIS_CHANNELS = ['from_session_generator_to_apriori']


from Session import SessionGenerator

import motor
from bson.objectid import ObjectId
import json
from tornado.concurrent import Future

class SessionGeneratorService(object):
    def __init__(self, redis_connector, workers, method, channel='from_preprocessing_to_sesssion_generator'):
        self.redis = redis_connector
        self.subscriber = self.redis.new_subscriber(channel)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.workers = workers
        self.method = method
    
    # @tornado.gen.engine
    # def to_mongo(self, data, callback=None):
    #     print()
    #     print("to_mongo Session Generator data {}".format(data))
    #     print()
    #     data = {"data": data}
    #     client = motor.MotorClient("mongodb://localhost:27017")
    #     result = yield tornado.gen.Task(client.db.sessions.insert, data, self.my_callback)
    #     return result

    @tornado.gen.coroutine
    def my_callback(self, result):
        print("callbak {}, ".format(result))
        for channel in REDIS_CHANNELS:
            print("SESSION GENERATOR public {}".format(channel))
            print(channel)
            print("callback {}".format(self.task))
            status = self.redis.publish_message(str(result) + "__" + self.task.split("/")[-1], channel)
            self.redis.set_value(self.task.split("/")[-1], "apriori is searching rules")
            print("SESSION GENERATOR public status {}".format(status))
        print('complete {0} sessions'.format(self.task))
        return result

    @tornado.gen.coroutine
    def my_loop(self):
        print("SESSION ___ START")
        data = next(self.subscriber.listen())
        print(data)
        while True:
            print("SESSION GENERATOR START")
            data = next(self.subscriber.listen())
            print(data)
            self.task = data.get('data').decode('utf8')
            print()
            print("session tast : {} ".format(self.task))
            print()
            result = next(self.workers.do([self.task], self.method))
            print("Result SESSIONS {} ".format(result))
            if not result:
                self.redis.set_value(self.task, 'session_generator_problem')
                print("session_generator_problem problem {} ".format(self.task))
            self.redis.set_value(self.task, 'session_generating')
            data = {"data": result}
            client = motor.MotorClient("mongodb://localhost:27017")
            future = client.db.sessions.insert(data)
            result = yield future
            self.my_callback(result)



    # def loop(self):
    #     print("SESSION ___ START")
    #     data = next(self.subscriber.listen())
    #     print("SESSION ___ START")
    #     print(data)
    #     while True:
    #         print("SESSION GENERATOR START")
    #         data = next(self.subscriber.listen())
    #         print(data)
    #         self.task = data.get('data').decode('utf8')
    #         print("session tast : {} ".format(self.task))
    #         result = next(self.workers.do([self.task], self.method))
    #         print("Result SESSIONS {} ".format(result))
    #         if not result:
    #             self.redis.set_value(self.task, 'session_generator_problem')
    #             print("session_generator_problem problem {} ".format(self.task))
    #         self.redis.set_value(self.task, 'session_generating')
    #         answer = yield self.to_mongo(result)
    #         print(answer)

    def start_loop(self):
        # self.app._shutting_down = False
        self.ioloop.add_callback(self.my_loop)
        self.ioloop.start()

    def stop_loop(self, shutdown=False):
        self.ioloop.stop()


if __name__ == '__main__':
    with open("./pids/sessions.pid", "w") as fobj:
        fobj.write(str(os.getpid()))
    workers = Master()
    redis_connctor = RedisWrapper()
    worker = SessionGeneratorService(redis_connctor, workers, SessionGenerator.generate)
    worker.start_loop()
