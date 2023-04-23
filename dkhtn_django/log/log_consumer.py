import json
import threading
from datetime import datetime
from typing import List

import pika

from config.settings.base import rabbitmq_host
from dkhtn_django.log.models import LogMessage
from django.utils.timezone import get_current_timezone


class LogConsuming(threading.Thread):
    @staticmethod
    def _get_connection():
        parameters = pika.ConnectionParameters(rabbitmq_host)
        return pika.BlockingConnection(parameters)

    @staticmethod
    def callback(ch, method, properties, body):
        # do something
        logs: List[dict] = json.loads(body.decode("utf-8"))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        tz = get_current_timezone()
        for log in logs:
            log["timestamp"] = tz.localize(datetime.strptime(log["timestamp"], "%Y-%m-%d %H:%M:%S"))
            message = LogMessage(**log)
            message.save()

    def run(self):
        connection = self._get_connection()
        channel = connection.channel()

        channel.queue_declare(queue='log_queue')

        print('Hello world! :) Here is Log Insert Service')

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue='log_queue', on_message_callback=self.callback)

        channel.start_consuming()
