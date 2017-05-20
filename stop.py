
import os
import signal
for file in os.listdir("./pids/"):
    with open("./pids/" + file) as fobj:
        pid = int(fobj.read())
        print(pid)
        os.kill(pid, signal.SIGTERM)
    os.remove(file)