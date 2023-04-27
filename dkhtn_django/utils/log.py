import logging
import os

from django.conf import settings


class Log(object):
    """
    日志记录.
    """
    def __init__(self):
        if not os.path.exists(settings.LOG_DIR):
            os.makedirs(settings.LOG_DIR)
        self.logname = os.path.join(settings.LOG_DIR, '%s' % "log")
        self.logger = logging.getLogger('django')
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')

    def __console(self, level, message):
        fh = logging.FileHandler(self.logname, 'a', encoding='utf-8')
        fh.suffix = '%Y-%m-%d.log'
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)

        if level == 'info':
            self.logger.info(message)
        elif level == 'debug':
            self.logger.debug(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)

        self.logger.removeHandler(fh)
        fh.close()

    def debug(self, message):
        self.__console('debug', message)

    def info(self, message):
        self.__console('info', message)

    def warning(self, message):
        self.__console('warning', message)

    def error(self, message):
        self.__console('error', message)
