# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

import datetime

import shortuuid
from werkzeug.security import generate_password_hash, check_password_hash

from exts import db


class Admin(db.Model):
    '''
    管理员类
    '''
    __tablename__ = 't_admin'
    id = db.Column(db.String(100), primary_key=True, default=shortuuid.uuid)
    telephone = db.Column(db.String(11), unique=True)
    username = db.Column(db.String(50), nullable=True, unique=True)
    _password = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(50), unique=True)
    realname = db.Column(db.String(20))
    # avatar_path = db.Column(db.String(100))
    join_time = db.Column(db.DateTime, default=datetime.datetime.now)
    last_login_time = db.Column(db.DateTime, default=datetime.datetime.now)

    def __init__(self, *args, **kwargs):
        if 'password' in kwargs:
            self.password = kwargs.get('password')
            kwargs.pop('password')
        super(Admin, self).__init__(*args, **kwargs)

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, newpwd):
        self._password = generate_password_hash(newpwd)

    def check_password(self, rawpwd):
        return check_password_hash(self._password, rawpwd)

    @staticmethod
    def verify(username, password):
        print(username, password)
        from apis.common.response_code import AuthFailed
        user = Admin.query.filter_by(username=username).first()
        if not user:
            raise AuthFailed()
        if not user.check_password(password):
            raise AuthFailed()
            # return unauth_error()
        # if user.auth == 1:
        #     scope = 'UserScope'
        # elif user.auth == 2:
        #     scope = 'AdminScope'
        # elif user.auth == 3:
        #     scope = 'AdministratorsScope'
        # else:
        #     raise AuthFailed()
        return {'uid': user.id, }


class WechatTag(db.Model):
    __tablename__ = 't_wechat_tag'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tag_name = db.Column(db.String(30), nullable=True, unique=True)
    tag_en = db.Column(db.String(30), nullable=True, unique=True)
    tag_summary = db.Column(db.String(100), nullable=True, unique=True)

    create_time = db.Column(db.DateTime, default=datetime.datetime.now)

    accounts = db.relationship('TWechatAccount', backref='tags', lazy=True)
    Caccounts = db.relationship('TCommunityWechatAccount', backref='Ctags', lazy=True)


class TWechatAccount(db.Model):
    __tablename__ = 't_wechat_account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.String(50), nullable=True, unique=True)
    account_name = db.Column(db.String(30), nullable=True)
    tag = db.Column(db.Integer, db.ForeignKey('t_wechat_tag.id'))
    status = db.Column(db.String(50), nullable=True, default='forbid',
                       comment='监控的状态 默认 禁用 forbid  开始监控 start')  # 规则的状态 默认active 1 禁用 为0

    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


class TCommunityWechatAccount(db.Model):  # 社区提交的公众号
    __tablename__ = 't_community_wechat_account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account_id = db.Column(db.String(50), nullable=True, unique=True)
    account_link = db.Column(db.Text, nullable=True, )
    account_name = db.Column(db.String(30), nullable=True)
    tag = db.Column(db.Integer, db.ForeignKey('t_wechat_tag.id'))
    founder = db.Column(db.String(50), nullable=True, comment='贡献的人')
    status = db.Column(db.String(50), nullable=True, default='0',
                       comment='监控的状态 默认未审核 0  审核未通过 forbid  审核通过 permit')  # 社区提交公众号。默认为待审核 同意加入 permit 录用 弃用

    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


class Announcement(db.Model):
    __tablename__ = 't_announcement'  # 公告

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=True)
    context = db.Column(db.Text, nullable=True)
    flag = db.Column(db.Integer)
    time = db.Column(db.DateTime, default=datetime.datetime.now)
    publisher = db.Column(db.String(100), db.ForeignKey('t_admin.id'))


class GitCommit(db.Model):
    __tablename__ = 't_git_commit'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    commit_log = db.Column(db.String(100), nullable=True, comment='git 提交的commit记录')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


