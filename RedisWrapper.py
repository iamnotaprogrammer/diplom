import redis

settings = {'host':"localhost", 'port':6379, 'max_connections':10}

class RedisWrapper(object):
    '''
        RedisWrapper implements the methods which help to use redis
        methods for pub/sub
        methods for control connection
        methods for get/set data
    '''
    instance = None

    def __new__(cls):
        if cls.instance:
            return cls.instance
        cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, max_connections=None):
        if max_connections:
            settings["max_connections"] = max_connections
        self.pool = redis.ConnectionPool(**settings)
        self._connection = redis.StrictRedis(connection_pool=self.pool)

    @property
    def connection(self):
        return self._connection

    @property
    def subscriber(self):
        return self.connection.pubsub()

    def set_value(self, key, value, expire=None):
        con = self.connection
        return con.set(key, value)

    def get_keys(self, pattern):
        return self.connection.keys()

    def get_value(self, key):
        val = self.connection.get(key)
        return val.decode('utf-8')

    def publish_message(self,message, channel):
        try:
            print("channel : {} message {}".format(channel, message))
            print("Publik STATUS {}".format(self.connection.publish(channel, message)))
        except:
            return False
        return True

        
    def new_subscriber(self, channel):
        new_subscriber = self.subscriber
        print("NEW SUSCRIBER {0}".format(channel))
        new_subscriber.subscribe(channel)
        return new_subscriber

master = RedisWrapper()


if __name__ == '__main__':
    r = RedisWrapper()
    assert r.set_value("1", "2")
    assert r.get_value("1") == "2"

