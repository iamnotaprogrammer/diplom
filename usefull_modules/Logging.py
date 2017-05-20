
import os, sys
import logging


class BasicLogging(object):
    def __init__(self, level, format, *args):
        self.level = level
        self.format = format
        self._initArgs(*args)
        self._initLogger()

    def reopen(self):
        self._destroyHandler()
        self._initHandler()

    def _initArgs(self):
        pass

    def _initLogger(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(self.level)
        self.formatter = logging.Formatter(self.format)
        self._initHandler()

    def _initHandler(self):
        self.handler = self._openHandler()
        self.logger.addHandler(self.handler)

    def _openHandler(self):
        handler = logging.StreamHandler()
        handler.setFormatter(self.formatter)
        return handler

    def _destroyHandler(self):
        self.handler.flush()
        self.handler.close()
        self.logger.removeHandler(self.handler)
        del self.handler


class BasicFileLogging(BasicLogging):
    def _initArgs(self, file):
        self.file = file

    def _openHandler(self):
        handler = logging.FileHandler(self.file)
        handler.setFormatter(self.formatter)
        return handler


if __name__ == '__main__':
    level = logging.DEBUG
    format = '%(asctime)s\t%(process)d\t%(levelname)s\t%(message)s'

    if len(sys.argv) > 1:
        file = sys.argv[1]
        basicLogging = BasicFileLogging(level, format, file)
    else:
        basicLogging = BasicLogging(level, format)

    logging.debug("1")

    if len(sys.argv) > 1:
        file = sys.argv[1]
        os.rename(file, '%s.bak' % file)

    logging.debug("2")

    basicLogging.reopen()

    logging.debug("3")

