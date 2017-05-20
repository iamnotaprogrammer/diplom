import psycopg2

settings = {'host':"localhost", 'db_name':"", 'user':"", 'password':""}

class PostgressWrapper(object):
    instance = None
    def __new__(cls):
        if cls.instance:
            return cls.instance
        cls.instance = object.__new__(cls)
        return cls.instance

    def __init__(self, min_con, max_con):
        settings["minconn"] = min_con
        settings["maxconn"] = max_con
        self.con = psycopg2.pool.ThreadedConnectionPool(**settings)

    @property
    def connection(self):
        return self.con.getconn()

    def execute(self, query):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(query)
                cursor.commit()
            except:
                return False
        return True

    