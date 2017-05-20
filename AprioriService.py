import sys
import errno
import os
import time
import signal
import ujson
import tornado.ioloop

from RedisWrapper import RedisWrapper
from Master import Master
from usefull_modules import LogValidator as LV
from PostgressWrapper import PostgressWrapper
import motor
from AprioriApi import AprioriApi
from bson.objectid import ObjectId

# postgress_conn = PostgressWrapper(10, 20)

class AprioriService(object):
    def __init__(self, redis_connector, workers, method, channel='from_session_generator_to_apriori'):
        self.redis = redis_connector
        self.subscriber = self.redis.new_subscriber(channel)
        self.ioloop = tornado.ioloop.IOLoop.instance()
        self.workers = workers
        self.method = method

    def to_mongo(self, data):
        print("to_mongo")
        data = {"data": data}
        client = motor.MotorClient("mongodb://localhost:27017")
        client.db.ass_rules.insert(data)

    def my_callback(self, result, error):
        print("callbak {}, {} ".format(result, error))
        return result

    @tornado.gen.coroutine
    def loop(self):
        print("APRIORI START")
        data = next(self.subscriber.listen())
        print(data)
        while True:
            print("APRIORI START")
            data = next(self.subscriber.listen())
            task = data.get('data').decode('utf8')
            print(data)
            session_id, task = task.split("__")
            print("session_id : {0}  ::: task {1}".format(session_id, task))
            client = motor.MotorClient("mongodb://localhost:27017")
            cursor = client.db.sessions.find({ "_id": ObjectId(session_id)})
            while (yield cursor.fetch_next):
                sessions = cursor.next_object()
            sessions = sessions["data"]
            print("./jsons/" + str(task))
            app = AprioriApi("./jsons/" + str(task), sessions, 1, 0)
            app.first_step()
            app.second_step()
            data = {"data": ujson.dumps(app.associate_rules())}
            client = motor.MotorClient("mongodb://localhost:27017")
            result = yield client.db.ass_rules.insert(data)
            if not result:
                self.redis.set_value(task, 'apriori problem')
                print("apriori problem {} ".format(task))
            self.redis.set_value(task, 'Done')
            print("SET VALUE {} : {}".format(task, 'Done'))
            print('Apriori complete {0}'.format(task))

    def start_loop(self):
        # self.app._shutting_down = False
        self.ioloop.add_callback(self.loop)
        self.ioloop.start()

    def stop_loop(self, shutdown=False):
        self.ioloop.stop()


if __name__ == '__main__':
    with open("./pids/apriory.pid", "w") as fobj:
        fobj.write(str(os.getpid()))

    workers = Master()
    redis_connctor = RedisWrapper()
    worker = AprioriService(redis_connctor, workers, None)
    worker.start_loop()