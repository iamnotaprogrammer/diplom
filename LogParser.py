import multiprocessing
import re
from datetime import datetime

class LogParser(object):
    url_pattern =  r"(GET|POST) (.*) HTTP"
    ip_pattern = r"([(\d\.)]+)"
    date_pattern = r"\[(.*?)\]"
    date2_pattern = r"\d{2}/\w{3,4}/\d{4}:\d{2}:\d{2}:\d{2}"
    parse_date_pattern = '%d/%b/%Y:%H:%M:%S'

    @staticmethod
    def extract_data(line):
        try:
            url = re.search(LogParser.url_pattern, line).group().split()[1]
            ip = re.search(LogParser.ip_pattern, line).group()
            date = re.search(LogParser.date_pattern, line).group()
            date = re.search(LogParser.date2_pattern, date).group()
            # datetime_object = datetime.strptime(date, LogParser.parse_date_pattern)
        except:
            print(line)
            ip, date, url = "","",""
        return [date, ip, url]

    @staticmethod
    def parse_data(list_object):
        result = []
        pool = multiprocessing.Pool(10)
        for line in list_object:
            if len(line) > 10:
                data = pool.map(extract_data_parallels, (line,))[0]
                result.append(data)
            else:
                print("invalid strings {}".format(line))
        result = sorted(result, key = lambda x: (datetime.strptime(x[0], LogParser.parse_date_pattern) - datetime.utcfromtimestamp(0)).total_seconds())
        return result

    @staticmethod
    def parse_log(path_to_file):
        result = []
        pool = multiprocessing.Pool(10)
        with open(path_to_file, "r") as fileobj:
            lines = fileobj.readlines()
            for line in lines:
                if len(line) > 10:
                    data = pool.map(extract_data_parallels, (line,))[0]
                    result.append(data)
                else:
                    print("invalid strings {}".format(line))
        result = sorted(result)
        return result

def extract_data_parallels(line):
    return LogParser.extract_data(line)


if __name__ == "__main__":
    print(LogParser.parse_log("./complete/x3vkqm.1"))
