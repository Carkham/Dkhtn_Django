import pika
from config.settings.base import rabbitmq_host


def rabbit_mq(message):
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()

    channel.queue_declare(queue="email_send_queue")
    channel.basic_publish(exchange="", routing_key="email_send_queue", body=message)
    channel.close()
