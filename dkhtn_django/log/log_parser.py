# import re
import abc
from abc import ABC
from datetime import datetime

from dkhtn_django.log.model import LogMessage


class AbstractLogParser(ABC):
    @abc.abstractmethod
    def parse_log(self, log: str) -> LogMessage:
        pass


class LogParser(AbstractLogParser):
    def parse_log(self, log: str) -> LogMessage:
        log_parts = log.split(" | ")
        timestamp, log_name = log_parts[0].strip(), log_parts[1].strip()
        log_parts = log_parts[2].split("-")
        level = log_parts[0].strip()
        message = "-".join(log_parts[1:])
        message = message.strip()

        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return LogMessage(timestamp=timestamp, function_id=log_name, level=level, message=message)
