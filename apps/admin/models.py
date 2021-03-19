# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from exts import db


class WechatAccount(db.Model):
    '''
        爬取的微信公众号信息
    '''
    __tablename__ = 'wechat_account'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account = db.Column(db.String(255), nullable=True, comment='公众号中文名')
    head_url = db.Column(db.String(255), nullable=True, comment='公众号头像链接')
    summary = db.Column(db.String(500), nullable=True, comment='公众号描述')
    qr_code = db.Column(db.String(255), nullable=True, comment='公众号二维码')
    verify = db.Column(db.String(255), nullable=True, comment='公众号认证')
    spider_time = db.Column(db.DateTime, comment='上次爬取时间')

    @classmethod
    @property
    def get_biz(self):
        return WechatAccount.__biz

WechatAccount.__biz = db.Column(db.String(50), nullable=True,unique=True, comment='公众号id')


class WechatAccountTask(db.Model):
    '''
        待爬取公众号任务id
    '''
    __tablename__ = 'wechat_account_task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    last_publish_time = db.Column(db.DateTime, nullable=True, comment='上次抓取到的文章发布时间，做文章增量采集用')
    last_spider_time = db.Column(db.DateTime, nullable=True, comment='上次抓取时间，用于同一个公众号每隔一段时间扫描一次')
    is_zombie = db.Column(db.Integer, nullable=True, default=0, comment='僵尸号 默认3个月未发布内容为僵尸号，不再检测')


WechatAccountTask.__biz = db.Column(db.String(50), nullable=True, comment='公众号id')


class WechatArticle(db.Model):
    '''
        公众号文章
    '''
    __tablename__ = 'wechat_article'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    account = db.Column(db.String(255), nullable=True, comment='公众号名称')
    title = db.Column(db.String(255), nullable=True, comment='公众号标题')
    url = db.Column(db.String(255), nullable=True, comment='公众号的url')
    author = db.Column(db.String(50), nullable=True, comment='工作中号发布的作者')
    publish_time = db.Column(db.DateTime, nullable=True, comment='文章发布时间')

    digest = db.Column(db.String(50), nullable=True, comment='公众号文章描述')
    cover = db.Column(db.String(50), nullable=True, comment='公众号文章封面')
    pics_url = db.Column(db.TEXT, nullable=True, comment='公众号文章中图片列表')
    content_html = db.Column(db.Text(16777216), nullable=True, comment='公众号文章中心内容')
    source_url = db.Column(db.String(255), nullable=True, comment='公众号文章源连接')
    comment_id = db.Column(db.String(50), nullable=True, comment='公众号文章评论id')
    sn = db.Column(db.String(50), nullable=True, unique=True,comment='')
    spider_time = db.Column(db.DateTime, nullable=True, comment='公众号抓取时间')
    flag  = db.Column(db.Integer, nullable=True,default=0, comment='flag标志，默认为0 普通，1为精华')
    is_hide  = db.Column(db.Integer, nullable=True,default=0, comment='文章是否隐藏不对外显示，默认0不隐藏')
    re_spider  = db.Column(db.Integer, nullable=True,default=0, comment='是否回采文章，0默认、1失败、2完成')
WechatArticle.__biz = db.Column(db.String(50), nullable=True, index=True,comment='公众号id')


class WechatArticleComment(db.Model):
    '''
        公众号的评论
    '''
    __tablename__ = 'wechat_article_comment'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    comment_id = db.Column(db.String(50), nullable=True, comment='评论的id与文章关联')
    nick_name = db.Column(db.String(255), nullable=True, comment='评论的昵称')
    logo_url = db.Column(db.String(255), nullable=True, comment='公众号id')
    content = db.Column(db.String(2000), nullable=True, comment='评论内容')
    create_time = db.Column(db.DateTime, nullable=True, comment='评论添加时间')
    content_id = db.Column(db.String(50), nullable=True, comment='本条评论内容的id')
    like_num = db.Column(db.Integer, nullable=True, comment='点赞数')
    is_top = db.Column(db.Integer, nullable=True, comment='')
    spider_time = db.Column(db.DateTime, nullable=True, comment='抓取时间')


WechatArticleComment.__biz = db.Column(db.String(50), nullable=True, comment='公众号id')


class WechatArticleDynamic(db.Model):
    '''
        公众号动态：点赞数、喜欢书、评论数
    '''
    __tablename__ = 'wechat_article_dynamic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sn = db.Column(db.String(50), nullable=True, comment='公众号id')
    read_num = db.Column(db.Integer, nullable=True, default=0, comment='阅读数')
    like_num = db.Column(db.Integer, nullable=True, default=0, comment='喜欢数')
    comment_count = db.Column(db.Integer, nullable=True, default=0, comment='评论数')
    spider_time = db.Column(db.DateTime, nullable=True, comment='抓取时间')

WechatArticleDynamic.__biz = db.Column(db.String(50), nullable=True, comment='公众号id')

class WechatArticleList(db.Model):
    '''
        公众号中微信文章列表
    '''
    __tablename__ = 'wechat_article_list'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(255), nullable=True, comment='标题')
    digest = db.Column(db.String(2000), nullable=True, comment='描述')
    url = db.Column(db.String(500), nullable=True, comment='文章链接')
    source_url = db.Column(db.String(1000), nullable=True, comment='源地址')
    cover = db.Column(db.String(255), nullable=True, comment='封面地址')
    subtype = db.Column(db.Integer, nullable=True, comment='')
    is_multi = db.Column(db.Integer, nullable=True, comment='')
    author = db.Column(db.String(255), nullable=True, comment='作者')
    copyright_stat = db.Column(db.Integer, nullable=True, comment='')
    duration = db.Column(db.Integer, nullable=True, comment='')
    del_flag = db.Column(db.Integer, nullable=True, comment='删除标志')
    type = db.Column(db.Integer, nullable=True, comment='')
    sn = db.Column(db.String(50), nullable=True, comment='',index=True)
    publish_time = db.Column(db.DateTime, nullable=True, comment='文章发布时间，做文章增量采集用')
    spider_time = db.Column(db.DateTime, nullable=True, comment='上次抓取时间，')



WechatArticleList.__biz = db.Column(db.String(50), nullable=True, comment='公众号id')


class WechatArticleTask(db.Model):
    '''
        微信文章任务队列
    '''
    __tablename__ = 'wechat_article_task'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sn = db.Column(db.String(50), nullable=True, comment='')
    article_url = db.Column(db.String(255), nullable=True, comment='公众号链接')
    state = db.Column(db.Integer, default=0,  comment='文章抓取状态:0 待抓取 2 抓取中 1 抓取完毕 -1 抓取失败')


WechatArticleTask.__biz = db.Column(db.String(50), nullable=True, comment='公众号id')
