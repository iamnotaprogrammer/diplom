from Session import Session, SessionGenerator
from Master import Master
from datetime import datetime
from datetime import time as datetime_time
import re
import requests
from user_agents import parse
import json


GOOGLE_API_KEY = "AIzaSyDO_rIS9vuTxNB_X8dmAaYlMlnGdicGYdc"


# Information about visitors: hosts, top-level domains, countries, states, cities, authenticated users, bots,
# screen resolutions, color depths and languages
# mobiles, computers,
#  OS
# Browsers, operating systems, device types and spiders statistics
# top pages
# top highload
# top users
# Geo Location of user
#
#
def is_sublist(lst1, lst2):
    ls1 = [element for element in lst1 if element in lst2]
    ls2 = [element for element in lst2 if element in lst1]
    return ls1 == ls2


print(datetime_time(6, 0, 0))
regex_time = r':\d{2}:\d{2}:\d{2}'
regex_date = r'\d{2}\/\w{2,3}\/\d{4}'

date = "[07/Mar/2004:16:10:49 -0800]"
print(re.search(regex_date, date).group())
print(datetime.strptime(re.search(regex_time, date).group()[1:], '%H:%M:%S').time())

regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) ?"?([^-\s]?){0,1}"?'

line = '64.242.88.10 - - [07/Mar/2004:16:05:49 -0800] "GET /twiki/bin/edit/Main/Double_bounce_sender?topicparent=Main.ConfigurationVariables HTTP/1.1" 401 12846 "http://ramillion.com/" "Mozilla/5.0 (compatible; U; DataMiner/3.14; +http://ramillion.com)"'
print(re.match(regex, line).groups())

line = '62.65.39.20 - - [27/Feb/2017:04:50:47 +0000] "GET / HTTP/1.1" 200 612 "http://ramillion.com/" "Mozilla/5.0 (compatible; U; DataMiner/3.14; +http://ramillion.com)"'

print(re.match(regex, line).groups())

# ip, date, url, status, size, from_url, user_agent = re.match(regex, line).groups()

print(len(re.match(regex, line).groups()))


# print(ip, date, url, status, size, user_agent)