class System_Settings(db.Model):
    __tablename__ = 't_system_settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    commit_log = db.Column(db.String(100), nullable=True)
    github_url = db.Column(db.String(100), nullable=True, comment='github 仓库地址')
    maintenance = db.Column(db.String(10), comment='是否开启网站维护：True，False')
    # 邮件一天内提醒次数2 一天两次  1/3 3天一次
    warning_times = db.Column(db.INTEGER, default=0, comment='当天预警的次数')
    last_warning_date = db.Column(db.DateTime, comment='上次预警的时间')
    smtp_server = db.Column(db.String(30), nullable=True, comment='邮件服务器地址')
    smtp_port = db.Column(db.String(30), nullable=True, comment='邮件服务器端口')
    smtp_sender = db.Column(db.String(30), nullable=True, comment='邮件发件人')
    smtp_username = db.Column(db.String(30), nullable=True, comment='邮件服务器用户名')
    smtp_password = db.Column(db.String(30), nullable=True, comment='邮件服务器密码')

    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


class EmailUser(db.Model):
    __tablename__ = 't_email_user'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=True, comment='待发送邮箱用户')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


class Banner(db.Model):
    __tablename__ = 't_banner'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), nullable=True)
    image_url = db.Column(db.String(255), nullable=True)
    link_url = db.Column(db.String(255), nullable=True)
    priority = db.Column(db.Integer, default=0)
    create_time = db.Column(db.DateTime, default=datetime.datetime.now)


class User_Logs(db.Model):
    __tablename__ = 't_user_logs'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visitor_id = db.Column(db.String(255), nullable=True, comment='访客id')
    ip = db.Column(db.String(255), comment='ip')
    user_agent = db.Column(db.String(500), comment='user_agent')
    path = db.Column(db.String(255), comment='访问路由')
    url = db.Column(db.String(500), comment='访问链接')
    referrer = db.Column(db.String(500), comment='referrer')
    area = db.Column(db.String(255), comment='访客地区,如中国·北京')
    province = db.Column(db.String(255), comment='访客省份,如北京')
    create_time = db.Column(db.DateTime, comment='访问时间')


class MsgBoard(db.Model):
    __tablename__ = 't_msg_board'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visitor_id = db.Column(db.String(255), nullable=True, comment='留言者id')
    ip = db.Column(db.String(255), comment='留言者的ip')
    area = db.Column(db.String(255), comment='留言者访客地区,如中国·北京')
    content = db.Column(db.Text, nullable=True, comment='留言内容')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='留言时间')


class BlockIP(db.Model):
    '''
    黑名单
    '''
    __tablename__ = 't_block_ip'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ip = db.Column(db.String(255), comment='ip地址')
    end_time = db.Column(db.DateTime, comment='结束时间')
    notes = db.Column(db.Text, nullable=True, comment='备注内容')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='添加时间')


class HotSearch(db.Model):
    '''
    搜索的关键字
    '''
    __tablename__ = 't_hot_search'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    visitor_id = db.Column(db.String(255), nullable=True, comment='访客id')
    search = db.Column(db.String(255), nullable=True, comment='搜索词')
    page = db.Column(db.Integer, nullable=True, comment='页数')
    count = db.Column(db.Integer, nullable=True, comment='搜索结果')
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='添加时间')


class Donate(db.Model):
    '''
    捐赠列表
    '''
    __tablename__ = 't_donate'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), comment='捐助人名')
    money = db.Column(db.Integer, comment='捐助钱数')
    note = db.Column(db.String(255), comment='备注')
    hide = db.Column(db.Integer, default=0, comment='隐藏标注，1隐藏、0不隐藏')
    pay_time = db.Column(db.DateTime, comment='支付时间')  # 时间应该不会显示。
    create_time = db.Column(db.DateTime, default=datetime.datetime.now, comment='创建时间')
