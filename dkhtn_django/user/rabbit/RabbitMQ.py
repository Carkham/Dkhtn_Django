import pika


class RabbitMQ:
    def __init__(self, email):
        connection = pika.BlockingConnection(pika.ConnectionParameters('139.9.143.161'))
        channel = connection.channel()

        channel.queue_declare(queue="email_send_queue")
        channel.basic_publish(exchange="", routing_key="email_send_queue", body=email)
        channel.close()