class SessionStat(Session):
    def __init__(self, log):
        # self.log = log
        # self.user_session, self.user_ip_list = SessionGenerator.generate(log)
        self.stat = {}
        self.erorrs = 0
        self.traffic = 0
        self.stat_devices = {}
        self.stat_browser = {}
        self.stat_os = {}
        self.stat_device_models = {}
        self.user_distribution = {}
        self.pages = {}
        self.urls_from = {}
        self.user_distribution_by_time = {}
        self.statuses = {}
        self.time_distribution = {}

    @classmethod
    def from_json(cls, json_data):
        pass

    def increment_traffic(self, size):
        self.traffic += size

    def get_log_statistic(self):
        with open(self.log, 'r') as fobj:
            for line in fobj:
                try:
                    ip, date, page, status, size, *data = re.match(regex, line).groups()
                    if len(data) == 2:
                        from_url, user_agent = data
                    else:
                        user_agent = data[0]
                    user_agent = parse(user_agent)
                    self.add_to_statistic(ip, date, page, status, size, from_url, user_agent)
                except:
                    self.increment_errors()

        return self.get_json_statistic()

    def get_json_statistic(self):
        answer = {"errors": {"data": self.erorrs},
                  "uniqe_users": {"data": self.uniqe_user()},
                  "location_user": {
                      "data": [['Location', 'Amount'] + [[k, v] for k, v in self.user_distribution.items()]]},
                  "distribution_browser": {
                      "data": [['Browsers', 'Amount'] + [[k, v] for k, v in self.stat_browser.items()]]
                  },
                  "distribution_devices": {
                      "data": [['Devices', 'Amount'] + [[k, v] for k, v in self.stat_devices.items()]]
                  },
                  "distribution_device_models": {
                      "data": [['Models', 'Amount'] + [[k, v] for k, v in self.stat_device_models.items()]]
                  },
                  "distribution_time": {
                      "data": [['Period', 'Amount'] + [[k, v] for k, v in self.time_distribution.items()]]
                  },
                  "top_pages": {
                      "data": [['Pages', 'Count'] + [[k, v] for k, v in self.pages.items()]]
                  },
                  "pages_from": {
                      "data": [['Pages', 'Count'] + [[k, v] for k, v in self.urls_from.items()]]
                  },
                  "statuses": {
                      "data": [["Status", 'Amount'] + [[k, v] for k, v in self.statuses.items()]]
                  }
        }
        return json.dumps(answer)

    def add_to_device_models(self, user_agent):
        self.stat_device_models[user_agent.device.family] = self.stat_devices_models.get(user_agent.device.family,
                                                                                         0) + 1

    def add_to_time_distribution(self, time):
        night_end = datetime_time(6, 0, 0)
        morning_end = datetime_time(12, 0, 0)
        day_end = datetime_time(18, 0, 0)

        if time < night_end:
            self.time_distribution['night'] = self.time_distribution.get('night', 0) + 1
        elif time < morning_end:
            self.time_distribution['morning'] = self.time_distribution.get('morning', 0) + 1
        elif time < day_end:
            self.time_distribution['day'] = self.time_distribution.get('day', 0) + 1
        else:
            self.time_distribution['evening'] = self.time_distribution.get('evening', 0) + 1

    def add_to_devices(self, user_agent):
        if user_agent.is_mobile:
            self.stat_devices['mobile'] = self.stat_devices.get('modile', 0) + 1
        elif user_agent.is_tablet:
            self.stat_devices['tablet'] = self.stat_devices.get('tablet', 0) + 1
        elif user_agent.is_touch_capable:
            self.stat_devices['touch_capable'] = self.stat_devices.get('touch_capable', 0) + 1
        elif user_agent.is_pc:
            self.stat_devices['pc'] = self.stat_devices.get('pc', 0) + 1
        elif user_agent.is_bot:
            self.stat_devices['bot'] = self.stat_devices.get('bot', 0) + 1
        else:
            self.increment_errors()

    def add_to_browsers(self, user_agent):
        key = user_agent.browser.family + user_agent.browser.version_str
        self.stat_browser[key] = self.stat_browser.get(key, 0) + 1

    def add_to_locations(self, ip):
        location = self.get_location_by_ip(ip)
        self.user_distribution[location] = self.user_distribution.get(location, 0) + 1

    def add_to_pages(self, page):
        self.pages[page] = self.pages.get(page, 0) + 1

    def add_to_url_from(self, url_from):
        self.urls_from[url_from] = self.urls_from.get(url_from, 0) + 1

    def add_to_statuses(self, status):
        status = int(status)
        if status >= 400:
            self.statuses['bad_status'] = self.correct_status.get('bad_status', 0) + 1
        else:
            self.statuses['success_status'] = self.correct_status.get('success_status', 0) + 1

    def add_to_statistic(self, ip, date, page, status, size, from_url, user_agent):
        self.add_to_devices(user_agent)
        self.add_to_device_models(user_agent)
        self.add_to_browsers(user_agent)
        self.add_to_locations(ip)
        self.increment_traffic(size)
        self.add_to_pages(page)
        self.add_to_statuses(status)
        self.add_to_url_from(from_url)
        time = datetime.strptime(re.search(regex_time, date).group()[1:], '%H:%M:%S').time()
        self.add_to_time_distribution(time)
        date = re.search(regex_date).group()
        self.add_to_date_distribution(date)

    def increment_errors(self):
        self.erorrs += 1

    def uniqe_user(self):
        return len(self.user_sessions)

    def extract_user_agent(self, line):
        return

    def extract_date(self, line):
        return

    def extract_url(self, line):
        return

    def extract_ip(self, line):
        return

    def extract_ip(self, line):
        return

    def get_location_by_ip(self, ip):
        url = 'https://freegeoip.net/json/{}'.format(ip)
        return requests.get(url=url).text

        # def user_distribution(self):
        #     distribution = {}
        #     for ip in self.user_ip_list:
        #         location = self.get_location_by_ip(ip)['city']
        #         distribution[location] = distribution.get(location, 0) + 1
        #     return distribution


if __name__ == '__main__':
    stat = SessionStat('file')
    print(stat.get_location_by_ip('46.39.248.165'))
