from pymongo import MongoClient

settings = ['localhost', 27017]

class MongoWrapper(object):
    instance = None
    def __new__(cls):
        if cls.instance:
            return cls.instance
        return object.__new__(cls)

    def __init__(self):
        self._client = MongoClient(*settings)

    @property
    def client(self):
        return self._client

    def insert(self, json_data):
        pass

    def find(self, data):
        pass
        