import multiprocessing as mp
import random
import smtplib
from email.mime.text import MIMEText
import pika
from config.settings.base import EMAIL_FROM, EMAIL_TITLE, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD


class EmailSender(mp.Process):
    def __init__(self, name):
        self.name = name
        super().__init__()

    def run(self):
        start_email_sender()


def callback(ch, method, properties, email):
    sender = 'dkhtn163@163.com'
    receivers = [email.decode('utf-8')]

    sms_code = '%06d' % random.randint(0, 999999)
    message = MIMEText("[Faas] 验证码: {0} (十分钟有效)，仅用于Faas平台邮箱有效性验证，请您尽快完成验证。请勿将验证码泄露给他人。".format(sms_code), 'plain',
                       'utf-8')
    message['Subject'] = EMAIL_TITLE
    message['From'] = EMAIL_FROM
    message['To'] = receivers[0]

    try:
        smtpObj = smtplib.SMTP()
        smtpObj.connect(EMAIL_HOST, 25)
        smtpObj.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
        smtpObj.sendmail(sender, receivers, message.as_string())
        smtpObj.quit()
    except smtplib.SMTPException as e:
        print('error', e)

    print("邮箱：{0} 发送成功".format(email.decode("utf-8")))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def connect_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='139.9.143.161'))
    channel = connection.channel()
    channel.queue_declare(queue='email_send_queue')

    channel.basic_consume(queue='email_send_queue',
                          auto_ack=False,
                          on_message_callback=callback)
    # 开始监听队列
    channel.start_consuming()
    # 关闭连接
    # channel.close()
    # connection.close()


def start_email_sender():
    sender = mp.Process(target=connect_rabbitmq)
    sender.start()

    # sender = EmailSender("emailSender")
    # sender.daemon = True
    # sender.start()
    # print("sender start")
