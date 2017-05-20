import os
import sys
import string
import re



def get_data(line):
    regex = '([\d]{1,3}\.*) - - \[(.*?)\] "(.*?)" (\d+) - "(.*?)" "(.*?)"'
    return re.match(regex, line).groups()


HTTP_METHODS = []



class LogValidator(object):
    """This class implement the log-validator methods """
    @staticmethod
    def validate(line):
        return any([getattr(LogValidator,result)(line) for result in dir(LogValidator) if "check" in result ])

    @staticmethod
    def check_user_agent(line):
        """check user-agent"""
        return True

    @staticmethod
    def check_date(line):
        """check date"""
        return True

    @staticmethod
    def check_Ip(line):
        """check IP"""
        return True

    @staticmethod
    def check_http_method(line):
        """check http method"""
        return True

    @staticmethod
    def check_content_path(line):
        """check content path"""
        return True

    @staticmethod
    def check_content_size(line):
        """check size of content """
        return True

    @staticmethod
    def check_protocol(line):
        """check protocol"""
        return True

    @staticmethod
    def check_code_status(line):
        """check code status"""
        return True

    @staticmethod
    def check_indentification(line):
        """check indentification"""
        return True

    @staticmethod
    def check_auth(line):
        return True

    @staticmethod
    def check_url(line):
        return True