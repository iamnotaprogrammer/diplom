import sys
import os
import time
sys.path.append(os.path.dirname(__file__))
from database_worker import DbConnector
import pymysql


class MoodleSchemaError(Exception):
    pass

class MoodleDataBaseError(Exception):
    pass


class MoodleWorker(DbConnector):
    """class for work with moodle database"""

    def __init__(self, **kwargs):
        super(MoodleWorker, self).__init__(**kwargs)
        tables_list = ['mdl_course', 'mdl_course_categories', 'mdl_log',
                       'mdl_logstore_standard_log']
        # self.mdl_course = kwargs['mdl_course']
        # self.mdl_course_categories = kwargs['mdl_course_categories']
        # self.mdl_log = kwargs['mdl_log']
        # self.mdl_logstore_standard_log = kwargs['mdl_logstore_standard_log']
        self.mdl_course = 'mdl_course'
        self.mdl_course_categories = 'mdl_course_categories'
        self.mdl_log = 'mdl_log'
        self.mdl_logstore_standard_log = 'mdl_logstore_standard_log'
        # change after testing
        result = self.execute('show tables FROM uir;')
        for table in tables_list:
            for el in result:
                if table == el[0]:
                    break
            else:
                raise MoodleSchemaError('table {0} is absent'.format(table))

    def get_course_id(self, shortname, fullname):
        query = 'SELECT id FROM {0} where shortname= "{1}" or fullname = "{2}"'.format(
            self.mdl_course, shortname, fullname)
        return self.execute(query)

    def create_course_log_table(self, shortname='', fullname=''):
        """"""
        id_course = self.get_course_id(shortname, fullname)[0][0]
        table_name = 'temp_table' + str(int(time.time()))
        query = 'CREATE TABLE {0} AS (SELECT * FROM {1} WHERE courseid = {2} ) ; '.format(
            table_name, self.mdl_logstore_standard_log, id_course
        )
        if len(self.execute(query)) == 0:
            return table_name
        else:
            raise MoodleDataBaseError('cannot create table')

        

    def delete_table(self, log_table):
        query = "Drop table {0} ;".format(log_table)
        return  self.execute(query)

    def get_log(self, log_table):
        """"""
        columns = ['ip', 'timecreated', 'eventname']
        query = "SELECT {0} FROM {1};".format(" , ".join(columns), log_table)
        return self.execute(query)
        
    def get_items(self, table, column="eventname"):
        query = "SELECT DISTINCT {0} from {1}".format(column, table)
        return self.execute(query)


if __name__ == '__main__':
    data = {
        "host": 'localhost',
        "user": 'root',
        "passwd": 'smirnov95',
        "db": 'uir',
        "database": 'mysql'
    }

    mdb = MoodleWorker(**data)
