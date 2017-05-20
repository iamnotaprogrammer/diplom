import os
import sys
import getpass
from subprocess import Popen, PIPE
import Services
import signal

VALID_COMMANDS = ['start', 'stop', 'restart', 'reload']
apriori = Services.Apriori()
validator = Services.Validator()
preprocessor = Services.Preprocessor()
sessiongenerator = Services.SessionGenerator()

api = Services.Api()
services = [validator, preprocessor, sessiongenerator, apriori, api]

# def child(services=services):


def start():

    Process = Popen(["sudo service redis start"], shell=True, stdout=PIPE, stdin=PIPE,
                    stderr=PIPE)
    print("redis {} ".format(Process.communicate()))
    Process = Popen(["sudo service postgresql start"], shell=True, stdout=PIPE, stdin=PIPE,
                    stderr=PIPE)
    print("postgresql {} ".format(Process.communicate()))
    Process = Popen(["sudo service mongodb start"], shell=True, stdout=PIPE, stdin=PIPE,
                    stderr=PIPE)
    print("mongo {} ".format(Process.communicate()))
    for i in range(len(services)):
        current = services.pop()
        pid = os.fork()
        if pid == 0:
            print('service start')
            current.loop()
            break
        else:
            print(os.getpid())


def restart():
    stop()
    start()

def stop():
    for file in os.listdir("./pids/"):
        with open("./pids/" + file) as fobj:
            pid = int(fobj.read())
            print(pid)
            os.kill(pid, signal.SIGTERM)
        os.remove(file)

def reload():
    pass

COMMANDS_DICT = {'start': start, 'stop': stop,'restart': restart, 'reload': reload}

if __name__ == '__main__':
    if getpass.getuser() != "root":
        print('Please, use sudo')
        sys.exit(1)
    command = sys.argv[1]

    if command in VALID_COMMANDS:
        COMMANDS_DICT[command]()
    else:
        print('invalid commands')
        print('availible commands {}'.format(VALID_COMMANDS))
        sys.exit(1)
