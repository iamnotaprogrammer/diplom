from Session import Session
from usefull_modules import MoodleWorker, Logging

class DataParser(object):
    """class implements data prerocessing"""
    def __init__(self, log, log_format, db_worker=None):
        self.data = log
        self.format = log_format
        self.db_worker = db_worker
    
    def preprocessing_use_table(self, course_name):
        self.log_table = self.db_worker.create_course_log_table(course_name)
        self.data = self.db_worker.get_log(self.log_table)
        self.sessions = self.get_sessions()
        self.min_support = self.min_support * len(self.sessions)/100
        del self.data
    
    def preprocessing_use_memory(self):
            self.log_table = self.db_worker.create_course_log_table(
            self.course_name)
            self.data = self.db_worker.get_log(self.log_table)
            self.sessions = self.get_sessions()
            self.min_support = self.min_support * len(self.sessions)/100
            del self.data

    def get_sessions(self):
        """extract sessions from database log """
        result = []
        temp_dict = {}
        session_time = 6900
        for raw in self.data:
            ip, time_, url = raw
            if temp_dict.get(ip, None) == None:
                temp_dict[ip] = Session(time_, url)
            elif time_ - temp_dict[ip].start > session_time:
                result.append(temp_dict[ip].actions)
                temp_dict[ip] = Session(time_, url)
            else:
                temp_dict[ip].actions.append(url)
        self.sessions = result
        return result