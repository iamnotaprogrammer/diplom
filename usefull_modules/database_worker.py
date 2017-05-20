import sys
import pymysql
import logging
# import psycopg2

class DataBaseSupportErorr(Exception):
    pass


class DbConnector(object):
    def __init__(self, **kwargs):

        if kwargs.pop('database') == 'mysql':
            self.type = pymysql
        # elif kwargs['database'] == 'postgres':
        #     self.connection = psycopg2
        else:
             raise DataBaseSupportErorr('This module cannot support this database {0} (only mysql | postgres)'.format(kwargs['database']))
        self.data = kwargs
    def __connect(self):
        self.connection = self.type.connect(**self.data)
        logging.debug('Connection open')

    def __close(self):
        if self.connection:
            self.connection.close()
            logging.debug('Connection close')
            return True
        logging.warning("Error close connection which doesn't exist")

    def execute(self, query):
        result = None
        self.__connect()
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(query)
                result = cursor.fetchall()
        except Exception as e:
            print(query)
            logging.warning("Db connection problems {0} ".format(repr(e)))
            self.__close()
        return result


