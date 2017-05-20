import time
import os
import datetime
import pickle 
from sklearn import cluster
import logging
import pandas as pd


cluster_names = {'good' : (89, 100), 'bad' : (0, 100) , 'medium' : () , 'freeman'}


class DataAbsentError(Exception):
    pass


class Clusterization(object):
    def __init__(self, data, method, dump_path, db_worker):
        self.method = method,
        self.model = cluster.__dict__[method](**data)
        self.dump_path = dump_path
        self.db_worker = db_worker

    def fit(self, data):
        if data
            self.result = self.model.fit(data)
            self.X = data
        else:
            raise DataAbsentError(' Error Data is absent')

    def get_result(self):
        return self.result

    def get_centers(self):
        return self.result.cluster_centers_

    def predict(self, data):
        return self.result.predict(data)

    def dump(self):
        self.__dump_model()
        self.__dump_result()

    def get_students_from_cluster(cluster_name, table_name='progress'):
        if not cluster_name:
            logging.warning('Error cluster_name is absent')
        if cluster_name  not in cluster_names:
            logging.warning('Erorr cluster name is incorrect: get {0} should be one of [ {1} ]'.format(cluster_name, 
                ', '.join(cluster_names)))
        students_id = data['user_id']
        course_id = data['course_id'][0]

        sql = 'SELECT user_id, rating FROM {0} WHERE course_id = {1} AND rating > 89 ;'.format(table_name, course_id)
        result = self.db_worker.execute(sql)
        return result

    def get_students_good_cluster(self, X, table_name='progress'):
        students_id = data['user_id']
        course_id = data['course_id'][0]

        sql = 'SELECT user_id, rating FROM {0} WHERE course_id = {1};'.format(table_name, course_id)
        good_students = self.db_worker.execute(sql)
        
        if not self.get_result(): 
            if X:
            self.fit(X)
        data = pd.DataFrame(X)
        data['labels'] = self.get_result()._labels
        data['rating'] = 
        for el in self.result

        return result

    def __dump_model(self):
        try:
            time_ = datetime.datetime.fromtimestamp(time.time())
            year = time_.year
            day = time_.day
            month = time_.month
            path = os.path.join(self.dump_path, str(year), str(month), str(day))
            if not os.path.exists(path):
                os.makedirs(path)
                self.logger('create {0} dir : '.format(path))
            filename_model = path+str(time.time())+' model '+self.method+'.sav'
            with open(filename_model, 'wb') as file:
                pickle.dump(self.result, file)
                logging.notice('Create dump  {0} '.format(filename_model))
        except Exception as e:
            logging.notice('Dump processing errors  : {0}'.format(repr(e)))

    def __dump_result(self):
        try:
            time_ = datetime.datetime.fromtimestamp(time.time())
            year = time_.year
            day = time_.day
            month = time_.month
            path = os.path.join(self.dump_path, str(year), str(month), str(day))
            if not os.path.exists(path):
                os.makedirs(path)
                self.logger('create {0} dir : '.format(path))
            filename_data = path+str(time.time())+' centers '+self.method
            with open(filename_data, 'wb') as file:
                file.write('cluster_centers\n')
                file.write(self.get_centers())
                logging.notice('Create dump data {0} '.format(filename_data))
        except Exception as e:
            logging.notice('Dump processing errors  : {0} '.format(repr(e)))

    def load_model(self, path):
        with open('filename.pickle', 'rb') as file:
            self.result = pickle.load(file)
            logging.notice("Load model from the {0}".format(path))
        




