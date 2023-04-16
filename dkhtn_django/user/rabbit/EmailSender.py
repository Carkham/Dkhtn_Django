import multiprocessing as mp
import random
import smtplib
from email.mime.text import MIMEText

import pika

from config.settings.base import EMAIL_FROM, EMAIL_TITLE, EMAIL_HOST, EMAIL_HOST_USER, EMAIL_HOST_PASSWORD
from config.settings.base import rabbitmq_host

html_head = """<!DOCTYPE html>
<html lang="en" xmlns:th="http://www.thymeleaf.org">
<head>
    <meta charset="UTF-8">
    <title>邮箱验证码</title>
    <style>
        table {
            width: 700px;
            margin: 0 auto;
        }
        #top {
            width: 700px;
            border-bottom: 1px solid #ccc;
            margin: 0 auto 30px;
        }
        #top table {
            font: 12px Tahoma, Arial, 宋体;
            height: 40px;
        }
        #content {
            width: 680px;
            padding: 0 10px;
            margin: 0 auto;
        }
        #content_top {
            line-height: 1.5;
            font-size: 14px;
            margin-bottom: 25px;
            color: #4d4d4d;
        }
        #content_top strong {
            display: block;
            margin-bottom: 15px;
        }
        #content_top strong span {
            color: #f60;
            font-size: 16px;
        }
        #verificationCode {
            color: #f60;
            font-size: 24px;
        }
        #content_bottom {
            margin-bottom: 30px;
        }
        #content_bottom small {
            display: block;
            margin-bottom: 20px;
            font-size: 12px;
            color: #747474;
        }
        #bottom {
            width: 700px;
            margin: 0 auto;
        }
        #bottom div {
            padding: 10px 10px 0;
            border-top: 1px solid #ccc;
            color: #747474;
            margin-bottom: 20px;
            line-height: 1.3em;
            font-size: 12px;
        }
        #content_top strong span {
            font-size: 18px;
            color: #FE4F70;
        }
        #sign {
            text-align: right;
            font-size: 18px;
            color: #FE4F70;
            font-weight: bold;
        }
        #verificationCode {
            height: 100px;
            width: 680px;
            text-align: center;
            margin: 30px 0;
        }
        #verificationCode div {
            height: 100px;
            width: 680px;
        }
        .button {
            color: #FE4F70;
            margin-left: 10px;
            height: 80px;
            width: 250px;
            resize: none;
            font-size: 42px;
            border: none;
            outline: none;
            padding: 10px 15px;
            background: #ededed;
            text-align: center;
            border-radius: 17px;
            box-shadow: 6px 6px 12px #cccccc,
            -6px -6px 12px #ffffff;
        }
        .button:hover {
            box-shadow: inset 6px 6px 4px #d1d1d1,
            inset -6px -6px 4px #ffffff;
        }
    </style>
</head>
<body>
<table>
    <tbody>
    <tr>
        <td>
            <div id="top">
                <table>
                    <tbody><tr><td></td></tr></tbody>
                </table>
            </div>
            <div id="content">
                <div id="content_top">
                    <strong>尊敬的用户：您好！</strong>
                    <strong>
                        您正在进行<span>注册账号</span>操作，请在验证码中输入以下验证码完成操作：
                    </strong>
                    <div id="verificationCode">
                        <button class="button" >"""
html_end = """</button>
                    </div>
                </div>
                <div id="content_bottom">
                    <small>
                        注意：此操作可能会修改您的密码、登录邮箱或绑定手机。如非本人操作，请及时登录并修改密码以保证帐户安全
                        <br>（工作人员不会向你索取此验证码，请勿泄漏！)
                    </small>
                </div>
            </div>
            <div id="bottom">
                <div>
                    <p>此为系统邮件，请勿回复<br>
                        请保管好您的邮箱，避免账号被他人盗用
                    </p>
                    <p id="sign">——Faas平台</p>
                </div>
            </div>
        </td>
    </tr>
    </tbody>
</table>
</body>
"""


def send_email(email):
    sms_code = '%06d' % random.randint(0, 999999)
    context = html_head + sms_code + html_end
    message = MIMEText(context, 'html', 'utf-8')
    message['Subject'] = EMAIL_TITLE
    message['From'] = EMAIL_FROM
    message['To'] = email

    smtpObj = smtplib.SMTP()
    smtpObj.connect(EMAIL_HOST, 25)
    smtpObj.login(EMAIL_HOST_USER, EMAIL_HOST_PASSWORD)
    smtpObj.sendmail(EMAIL_FROM, [email], message.as_string())
    smtpObj.quit()


def callback(ch, method, properties, email):
    send_email(email.decode("utf-8"))
    ch.basic_ack(delivery_tag=method.delivery_tag)


def connect_rabbitmq():
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    channel = connection.channel()
    channel.queue_declare(queue='email_send_queue')

    channel.basic_consume(queue='email_send_queue',
                          auto_ack=False,
                          on_message_callback=callback)
    # 开始监听队列
    channel.start_consuming()


def start_email_sender():
    sender = mp.Process(target=connect_rabbitmq)
    sender.start()
