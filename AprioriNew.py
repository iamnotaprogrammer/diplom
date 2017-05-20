class Apriori(object):
    def __init__(self, support, confidence, sessions):
        self.support = support
        self.confidence = confidence
        self.sessions = sessions

    def support_item(self, items):
        if len(items) == 0:
            return 0
        result = 0
        for el in self.sessions:
            if items == el:
                result += 1
            elif len(items) > len(el):
                continue
            else:
                for element in items:
                    if element not in el:
                        break
                else:
                    result += 1

    def find_uniq_elements(self):
        el_count_dict = dict()
        for session in self.sessions:
            for el in session:
                el_count_dict[el] = el_count_dict.get(el, 0) + 1

        for k, v in el_count_dict.items():
            if v < self.support:
                del k
        
    