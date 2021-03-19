# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/11/9 17:13
@Auth ： AJay13
@File ：scheduler_job.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

from datetime import datetime, timedelta

from apscheduler.jobstores.redis import RedisJobStore

from apps.admin.models import WechatAccountTask, WechatArticle
from exts import scheduler, db
from models import EmailUser, System_Settings


class Config(object):  # 创建配置，用类
    # 任务列表
    SCHEDULER_JOBSTORES = {
        # 'default': SQLAlchemyJobStore(url=config.TestingConfig.SQLALCHEMY_DATABASE_URI),
        "redis": RedisJobStore(host='47.100.199.103', port=6379, password='doonsec', db=1)
    }
    SCHEDULER_API_ENABLED = True


# 检测爬虫服务的状态
@scheduler.task('cron', id='check_status', minute='*/40', )
def check_status():
    nowtime = datetime.now()
    print('检测是否爬取任务是否中断', datetime.now())
    account_task = WechatAccountTask.query.order_by(WechatAccountTask.last_spider_time.desc()).first()  # 公众号最近采集时间
    article = WechatArticle.query.order_by(WechatArticle.spider_time.desc()).first()  # 文章最近采集时间

    # 如果有一个时间大于，或者僵尸号的数量超过>总数的30% ,并且发送邮件的数量少于三
    if account_task and article:
        account_task_last_spider_time = account_task.last_spider_time
        article_spider_time = article.spider_time
        print(account_task_last_spider_time)
        print(article_spider_time)
        if (nowtime - article_spider_time > timedelta(
                hours=20) and nowtime - account_task_last_spider_time > timedelta(hours=20)):
            setting = System_Settings.query.order_by(System_Settings.create_time.desc()).first()  # 查找最新的配置文件中
            if setting and setting.warning_times < 6:
                email_user = EmailUser.query.all()
                if email_user:
                    # 发送一封邮件到全部人的账户
                    from utils.send_email import send_reemail
                    mail_user = []
                    for i in email_user:
                        mail_user.append(i.email)
                    message = {"article_spider_time": article_spider_time,
                               "account_task_last_spider_time": account_task_last_spider_time}
                    send_reemail(mail_user, **message)  # 发送邮件
                    setting.warning_times = setting.warning_times + 1
                    setting.last_warning_date = nowtime
                    db.session.commit()


# 定时同步访问日志模块，每半个小时同步一次访问的日志
@scheduler.task('cron', id='job_synchronization_log', hour='*/1', )
def job_synchronization_log():
    from utils.tools import synchronization_log
    print('自动同步访问日志：', str(datetime.now()))
    synchronization_log()
