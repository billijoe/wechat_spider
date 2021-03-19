# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from apis.common.dbs import api_db, Base
from sqlalchemy import orm


class WechatArticle(Base):
    '''
        公众号文章
    '''
    __tablename__ = 'wechat_article'
    id = api_db.Column(api_db.Integer, primary_key=True, autoincrement=True)
    account = api_db.Column(api_db.String(255), nullable=False, comment='公众号名称')
    title = api_db.Column(api_db.String(255), nullable=False, comment='公众号标题')
    url = api_db.Column(api_db.String(255), nullable=False, comment='公众号的url')
    author = api_db.Column(api_db.String(50), nullable=False, comment='工作中号发布的作者')
    publish_time = api_db.Column(api_db.DateTime, nullable=True, comment='文章发布时间')

    digest = api_db.Column(api_db.String(50), nullable=False, comment='公众号文章描述')
    cover = api_db.Column(api_db.String(255), nullable=False, comment='公众号文章封面')
    pics_url = api_db.Column(api_db.TEXT, nullable=False, comment='公众号文章中图片列表')
    content_html = api_db.Column(api_db.Text(16777216), nullable=False, comment='公众号文章中心内容')
    source_url = api_db.Column(api_db.String(255), nullable=False, comment='公众号文章源连接')
    comment_id = api_db.Column(api_db.String(50), nullable=False, comment='公众号文章评论id')
    sn = api_db.Column(api_db.String(50), nullable=False, unique=True, comment='')
    spider_time = api_db.Column(api_db.DateTime, nullable=True, comment='公众号抓取时间')
    flag = api_db.Column(api_db.Integer, nullable=True, comment='flag标志，默认为0 普通，1为精华')

    @orm.reconstructor
    def __init__(self):
        self.fields = ['id', '__biz', 'title', 'url', 'publish_time', 'digest', 'cover']

WechatArticle.__biz = api_db.Column(api_db.String(50), nullable=False, index=True, comment='公众号id')


class WechatTagApi(Base):
    '''
    公众号标签："安全研发等等"
    '''
    __tablename__ = 't_wechat_tag'
    id = api_db.Column(api_db.Integer, primary_key=True, autoincrement=True)
    tag_name = api_db.Column(api_db.String(30), nullable=False, unique=True)
    tag_en = api_db.Column(api_db.String(30), nullable=False, unique=True)
    tag_summary = api_db.Column(api_db.String(100), nullable=False, unique=True)
    accounts = api_db.relationship('TWechatAccount', backref='tags', lazy=True)

    @orm.reconstructor
    def __init__(self):
        self.fields = ['id', 'tag_name', 'tag_en']


class TWechatAccount(Base):
    '''
    公众号
    '''
    __tablename__ = 't_wechat_account'
    id = api_db.Column(api_db.Integer, primary_key=True, autoincrement=True)
    account_id = api_db.Column(api_db.String(50), nullable=False, unique=True)
    account_name = api_db.Column(api_db.String(30), nullable=False)
    tag = api_db.Column(api_db.Integer, api_db.ForeignKey('t_wechat_tag.id'))
    status = api_db.Column(api_db.String(50), nullable=False, default='forbid',
                       comment='监控的状态 默认 禁用 forbid  开始监控 start')  # 规则的状态 默认active 1 禁用 为0

    @orm.reconstructor
    def __init__(self):
        self.fields = ['id', 'account_id', 'account_name', 'tag']


class Banner(Base):
    __tablename__ = 't_banner'
    id = api_db.Column(api_db.Integer, primary_key=True, autoincrement=True)
    name = api_db.Column(api_db.String(255), nullable=False)
    image_url = api_db.Column(api_db.String(255), nullable=False)
    link_url = api_db.Column(api_db.String(255), nullable=False)
    priority = api_db.Column(api_db.Integer, default=0)

    @orm.reconstructor
    def __init__(self):
        self.fields = ['id', 'name', 'image_url', 'link_url']