import logging
import os
import sys
import time
from collections import namedtuple
from itertools import chain, combinations

import json
import random

class AprioriApi(object):
    """class is support data mining algorithm Apriory"""

    def __init__(self,
                 name,
                 sessions,
                 min_support,
                 min_confidence
                 ):
        self.min_support = min_support
        self.min_confidence = min_confidence
        self.frequently_itemsets = dict()
        self.sessions = sessions
        self.name = name
    
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

    def first_step(self):
        """ first step of Apriori"""
        self.get_items_sup()

    def get_items_sup(self):
        """ get dict { item : support}  where support great then min_sup"""
        self.items_supp = {}
        for item in chain(*self.sessions):
            self.items_supp[(item,)] = self.items_supp.get((item,), 0) + 1

        for item in list(self.items_supp.keys()):
            if self.items_supp[item] < self.min_support:
                del self.items_supp[item]
        return self.items_supp

    def second_step(self):
        """second step of Apriori"""
        print('second step')
        i = 0
        self.frequently_itemsets.update(self.items_supp)
        print('here')
        while True:
            # print("self.frequently_itemsets {} : i {} ".format(self.frequently_itemsets, i))
            self.generate_new_items()
            self.update_frequency_itemset()
            if len(self.next_items) == 0 or i == 2:
                print('break')
                break
            i += 1

    # def support(self, items):
    #     """count support for seq """
    #     if len(items) == 0:
    #         return 0
    #     result = 0
    #     for el in self.sessions:
    #         if items == el:
    #             result += 1
    #         elif len(items) > len(el):
    #             continue
    #         else:
    #             for element in items:
    #                 if element not in el:
    #                     break
    #             else:
    #                 result += 1
    #     return result

    def generate_new_items(self):
        """generate new frequency items length length i + 1"""
        if not hasattr(self, 'current_items'):
            self.current_items = list(self.items_supp.keys())
            self.next_items = set()
        else:
            self.current_items = self.next_items
            self.next_items = set()
        print('start generate')
        print(len(self.current_items) * len(self.items_supp))
        for seq in self.current_items:
            for el_ in self.items_supp:
                if el_[0] not in seq:
                    # t = (*seq, el_[0])
                    t = tuple(seq) + el_
                    if list(t) in self.sessions:
                        self.next_items.add(frozenset(t))
        return self.next_items

    def update_frequency_itemset(self):
        for el in self.next_items:
            support_ = self.support(el)
            if support_ >= self.min_support:
                self.frequently_itemsets[el] = support_
        return self.frequently_itemsets

    def to_json(self):
        if not self.result:
            raise Exception('cannot create json file')
        json_valid = {'nodes': set(), 'edges': []}
        i = 0
        while i < random.randint(10, 30):
            try:
                i += 1
                print('LOOOOOOOOP')
                temp = []
                node_, node2_ = random.sample(list(self.result.keys()), 2)
                if len(node_) > 1:
                    temp = list(node_)
                    for el in temp:
                        json_valid['nodes'].add(el)
                    temp.append(self.result[node_])
                    json_valid['edges'].append(temp)
                    continue
                elif len(node2_) > 1:
                    temp = list(node2_)
                    for el in temp:
                        json_valid['nodes'].add(el)
                    temp.append(self.result[node2_])
                    json_valid['edges'].append(temp)
                    continue
                node, node2 = node_[0], node2_[0]
                temp.append(node)
                temp.append(node2)
                temp.append(self.result[node_] + self.result[node2_])
                json_valid['nodes'].add(node)
                json_valid['nodes'].add(node2)
                json_valid['edges'].append(temp)
            except Exception as e:
                print(e)
        else:
            print('GOOd end len edges {} len nodes {} '.format(len(json_valid['edges']), len(json_valid['nodes'])))
        json_valid['nodes'] = list(json_valid['nodes'])
        with open(self.name, 'w') as f:
            json.dump(json_valid, f)
        print("JSON {} created".format(self.name))


    def advance_update_frequency_itemset(self):
        for el in self.next_items:
            support_ = self.support(el)
            if support_ >= self.min_support:
                self.frequently_itemsets[el] = support_
            else:
                self.next_items.remove(el)
        return self.frequently_itemsets


    def associate_rules(self):
        print("start ass rules")
        print(self.frequently_itemsets)
        result = {}
        for el in self.frequently_itemsets:
            result[el] = self.support(el)
        self.result = result
        self.to_json()
        return result

    # def associate_rules(self):
    #     print("start ass rules")
    #     print(self.frequently_itemsets)
    #     result = {}
    #     for seq in self.frequently_itemsets:
    #         if len(seq) == 0:
    #             continue
    #         left = []
    #         temp = list(seq)
    #         for i in range(len(seq)-1):
    #             left.append(temp.pop())
    #             try:
    #                 answer = self.frequently_itemsets.get(frozenset(left), self.support(left))\
    #                 / self.frequently_itemsets.get(frozenset(temp), self.support(temp))
    #                 if answer * 100 > self.min_confidence:
    #                     result[(tuple(left), tuple(temp))] = answer
    #             except ZeroDivisionError:
    #                 print('errorrrrrrrrrrrrr ')
    #                 continue
    #     print('EEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEEE')
    #     print(result)
    #     self.result = result
    #     self.to_json()
    #     return result
        


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
    session = (
            ('bread', 'milk', 'cookies'),
            ('milk', 'milk2'),
            ('milk', 'bread', 'porriege', 'cookies'),
            ('meal', 'porriege'),
            ('bread', 'milk', 'cookies', 'porriege'),
            ('sweets',),
    )
    app = AprioriApi("temp", session, 0, 0)
    app.first_step()
    app.second_step()
    print(app.associate_rules())

