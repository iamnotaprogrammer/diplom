import os
from AprioriService import AprioriService
from Master import Master
from PreprocessorService import PeprocessService
from RedisWrapper import RedisWrapper
from Session import SessionGenerator as SessionGeneratorWorker
from SessionGeneratorService import SessionGeneratorService
from usefull_modules import LogValidator as LV
import ApiService

from Validator import ValidatorService


########################################TODO#################################
def valid_line(line):
    if LV.LogValidator.validate(line):
        return line
    else:
        return None

def validate_file(name):
    with open(name) as fobj:
        lines = fobj.readlines()
    master = Master()
    results = master.do(lines, valid_line)
    print(results)
    print(any(results))
    answer = any(results)
    return answer

########################################TODO#################################
Valid_Methods = ["GET", "POST"]
Valid_Status = ["201", "200"]


def preprocessing(line):
    for valid_method in Valid_Methods:
        if valid_method in line:
            break
    else:
        return None
    for valid_status in Valid_Status:
        if valid_status in line:
            break
    else:
        return None
    return line


def preprocesse_file(name):
    with open(name) as fobj:
        lines = fobj.readlines()
    pool = Master()
    results = [x for x in pool.do(lines, preprocessing) if (x is not None) and (len(x) > 2)]
    with open("./preprocessing/" + name.split("/")[-1], "w") as file:
        file.write(" \n".join(results))
    return "./preprocessing/" + name.split("/")[-1]


class ServiceVisitor(object):
    def loop(self, name):
        getattr(self, 'loop_' + name)()

    def loop_Apriori(self):

        with open("./pids/apriory.pid", "w") as fobj:
            fobj.write(str(os.getpid()))

        workers = Master()
        redis_connector = RedisWrapper()
        worker = AprioriService(redis_connector, workers, None)
        worker.start_loop()


    def loop_SessionGenerator(self):
        with open("./pids/sessions.pid", "w") as fobj:
            fobj.write(str(os.getpid()))
        workers = Master()
        redis_connector = RedisWrapper()
        worker = SessionGeneratorService(redis_connector, workers, SessionGeneratorWorker().generate)
        worker.start_loop()


    def loop_Preprocessor(self):
        with open("./pids/preprocessing.pid", "w") as fobj:
            fobj.write(str(os.getpid()))
        workers = Master()
        redis_connector = RedisWrapper()
        worker = PeprocessService(redis_connector, workers, preprocesse_file)
        worker.start_loop()


    def loop_Validator(self):
        with open("./pids/validator.pid", "w") as fobj:
            fobj.write(str(os.getpid()))
        workers = Master()
        redis_connector = RedisWrapper()
        worker = ValidatorService(redis_connector, workers, validate_file)
        worker.start_loop()

    def loop_Api(self):
        print("START")
        with open("./pids/api.pid", "w") as fobj:
            fobj.write(str(os.getpid()))
        ApiService.main()
        print("STOP")


VISITOR = ServiceVisitor()

class Service(object):
    def loop(self):
        VISITOR.loop(type(self).__name__)


class Validator(Service):
    pass


class SessionGenerator(Service):
    pass


class Apriori(Service):
    pass


class Preprocessor(Service):
    pass

class Api(Service):
    pass

if __name__ == '__main__':
    visitor = ServiceVisitor()
    temp = SessionGenerator()
    temp.loop()