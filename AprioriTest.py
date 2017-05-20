from algorithms import Apriori

import logging
import os
import sys
import time
from collections import namedtuple
from itertools import chain, combinations
# import pandas as pd
import pprint as pp
import ujson

sys.path.append('/home/ivan/diplom/cognitive_mapper/api/data_mining_app')

from algorithm import Algorithm
from usefull_modules import MoodleWorker, OurLogging
from Session import Session

class AprioriApi(Algorithm):
    """class is support data mining algorithm Apriory"""

    def __init__(self,
                 min_support,
                 min_confidence,
                 **kwargs
                 ):
        # self.db_worker = db_worker
        # self.table_name = kwargs['table_name']
        self.course_name = kwargs['course_name']

        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequently_itemsets = dict()

    # def start_preprocessing(self):
    #     self.log_table = self.db_worker.create_course_log_table(
    #         self.course_name)
    #     self.data = self.db_worker.get_log(self.log_table)
    #     self.sessions = self.get_sessions()
    #     self.min_support = self.min_support * len(self.sessions)/100
    #     del self.data

    # def get_sessions(self):
    #     """extract sessions from database log """
    #     result = []
    #     temp_dict = {}
    #     session_time = 6900
    #     for raw in self.data:
    #         ip, time_, url = raw
    #         if temp_dict.get(ip, None) == None:
    #             temp_dict[ip] = Session(time_, url)
    #         elif time_ - temp_dict[ip].start > session_time:
    #             result.append(temp_dict[ip].actions)
    #             temp_dict[ip] = Session(time_, url)
    #         else:
    #             temp_dict[ip].actions.append(url)
    #     self.sessions = result
    #     return result

    def support(self, seq):
        """count support for seq """
        if len(seq) == 0:
            return 0
        support_ = 0
        t = 0
        for raw in self.sessions:
            for el in seq:
                if el in raw:
                    t += 1
            else:
                if t == len(seq):
                    support_ += 1
                t = 0
        return support_

    def get_items_sup(self):
        """ get dict { item : support}  where support great then min_sup"""
        self.items_supp = {}
        for item in chain(*self.sessions):
            self.items_supp[(item, )] = self.items_supp.get((item,), 0) + 1
        for item in list(self.items_supp.keys()):
            if self.items_supp[item] < self.min_support:
                self.items_supp.pop(item)
        return self.items_supp

    def get_items_sup_test(self):
        self.items_supp = {}
        for el in chain(*self.sessions):
            self.items_supp[(el,)] = self.items_supp.get((el,), 0) + 1
        return self.items_supp

    def start_preprocessing_test(self):
        # self.sessions = (
        #     ('bread', 'milk', 'печенье'),
        #     ('milk', 'сметана'),
        #     ('milk', 'bread', 'сметана', 'печенье'),
        #     ('meal', 'сметана'),
        #     ('bread', 'milk', 'печенье', 'сметана'),
        #     ('sweets',),
        # )
        self.sessions = (
            ('bread', 'milk', 'cookies'),
            ('milk', 'milk2'),
            ('milk', 'bread', 'porriege', 'cookies'),
            ('meal', 'porriege'),
            ('bread', 'milk', 'cookies', 'porriege'),
            ('sweets',),
        )

    def first_step_test(self):
        print('Run')
        self.start_preprocessing_test()
        self.get_items_sup_test()


    def first_step(self):
        """ first step of Apriory"""
        self.start_preprocessing()
        self.get_items_sup()

    def second_step(self):
        """second step of Apriory"""
        i = 0
        self.frequently_itemsets.update(self.items_supp)
        while True:
            print(self.frequently_itemsets)
            self.generate_new_items()
            # self.advance_generate_new_items()
            if len(self.next_items) == 0:
                break
            self.update_frequency_itemset()
            # logging.info('Iteration {0}  end'.format(i))
            i += 1

    def generate_new_items(self):
        """generate new frequency items length length i + 1"""
        if not hasattr(self, 'current_items'):
            self.current_items = list(self.items_supp.keys())
            self.next_items = set()
        else:
            self.current_items = self.next_items
            self.next_items = set()
        for seq in self.current_items:
            for el_ in self.items_supp:
                if el_[0] not in seq:
                    t = (*seq, el_[0])
                    # logging.info(t)
                    self.next_items.add(frozenset(t))
                else:
                    continue
        return self.next_items

    def update_frequency_itemset(self):
        for el in self.next_items:
            support_ = self.support(el)
            if support_ >= self.min_support:
                self.frequently_itemsets[el] = support_
            # else:
        return self.frequently_itemsets
    
    def to_json(self, result):
        name = '{0}.{1}'.format(self.course_name, time.time())
        with open(name, 'w') as f:
            ujson.dump(result,f)
    
    def advance_generate_new_items(self):
        if not hasattr(self, 'current_items'):
            self.current_items = list(self.items_supp.keys())
            self.next_items = set()
        else:
            self.current_items = list(self.next_items)
            self.next_items = set()
        l = len(self.current_items)
        # for i in range(l):
        #     for j in range(i,l):
        #         for el in self.current_items[i]:
        # for item in self.current_items:
        #     for item_ in self.current_items:
        #         if item != item_:
        #             for el in item:
        #                 if el not in 
        #             if el not in self.current_items[j]:
        #                 t = frozenset((*self.current_items[j], el))
        #                 sup = self.support(t)
        #                 if sup >= self.min_support:
        #                     self.next_items.add(t)
        #                     self.frequently_itemsets[t] = sup
        return self.next_items
                    
    
    def advance_update_frequency_itemset(self):
        for el in self.next_items:
            support_ = self.support(el)
            if support_ >= self.min_support:
                self.frequently_itemsets[el] = support_
            else:
                self.next_items.remove(el)
        return self.frequently_itemsets
        

    def associate_rules(self):
        result = {}
        for seq in self.frequently_itemsets:
            if len(seq) == 0:
                continue
            left = []
            temp = list(seq)
            for i in range(len(seq)-1):
                left.append(temp.pop())
                try:
                    answer = self.frequently_itemsets.get(frozenset(left), self.support(left))\
                    / self.frequently_itemsets.get(frozenset(temp), self.support(temp))
                    if answer * 100 > self.min_confidence:
                        result[(tuple(left),tuple(temp))] = answer
                except ZeroDivisionError:
                    continue
                # else:
                #     # logging.info('{0} -> {1} with {2}'.format(left, temp, answer*100))
        self.to_json(result)
        return result
        


if __name__ == '__main__':
    level = logging.DEBUG
    format = '%(asctime)s\t%(process)d\t%(levelname)s\t%(message)s'

    # basicLogging = OurLogging.BasicLogging(level, format)
    # logging.debug("Start")

    data = {
        "host": 'localhost',
        "user": 'root',
        "passwd": 'smirnov95',
        "db": 'uir',
        "database": 'mysql',
        "charset": 'utf8',

    }
    mdb = MoodleWorker.MoodleWorker(**data)
    course = {
        'course_name': 'Менеджмент_б',
    }
    app = Apriory(mdb, 0, 0, **course)
    # logging.info(app.first_step_test())
    # logging.info(app.second_step())
    # logging.info(app.associate_rules())
    # app.first_step()
    app.first_step_test()
    app.second_step()
    print(app.associate_rules())
    # logging.info(app.first_step())
    # logging.info(app.second_step())
    # pp.pprint(app.associate_rules())
    # app.db_worker.delete_table(app.log_table)
   
