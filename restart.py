import os
import signal
for file in os.listdir("./pids"):
    with open("./pids/" + file) as fobj:
        os.kill(int(fobj.read()), signal.SIGTERM)

os.system("./start 1")