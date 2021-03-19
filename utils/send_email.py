# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/11/9 16:58
@Auth ： AJay13
@File ：send_email.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
from threading import Thread

from flask import render_template
from flask_mail import Message

from exts import db
from exts import mail
from utils import field


# 发送邮件函数
def send_email(subject, sender, recipients, text_body, html_body):
    app = db.app

    with app.app_context():
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        msg.html = html_body
        try:
            mail.send(msg)
        except Exception as e:
            print(e)
            return field.params_error(message='邮件服务器出错')


# 发送邮件的内容
def send_reemail(email_users, **kwargs):
    '''
    将通过send_reemail函数发送一封邮件给目标邮箱。token的生成为jwt（json web token），在生成代码中设置过期失效时间。expires_in=600
    发送邮件的模板可在静态文件中email/reemail.html修改设定。设定合适依照jinja2模板
    :param user: 用户的标识
    :param email:用户的邮箱地址
    :return:发送一封邮件
    '''
    app = db.app

    with app.app_context():
        send_email(subject='[洞见聚合]爬虫模块服务停止预警',
                   sender='15993248973@163.com',
                   recipients=email_users,
                   text_body='error',
                   html_body=render_template('common/email/email.html',message =kwargs))


def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)


# 多线程异步发送邮件
def asy_send_email(to, template=None, **kwargs):
    app = db.app

    msg = Message(subject='[洞见聚合]爬虫模块服务停止预警',
                  sender=app.config['MAIL_USERNAME'], recipients=to)
    msg.body = "render_template(template + '.txt', **kwargs)"
    msg.html = "render_template(template + '.html', **kwargs)"
    thr = Thread(target=send_async_email, args=[app, msg])
    thr.start()
    print(msg)
    return thr
