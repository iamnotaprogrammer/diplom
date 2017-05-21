import re
from datetime import datetime

line_pattern = re.compile(r'(\d{1,3}\.\d{1,3}.\d{1,3}.\d{1,3}) - - \[(.*)\] \"(\w{3,6}.* \w{0,4}/\d\.\d)\"')


class Session(object):
    """class implements user session"""

    def __init__(self, start, action):
        self.start = start
        self.actions = []
        self.actions.append(action)

    def append(self, iter_object):
        "add elements to actions list"
        for el in iter_object:
            self.actions.append(el)


class SessionGenerator(object):
    @staticmethod
    def generate(file_path):
        """extract sessions from web log """
        print("generator method()")
        result = []
        userIp_session = {}
        session_time = 300
        with open(file_path) as file_:
            for line in file_:
                ip_time_url = re.search(line_pattern, line)
                if ip_time_url is None:
                    continue
                ip, time_, url = ip_time_url.groups()[0], datetime.strptime(ip_time_url.groups()[1].split(" ")[0], '%d/%b/%Y:%H:%M:%S'), \
                                 ip_time_url.groups()[2].split(" ")[1]
                if userIp_session.get(ip, None) == None:
                    userIp_session[ip] = Session(time_, url)
                elif (time_ - userIp_session[ip].start).total_seconds() > session_time:
                    result.append(userIp_session[ip].actions)
                    userIp_session[ip] = Session(time_, url)
                else:
                    userIp_session[ip].actions.append(url)

                # print("pattern : {}  line :{} ".format(re.search(line_pattern, line), line))
                # print((time_ - userIp_session.get(ip, Session(datetime.now(),
                #                                               r"http://localhost:80/")).start).total_seconds())
            return result, list(userIp_session.keys())


if __name__ == "__main__":
    nlog = r'192.168.1.12 - - [23/Jun/2015:11:10:57 +0000] "GET /entry/how-create-configure-free-ssl-certificate-using-django-and-pythonanywhere HTTP/1.1" 302 5 "http://www.reddit.com/r/Python/" "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.18 Safari/537.36" "192.168.1.12"'
    nlog = r'185.169.229.226 - - [27/Feb/2017:05:08:41 +0000] "GET / HTTP/1.0" 200 737 "-" "masscan/1.0 (https://github.com/robertdavidgraham/masscan)"'
    nlog = r'62.65.39.20 - - [27/Feb/2017:04:50:47 +0000] "GET / HTTP/1.1" 200 612 "http://ramillion.com/" "Mozilla/5.0 (compatible; U; DataMiner/3.14; +http://ramillion.com)"'
    r = re.search(line_pattern, nlog)
    http_x_real_ip = r.groups()[0]
    print(http_x_real_ip)
    time_local = r.groups()[1]
    print(time_local)
    request = r.groups()[2]
    print(request)
    # status = r.groups()[3]
    # print(status)
    # body_bytes_sent = r.groups()[4]
    # print(body_bytes_sent)
    # http_referer = r.groups()[5]
    # print(http_referer)
    # http_user_agent = r.groups()[6]
    # print(http_user_agent)
    # http_x_forwarded_for = r.groups()[7]
    # print(http_x_forwarded_for)
