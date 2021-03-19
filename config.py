# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

import os

from apscheduler.jobstores.redis import RedisJobStore


class base_config:
    SECRET_KEY = 'DROPS'
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    # SECRET_KEY = os.urandom(24)
    CMS_USER_ID = 'DSADSA6jvxE2MeiZ5NnvJorNbN3XD1551512'
    VISITOR = 'vistor'
    WTF_CSRF_SECRET_KEY = '21321ewaawdasdas2321dsadsadas'
    TOKEN_EXPIRATION = 30 * 24 * 3600
    NGINX_CONFIG = '/etc/nginx/conf.d/blockip.conf'  # ip黑名单路径，使用nginx加载，只支持nginx的配置
    PDF_PATH = os.path.join(BASE_PATH, 'static', 'pdf')  # pdf文件存储路径
    HTML_PATH = os.path.join(BASE_PATH, 'static', 'html')  # html文件存储路径
    for path in [PDF_PATH, HTML_PATH]:  # 初始化创建目录
        if not os.path.exists(path):
            os.makedirs(path)
    is_save_html = True

    @staticmethod
    def init_app(app):
        pass

    # 配置周报公开发布时间
    Default_YEAR = 2020  # 默认展示年份
    Default_MIX_YEAR = 2019  # 默认展示最小年份
    Default_WEEK = 1  # 默认展示周
    Default_WEEKLY = 5  # 默认公布周报时间（1-7）：周一至周日
    # 黑名单周期
    BLOCK_IP_TIMEOUT = 24 * 60 * 60

    # 图片cdn接口
    IMG_CDN = 'http://img04.sogoucdn.com/net/a/04/link?appid=100520033&url='

    SCHEDULER_TIMEZONE = "Asia/Shanghai"
    # 邮件服务器配置
    # 发送者邮箱的服务器地址
    MAIL_SERVER = "smtp.163.com"
    MAIL_PORT = 465
    # MAIL_USE_TLS = True
    MAIL_USE_SSL = True
    MAIL_USERNAME = "xxx"
    MAIL_PASSWORD = "xxx"

    # 任务列表
    # SCHEDULER_JOBSTORES = {
    #     # 'default': SQLAlchemyJobStore(url=config.TestingConfig.SQLALCHEMY_DATABASE_URI),
  
    # }
    SCHEDULER_API_ENABLED = True


# 开发环境q
class DevConfig(base_config):
    DEBUG = True
    # 用户session

    # mysql设置

    MYSQL_HOST = '127.0.0.1'
    MYSQL_PORT = 3306
    MYSQL_DATABASE = 'wechat'
    MYSQL_USERNAME = 'root'
    MYSQL_PASSWORD = 'root'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(MYSQL_USERNAME, MYSQL_PASSWORD,
                                                                                   MYSQL_HOST, MYSQL_PORT,
                                                                                   MYSQL_DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_RECYCLE = 90

    # 配置redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PWD = 'doonsec'
    REDIS_DB = 3
    REDIS_DB_MEM = 4
    MEMCACHE_TIMEOUT = 60
    BLOCK_IP_TIMEOUT = 24 * 60 * 60

    # 首页文章加载片数
    FRONT_ARTICLES = 10


# 测试环境

class TestingConfig(base_config):
    SECRET_KEY = 'DROPS'
    DEBUG = False

    # mysql设置
    MYSQL_HOST = 'xxx'
    MYSQL_PORT = 3306
    MYSQL_DATABASE = 'xxx'
    MYSQL_USERNAME = 'xxx'
    MYSQL_PASSWORD = 'xxx'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(MYSQL_USERNAME, MYSQL_PASSWORD,
                                                                                   MYSQL_HOST, MYSQL_PORT,
                                                                                   MYSQL_DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_RECYCLE = 90

    # 配置redis
    REDIS_HOST = 'xxx'
    REDIS_PORT = 6379
    REDIS_PWD = 'xxx'
    REDIS_DB = 3
    REDIS_DB_MEM = 4
    MEMCACHE_TIMEOUT = 60
    BLOCK_IP_TIMEOUT = 24 * 60 * 60
    REDIS_PASSWORD = 'xxx'

    # 首页文章加载片数
    FRONT_ARTICLES = 10


# 生产环境
class ProConfig(base_config):
    SECRET_KEY = os.urandom(24)
    DEBUG = False

    # mysql设置
    MYSQL_HOST = 'rm-2ze67ql7d5x63p8ds.mysql.rds.aliyuncs.com'
    MYSQL_PORT = 3306
    MYSQL_DATABASE = 'wechat'
    MYSQL_USERNAME = 'xhsjcj'
    MYSQL_PASSWORD = 'xhsjcj@386'

    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://{}:{}@{}:{}/{}?charset=utf8'.format(MYSQL_USERNAME, MYSQL_PASSWORD,
                                                                                   MYSQL_HOST, MYSQL_PORT,
                                                                                   MYSQL_DATABASE)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = False
    SQLALCHEMY_POOL_SIZE = 100
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_POOL_RECYCLE = 90

    # 配置redis
    REDIS_HOST = '127.0.0.1'
    REDIS_PORT = 6379
    REDIS_PWD = 'foobared'
    REDIS_DB = 3
    REDIS_DB_MEM = 4
    MEMCACHE_TIMEOUT = 60
    BLOCK_IP_TIMEOUT = 24 * 60 * 60
    REDIS_PASSWORD = 'foobared'

    # 首页文章加载片数
    FRONT_ARTICLES = 10


config = {
    'development': DevConfig,
    'testing': TestingConfig,
    'production': ProConfig,
}
