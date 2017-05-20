
from __future__ import print_function

from std.logger.const import *
import std.logger

from std.context import LoggingContext
from std.fault import Fault

import sys
import os
import signal
import errno

import pysigset

_SigHandlers = {}
_SigPending = []
_SigSetHandled = pysigset.SIGSET()

_WorkerInstance = None

class WorkerLoopInterrupt(BaseException):
    pass

def _SigHandler(sig, frame):
    _SigPending.append(sig)
    if _WorkerInstance:
        _WorkerInstance.loop_interrupt_handler(sig)
    else:
        raise WorkerLoopInterrupt

class Worker(object):
    
    def __init__(self, **ctx_attr):
        self.ctx_attr = ctx_attr
        self.type = self.ctx_attr['name']
        self.socket_dispatcher = self.ctx_attr['socket_dispatcher']
        self.listen = self.ctx_attr['listen']

    def loop_interrupt_handler(self, sig):
        raise WorkerLoopInterrupt

    def install_signal_handlers(self):
        self.set_sig_handler(signal.SIGTERM, lambda: self.sig_TERM_handler())
        self.set_sig_handler(signal.SIGUSR1, lambda: self.sig_USR1_handler())

    def init_resources(self):
        self.Std = LoggingContext(self.ctx_attr['url'], self.ctx_attr['name'])
        self.logger = self.Std._logger

    def release_resources(self):
        pass

    def loop(self):
        pass

    def run(self):
        global _WorkerInstance

        pid = os.fork()

        if pid != 0:
            self.pid = pid
            return

        _WorkerInstance = self

        try:
            closed_sock = self.socket_dispatcher.keys()
            for sock_id in self.listen:
                closed_sock.remove(sock_id)

            for sock_id in closed_sock:
                self.socket_dispatcher[sock_id] = None

            self.install_signal_handlers()

            self.close_logs()
            self.init_resources()

            self.logger(LOG_NOTICE, "Worker started")

            self.GO_ON = True

            while self.GO_ON == True:
                try:
                    pysigset.sigprocmask(pysigset.SIG_UNBLOCK, _SigSetHandled, pysigset.NULL)
                    self.loop()
                    pysigset.sigprocmask(pysigset.SIG_BLOCK, _SigSetHandled, pysigset.NULL)
                except WorkerLoopInterrupt:
                    pass
                except Exception as e:
                    self.logger(LOG_ERROR, "Unexpected error while running worker loop: "+repr(e))
                finally:
                    self.handle_signals()

            self.release_resources()

            self.logger(LOG_NOTICE, "Worker stopped")

        except Exception as e:
            self.logger(LOG_ERROR, "Error running worker: "+repr(e))

        finally:
            self.close_logs()
            sys.exit(0)

    def handle_signals(self):
        global _SigHandlers
        global _SigPending

        while len(_SigPending) > 0:
            try:
                signal = _SigPending[0]
                _SigPending = _SigPending[1:]
                self.logger(LOG_DEBUG, "Handling signal "+repr(signal))
                _SigHandlers[signal]()
            except Exception as e:
                self.logger(LOG_ERROR, "Cannot handle signal "+repr(signal)+": "+repr(e))

    def set_sig_handler(self, sig, handler):
        global _SigHandlers
        global _SigSetHandled

        signal.signal(sig, _SigHandler)
        _SigHandlers[sig] = handler
        pysigset.sigaddset(_SigSetHandled, sig)

    def sig_TERM_handler(self):
        self.logger(LOG_DEBUG, "SIGTERM caught by worker. Terminating")
        self.GO_ON = False
        
    def sig_USR1_handler(self):
        self.close_logs()

    def close_logs(self):
        std.logger.close_logs()



