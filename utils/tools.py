#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'AJay'
__mtime__ = '2019/10/11 0011'

"""
import datetime
import os
import shutil
import time
from html import unescape
from operator import itemgetter

from dateutil.relativedelta import relativedelta
from git import Repo
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Line
from pyecharts.charts import Pie
from qqwry import QQwry, updateQQwry
from sqlalchemy import and_, extract, func, desc, or_
from user_agents import parse

from apps.admin.models import WechatArticleDynamic, WechatArticleList, \
    WechatAccountTask, WechatAccount, WechatArticle
from config import base_config
from exts import db
from models import WechatTag, TCommunityWechatAccount, \
    User_Logs, HotSearch


class IP2Region():
    '''
    解析ip地址：lookup(ip)方法将ip转化成（"省份","地区"）
    '''

    def __init__(self):
        self.filename = 'qqwry.dat'
        self.dat_path = os.path.join(base_config.BASE_PATH, 'utils', self.filename)
        self.q = QQwry()
        if os.path.exists(self.dat_path):
            self.q.load_file(self.dat_path)
            print(self.q)
        else:
            return
            print('初始化更新ip库')
            self.update_dat()
            self.reload_dat()

    def get_lastone(self):
        '''
        ﻿返回最后一条数据，最后一条通常为数据的版本号
        ﻿没有数据则返回一个None
        :return:
        '''
        version = self.q.get_lastone()
        return version

    def update_dat(self):
        '''
        异步更新，使用线程或者celery更新IP数据库源
        :return:(bool) 成功后返回一个正整数，是文件的字节数；失败则返回一个负整数。
        '''
        result = updateQQwry(self.dat_path)
        if result > 0:
            print('ip库更新成功')
            return True
        print('ip库更新失败，网络出现故障')
        return False

    def lookup(self, ip):
        '''
        解析ip地址
        :param ip(str): 要解析的ip地址
        :return: 找到则返回一个含有两个字符串的元组，如：('国家', '省份')﻿没有找到结果，则返回一个None
        '''
        return self.q.lookup(ip)

    def reload_dat(self):
        '''
        重载IP数据源，当IPdat数据更新的时候，使用此方法更新数据
        :return: (bool) 重载成功返回True，重载失败返回Flase
        '''
        self.q.clear()
        if not self.q.is_loaded():
            self.q.load_file(self.dat_path)
            return True
        return False


def get_user_ip(request):
    '''
    获取用户的真实ip地址，因为使用的是nginx，所以常规看不到ip地址
    :param request: 请求的数据
    :return:
    '''
    x_forwarded_for = request.headers.get('X-Forwarded-For')
    if x_forwarded_for:
        if len(x_forwarded_for.split(',')) > 1:
            return x_forwarded_for.split(',')[-1]
        else:
            return x_forwarded_for
    elif request.headers.get('X-Real-IP'):
        return request.headers.get('X-Real-IP')
    else:
        return request.remote_addr


def get_user_referrer(request):
    '''
    获取用户的referer，如果是ngxin中设置了Referer，就会返回ngixn中的referer
    :param request: 请求的数据
    :return:
    '''
    Referer = request.headers.get("Referer")
    if Referer:
        return Referer
    return request.referrer


def get_user_driver(ua):
    '''
    解析用户的UA属性，browser （浏览器）、os（操作系统）、device（设备）。分别有family 、version 、brand 、version_string、model
    现用到返回设备
    :param ua: user_agent
    :return: user_agent(obj)：
    '''
    user_agent = parse(ua)
    return user_agent


def get_driver_logo(ua_obj):
    '''
    获取ua中系统的大致型号。给前端返回一个图标。
    #TODO：这里不确定有哪些型号，现在只做已知的内容，当收集一部分之后，再最后写固定。这个地方需要一点一点修改
    :param ua_obj(obj):获取ua的对象
    :return:
    '''
    os = ua_obj.os.family  # operating system properties
    if os == 'Windows':
        return 'Windows'
    elif os == 'Linux' or os == 'Ubuntu':
        return 'Linux'
    elif os == 'iOS' or os == 'Mac OS X':
        return 'iOS'
    elif os == 'Android':
        return 'Android'
    return os


import markdown


def markdown2html(text):
    return markdown.markdown(text, extensions=['extra'])


import re


# 过滤html
def filter_html(content_html):
    no_n_html = content_html.replace("\\n", '').replace('xa0', '').replace('\\', '')
    no_style_html = no_n_html.replace("style=\"visibility: hidden;\"", "")  #: 修复bug。微信改版爬取的数据被隐藏。
    new_html = no_style_html.replace('data-src=\\', 'src=').replace('data-src="',
                                                                    'src="http://img04.sogoucdn.com/net/a/04/link?appid=100520033&url=')
    return '<div style="margin: 20px">' + new_html + '</div>'  # 改变弹窗样式


# github排版
def do_work(commit_log):  # 生成md文件 并且同步到github上
    git_path = (os.path.join(base_config.BASE_PATH.split('apps')[0], 'git'))  # 组合
    print(git_path)
    'TODO:这里设置根据github项目的用户名_名称命名一个文件夹'
    if not os.path.exists(git_path):
        os.makedirs(git_path)
        clone_repo = Repo.clone_from('https://github.com/DropsOfZut/awesome-security-weixin-official-accounts.git',
                                     git_path)  # 拉取远程代码
        # clone_repo = Repo.clone_from('https://github.com/Hatcat123/WechatTogeter.git', git_path)  # 拉取远程代码

    # 新建版本库对象 每次使用git之前 先拉取分支
    repo = Repo(git_path)
    remote = repo.remote()
    remote.pull('master')  # 后面跟需要拉取的分支名称

    accounts_dict = {}
    accounts_obj = WechatAccount.query
    accounts = accounts_obj.all()
    accounts_num = accounts_obj.count()  # 公众号数量
    contributions = TCommunityWechatAccount.query.with_entities(
        TCommunityWechatAccount.founder).distinct().all()  # 贡献者名单 -> [('admin',),(''test),]

    for account in accounts:
        accounts_info = {}
        accounts_info['account'] = account.account
        accounts_info['head_url'] = account.head_url
        accounts_info['summary'] = account.summary
        accounts_info['qr_code'] = account.qr_code
        accounts_info['account'] = account.account
        accounts_info['__biz'] = account.__biz
        accounts_dict[account.__biz] = accounts_info

    tags_obj = WechatTag.query  # 获取所有tags obj
    tags = tags_obj.all()  # 获取所有tags
    tags_num = tags_obj.count()  # 获取所有tags 数量
    for tag in tags:
        tag_name = tag.tag_name
        tag_en = tag.tag_en

        print(tag_name)
        print('{}.md'.format(tag_en))  # 在这里创建一个文件夹
        with open(os.path.join(git_path, '{}.md'.format(tag_en)), 'w+', encoding='utf-8')as f:
            f.truncate()
            for account in tag.accounts:  # 获取tag下的所有的公众号

                accounts_info = accounts_dict.get(account.account_id)
                if accounts_info:
                    print(accounts_info)
                    one_accound = '''
### {account_name}

{summary}

<img align="top" width="180" src="{qr_code}" alt="" />

---

'''.format(account_name=accounts_info.get('account'), summary=accounts_info.get('summary'),
           account_id=accounts_info.get('__biz'), qr_code=accounts_info.get('qr_code'), )
                    f.write(one_accound)
    # README.md的编写
    header_accound = ''
    body_accound = ''
    foot_accound = ''
    all_accound = ''
    header_accound = '''
# awesome-security-weixin-official-accounts
网络安全类公众号推荐，点击分类详情可快速查看微信公众号二维码

本项目共分为{tag_num}大类，收集公众号{account_num}个。
收集优质文章在[微信聚合平台](http://wechat.doonsec.com)展示。

- [目录分类]()\n'''.format(tag_num=tags_num, account_num=accounts_num)
    for tag in tags:
        tag_name = tag.tag_name
        header_accound += '	- [{tag_name}](#{tag_name})\n'.format(tag_name=tag_name)

    for tag in tags:
        tag_name = tag.tag_name
        tag_en = tag.tag_en
        tag_summary = tag.tag_summary
        body_accound += '''

---

## [{tag_name}](/{tag_en}.md)

*{tag_summary}*
'''.format(tag_name=tag_name, tag_en=tag_en, tag_summary=tag_summary)
        for account in tag.accounts:
            accounts_info = accounts_dict.get(account.account_id)
            if accounts_info:
                print(accounts_info)
                body_accound += "* [{account_name}](/{tag_en}.md#{account_name}) :- {summary} \n".format(
                    account_name=accounts_info.get('account'), tag_en=tag_en,
                    summary=accounts_info.get('summary'))

    foot_accound = '''
## Contribution

*感谢为平台提供优质公众号*

{Contribution}

##  Coder

*感谢洞见研发工程师参与此项目设计*

Avatar | ID 
--- | --- |
![](https://avatars1.githubusercontent.com/u/28727970?s=30) | [Hatcat123](https://github.com/Hatcat123 )
![](https://avatars1.githubusercontent.com/u/22851022?s=30) | [Joynice](https://github.com/Joynice )

## Thanks
感谢[@neargle](https://github.com/neargle)对本项目提供无私的帮助
## License
GNU GENERAL PUBLIC LICENSE'''.format(
        Contribution='\n'.join('【[{name}](https://github.com/{name})】'.format(name=name[0]) for name in contributions))

    all_accound = header_accound + body_accound + foot_accound  # 仓库readme组成部分为头、身体、脚
    with open(os.path.join(git_path, 'README.md'), 'w+', encoding='utf-8')as f:
        f.write(all_accound)

        # 如何预览md的格式？
    try:

        index = repo.index
        for tag in tags:
            index.add(['{tag_en}.md'.format(tag_en=tag.tag_en)])
        index.add(['README.md'])

        index.commit(commit_log)  # 从前端填写commit信息。。。

        # 推送本地分支到远程版本库
        remote.push()
    except Exception as e:
        shutil.rmtree(path=git_path)
    return True


# 周报排版
def weekily_work(year, week, week_day, wechat_article, keyword=''):
    # 周报的头信息
    if year and week and week_day:
        header = '''# {year}年 第{week}周 微信公众号精选安全技术文章总览
    
> [洞见网安](http://wechat.doonsec.com) {date}\n
    '''.format(year=year, week=week,
               date='{year}-{mon}-{day}'.format(year=week_day[0], mon=week_day[1], day=week_day[2], ))
    else:
        # 关键字搜索的头信息
        header = '''# {keyword} | 微信公众号精选安全技术文章汇总
    
> [洞见网安](http://wechat.doonsec.com) \n
        '''.format(keyword=keyword)
    body = ''
    for article in wechat_article:
        _ = '''
---
### [{title}]({url})

> [{account}](http://wechat.doonsec.com/article/?id={sn}) {publish_time}

{digest}

'''.format(title=article.title, url=article.url, account=article.account, sn=article.sn,
           publish_time=article.publish_time, digest=article.digest)
        body += _
    foot = '''
>本站文章为爬虫采集，目的是为了方便更好的提供免费聚合服务，如有侵权请告知。具体请在留言告知，我们将清除对此公众号的监控，并清空相关文章。所有内容，均摘自于互联网，不得以任何方式将其用于商业目的。由于传播，利用此文所提供的信息而造成的任何直接或间接的后果和损失，均由使用者本人负责，本站以及文章作者不承担任何责任。
'''
    content = header + body + foot
    return content


# 快速关注公众号排版
def follow_wechat():
    accounts_dict = {}
    accounts_obj = WechatAccount.query
    accounts = accounts_obj.all()
    accounts_num = accounts_obj.count()  # 公众号数量

    for account in accounts:
        accounts_info = {}
        accounts_info['account'] = account.account
        accounts_info['head_url'] = account.head_url
        accounts_info['summary'] = account.summary
        accounts_info['qr_code'] = account.qr_code
        accounts_info['account'] = account.account
        accounts_info['__biz'] = account.__biz
        accounts_dict[account.__biz] = accounts_info

    tags_obj = WechatTag.query  # 获取所有tags obj
    tags = tags_obj.all()  # 获取所有tags
    tags_num = tags_obj.count()  # 获取所有tags 数量

    # README.md的编写
    header_accound = ''
    body_accound = ''
    foot_accound = ''
    all_accound = ''

    header_accound = '''
# [awesome-security-weixin-official-accounts](https://github.com/DropsOfZut/awesome-security-weixin-official-accounts/)
网络安全类公众号推荐，点击名称可快速关注微信公众号

本项目共分为{tag_num}大类，收集公众号{account_num}个。
收集优质文章在[微信聚合平台](http://wechat.doonsec.com)展示。

- [目录分类]()\n'''.format(tag_num=tags_num, account_num=accounts_num)

    for tag in tags:
        tag_name = tag.tag_name
        tag_summary = tag.tag_summary
        header_accound += '	- [{tag_name}](#{tag_name})\n'.format(tag_name=tag_name)
        body_accound += '''

---

## [{tag_name}]({tag_name})\n
{tag_summary}


|公众号||公众号||公众号||公众号|
|:--|:--|:--|:--|:--|:--|:--|
'''.format(tag_name=tag_name, tag_summary=tag_summary)
        for account_list in split_list_average_n(tag.accounts, 4):
            for account in account_list:
                accounts_info = accounts_dict.get(account.account_id)
                if accounts_info:
                    body_accound += '|<div style="width: 150pt"><img align="right" width="80" src="{qr_code}" alt="" />**[{account_name}](http://wechat.doonsec.com/admin/wechat_echarts/?biz={account_biz})**<details><summary>*{summary_short}*</summary> {summary}</details></div>|<img width=1/>'.format(
                        account_name=accounts_info.get('account'),
                        summary_short=accounts_info.get('summary').replace('|', '')[0:6],
                        account_biz=accounts_info.get('__biz'),
                        summary=accounts_info.get('summary').replace('|', '')[6:], qr_code=accounts_info.get('qr_code'))
            body_accound += '|\n'

    foot_accound = '''
## Coder
感谢洞见研发工程师参与此项目设计

* [@AJay13](https://github.com/Hatcat123)
* [@Joynice](https://github.com/Joynice)

## Thanks
感谢[@neargle](https://github.com/neargle)对本项目提供无私的帮助

## License
GNU GENERAL PUBLIC LICENSE'''

    all_accound = header_accound + body_accound + foot_accound  # 仓库readme组成部分为头、身体、脚
    return all_accound


## 将一个列表,分成若干个大小为n的列表
def split_list_average_n(origin_list, n):
    for i in range(0, len(origin_list), n):
        yield origin_list[i:i + n]


def is_Linux_which_sys():
    # 判断系统是不是linux系统，一般软件只能在linux上运行，windows上只是开发环境。目前时对黑名单做判断操作nginx
    import platform
    if (platform.system() == 'Windows'):
        print('Windows系统')
        return False
    elif (platform.system() == 'Linux'):
        print('Linux系统')
        return True
    else:
        return False


# 本周收录文章统计
def bar_base1() -> Line:
    today = datetime.date.today()
    date_list = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    date_list.reverse()

    data_list = [WechatArticle.query.filter(
        and_(extract('year', WechatArticle.spider_time) == str(date).split('-')[0],
             extract('month', WechatArticle.spider_time) == str(date).split('-')[1],
             extract('day', WechatArticle.spider_time) == str(date).split('-')[2],
             )).count() for date in date_list]

    c = (
        Line()
            .add_xaxis(xaxis_data=date_list)
            .add_yaxis("文章数", data_list, is_smooth=True, color='#66CDAA',
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="本周收录文章统计", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return c


# 今日收录文章表
def bar_base2() -> Line:
    today = datetime.date.today()
    articles_num = [WechatArticle.query.filter(
        and_(extract('year', WechatArticle.spider_time) == str(today).split('-')[0],
             extract('month', WechatArticle.spider_time) == str(today).split('-')[1],
             extract('day', WechatArticle.spider_time) == str(today).split('-')[2],
             extract('hour', WechatArticle.spider_time) == str(i),
             )).count() for i in range(25)]
    # print(['{}:00'.format(i) for i in range(25)])
    c = (
        Line()
            .add_xaxis(['{}:00'.format(i) for i in range(25)])
            .add_yaxis("文章数", articles_num, is_smooth=True,
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="今日收录文章数", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return c


# 最多文章top10集合
def bar_base3():
    account = db.session.query(WechatArticle.account, func.count(WechatArticle.id)).group_by(
        WechatArticle.account).order_by(desc(func.count(WechatArticle.id))).limit(10).all()
    keys = []
    values = []
    for key, value in account:
        keys.append(key)
        values.append(value)
    bar = (
        Bar()
            .add_xaxis(keys)
            .add_yaxis("公众号名称", values)
            .set_global_opts(title_opts=opts.TitleOpts(title="公众号收录文章数TOP10", pos_top='10%', pos_left='40%'),
                             xaxis_opts=opts.AxisOpts(name_rotate=-90, name_location='center',
                                                      axislabel_opts={'rotate': -45}),
                             legend_opts=opts.LegendOpts(is_show=False))

        # 或者直接使用字典参数
        # .set_global_opts(title_opts={"text": "主标题", "subtext": "副标题"})
    )
    return bar


# 今日访问量
def bar_base4() -> Line:
    today = datetime.date.today()
    logs_num = [User_Logs.query.with_entities(User_Logs.visitor_id).filter(
        and_(extract('year', User_Logs.create_time) == str(today).split('-')[0],
             extract('month', User_Logs.create_time) == str(today).split('-')[1],
             extract('day', User_Logs.create_time) == str(today).split('-')[2],
             extract('hour', User_Logs.create_time) == str(i),
             )).distinct().count() for i in range(25)]
    # print(['{}:00'.format(i) for i in range(25)])
    c = (
        Line()
            .add_xaxis(['{}:00'.format(i) for i in range(25)])
            .add_yaxis("访问量", logs_num, is_smooth=True,
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="今日实时访问量", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return c


# 优化-减少查询次数

# 阅读量统计折线图
def readnum_echarts(biz):
    dynamics = WechatArticleDynamic.query.filter_by(__biz=biz).order_by(WechatArticleDynamic.id.desc()).all()

    keys = []
    values = []
    for dynamic in dynamics:
        keys.append(dynamic.sn)
        values.append(dynamic.read_num)

    c = (
        Line()
            .add_xaxis(keys)
            .add_yaxis("阅读量", values, is_smooth=True,
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="公众号阅读量", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return c

# 获取多少天前的日期
def getBetweenDay(begin_date):
    date_list = []
    begin_date = datetime.datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.datetime.strptime(time.strftime('%Y-%m-%d', time.localtime(time.time())), "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += datetime.timedelta(days=1)
    return date_list


# 获取某天凌晨的日期

def get_day_zero_time(date):
    """根据日期获取当天凌晨时间"""
    if not date:
        return 0
    date_zero = datetime.datetime.now().replace(year=date.year, month=date.month,
                                                day=date.day, hour=0, minute=0, second=0)
    date_zero_time = int(time.mktime(date_zero.timetuple())) * 1000
    return date_zero


# 本月发文折线图
def mouth_article(biz):
    begin_date = (datetime.datetime.now() - relativedelta(months=+1)).strftime("%Y-%m-%d")
    date_list = getBetweenDay(begin_date=begin_date)

    data_list = [WechatArticleList.query.filter_by(__biz=biz).filter(
        and_(extract('year', WechatArticleList.publish_time) == str(date).split('-')[0],
             extract('month', WechatArticleList.publish_time) == str(date).split('-')[1],
             extract('day', WechatArticleList.publish_time) == str(date).split('-')[2],
             )).count() for date in date_list]

    c = (
        Line()
            .add_xaxis(xaxis_data=date_list)
            .add_yaxis("文章数", data_list, is_smooth=True, color='#66CDAA',
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="月发布文章统计", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return c


# 历史发文时间折线图
def article_hour_num(biz):
    article_num = [WechatArticleList.query.filter_by(__biz=biz).filter(
        and_(
            extract('hour', WechatArticleList.publish_time) == str(i),
        )).count() for i in range(25)]
    c = (
        Line()
            .add_xaxis(['{}:00'.format(i) for i in range(25)])
            .add_yaxis("发布数量（篇）", article_num, is_smooth=True,
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="微信公众号文章发布时间段", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return c


# 评论率
def comment_rate(biz):
    dynamics = WechatArticleDynamic.query.filter_by(__biz=biz).order_by(WechatArticleDynamic.id.desc()).all()

    keys = []
    values = []
    for dynamic in dynamics:
        keys.append(dynamic.sn)
        if dynamic.read_num == 0 or dynamic.comment_count == None or dynamic.read_num == None:
            values.append(0)
        else:
            values.append((dynamic.comment_count / dynamic.read_num) * 1000)

    c = (
        Line()
            .add_xaxis(keys)
            .add_yaxis("评论率", values, is_smooth=True,
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="公众号评论率", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return c


# 再看率
def like_rate(biz):
    dynamics = WechatArticleDynamic.query.filter_by(__biz=biz).order_by(WechatArticleDynamic.id.desc()).all()

    keys = []
    values = []
    for dynamic in dynamics:
        keys.append(dynamic.sn)
        if dynamic.read_num == 0 or dynamic.like_num == None or dynamic.read_num == None:
            values.append(0)
        else:
            values.append((dynamic.like_num / dynamic.read_num) * 1000)

    c = (
        Line()
            .add_xaxis(keys)
            .add_yaxis("再看率", values, is_smooth=True,
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="公众号再看率", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    return c


# 互动率


# 阅读量分布扇形图0-1k-5k-1w-5w=10w

def readnum_echarts_pie(biz):
    dynamics = WechatArticleDynamic.query.filter_by(__biz=biz).order_by(WechatArticleDynamic.id.desc()).all()
    point0_100 = 0
    point100_500 = 0
    point500_1k = 0
    point1k_5k = 0
    point5k_1w = 0
    point1w_10w = 0
    for dynamic in dynamics:
        if dynamic.read_num == None:
            continue
        if dynamic.read_num <= 100:
            point0_100 += 1
        elif 100 < dynamic.read_num <= 500:
            point100_500 += 1
        elif 500 < dynamic.read_num <= 1000:
            point500_1k += 1
        elif 1000 < dynamic.read_num <= 5000:
            point1k_5k += 1
        elif 5000 < dynamic.read_num <= 10000:
            point5k_1w += 1
        elif 10000 < dynamic.read_num:
            point1w_10w += 1
        else:
            pass

    l = (
        ('0-100', point0_100),
        ('100-500', point100_500),
        ('500-1k', point500_1k),
        ('1k-5k', point1k_5k),
        ('5k-1w', point5k_1w),
        ('1w-10w', point1w_10w),
    )
    c = (
        Pie()

            .add(
            series_name="阅读量",
            radius=["40%", "60%"],
            is_clockwise=False,
            data_pair=l,
            label_opts=opts.LabelOpts(
                position="outside", ))

            .set_global_opts(title_opts=opts.TitleOpts(title="公众号阅读量分布", pos_left='center'),
                             legend_opts=opts.LegendOpts(type_='scroll', is_show=True, pos_left="5%", pos_top='5%',
                                                         orient="vertical"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}")))

    return c


# 发文时间扇形图
def article_hour_num_pie(biz):
    article_num = [WechatArticleList.query.filter_by(__biz=biz).filter(
        and_(
            extract('hour', WechatArticleList.publish_time) == str(i),
        )).count() for i in range(25)]
    resoult = {}
    for _ in range(len(article_num)):
        resoult[_] = article_num[_]

    l = (sorted(resoult.items(), key=itemgetter(1), reverse=True))
    c = (
        Pie()

            .add(
            series_name="时间段",
            radius=["40%", "60%"],
            is_clockwise=False,
            data_pair=l,
            label_opts=opts.LabelOpts(
                position="outside", ))

            .set_global_opts(title_opts=opts.TitleOpts(title="公众号发文时间分布", pos_left='center'),
                             legend_opts=opts.LegendOpts(type_='scroll', is_show=True, pos_left="5%", pos_top='5%',
                                                         orient="vertical"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}")))

    return c


# 文章原创率
def article_yuanchuang_pie(biz):
    yuanchuang_num = WechatArticleList.query.filter_by(__biz=biz).filter_by(copyright_stat=11).count()
    zhaunzai_num = WechatArticleList.query.filter_by(__biz=biz).filter(
        or_(WechatArticleList.copyright_stat == 201, WechatArticleList.copyright_stat == 101)).count()
    putong_num = WechatArticleList.query.filter_by(__biz=biz).filter_by(copyright_stat=100).count()
    qita_num = WechatArticleList.query.filter_by(__biz=biz).filter(and_(WechatArticleList.copyright_stat != 11,
                                                                        WechatArticleList.copyright_stat != 100,
                                                                        WechatArticleList.copyright_stat != 101,
                                                                        WechatArticleList.copyright_stat != 201,
                                                                        )).count()
    l = (
        ('原创', yuanchuang_num),
        ('普通', putong_num),
        ('转载', zhaunzai_num),
        ('其他', qita_num),
    )

    c = (
        Pie()

            .add(
            series_name="时间段",
            radius=["40%", "60%"],
            is_clockwise=False,
            data_pair=l,
            label_opts=opts.LabelOpts(
                position="outside", ))

            .set_global_opts(title_opts=opts.TitleOpts(title="公众号原创率", pos_left='center'),
                             legend_opts=opts.LegendOpts(type_='scroll', is_show=True, pos_left="5%", pos_top='5%',
                                                         orient="vertical"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}")))

    return c


# 大屏展示 本周收录文章统计
def echarts_1():
    today = datetime.date.today()
    x_date_list = [(today - datetime.timedelta(days=i)).strftime('%m-%d') for i in range(7)]
    date_list = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(7)]
    x_date_list.reverse()
    date_list.reverse()

    data_list = [WechatArticle.query.filter(
        and_(extract('year', WechatArticle.spider_time) == str(date).split('-')[0],
             extract('month', WechatArticle.spider_time) == str(date).split('-')[1],
             extract('day', WechatArticle.spider_time) == str(date).split('-')[2],
             )).count() for date in date_list]

    return {"x_data": x_date_list, "y_data": data_list}


# 大屏展示 今日采集文章统计
def echarts_2():
    today = datetime.date.today()
    articles_num = [WechatArticle.query.filter(
        and_(extract('year', WechatArticle.spider_time) == str(today).split('-')[0],
             extract('month', WechatArticle.spider_time) == str(today).split('-')[1],
             extract('day', WechatArticle.spider_time) == str(today).split('-')[2],
             extract('hour', WechatArticle.spider_time) == str(i),
             )).count() for i in range(25)]
    x_date_list = ['{}:00'.format(i) for i in range(25)]
    data_list = articles_num
    return {"x_data": x_date_list, "y_data": data_list}


# 大屏展示 实时访问量
def echarts_5():
    # 迁移日志redis到mysql数据库
    synchronization_log()
    today = datetime.date.today()
    logs_num = [User_Logs.query.filter(
        and_(extract('year', User_Logs.create_time) == str(today).split('-')[0],
             extract('month', User_Logs.create_time) == str(today).split('-')[1],
             extract('day', User_Logs.create_time) == str(today).split('-')[2],
             extract('hour', User_Logs.create_time) == str(i),
             )).count() for i in range(25)]
    x_date_list = ['{}:00'.format(i) for i in range(25)]
    data_list = logs_num
    return {"x_data": x_date_list, "y_data": data_list}


# 大屏展示 本周热搜TOP5
def echarts_6():
    week_ago_date = (datetime.datetime.now() - relativedelta(days=+30)).strftime("%Y-%m-%d %H:%M:%S")
    hot_seach = db.session.query(HotSearch.search, func.count(HotSearch.id)).group_by(
        HotSearch.search).filter(HotSearch.create_time > week_ago_date, HotSearch.page == 1).order_by(
        desc(func.count(HotSearch.id))).limit(
        10).all()
    print(hot_seach)
    x_date_list = []
    y_data_list = []
    if hot_seach:
        # 进行html过滤
        def html_to_plain_text(html):
            text = re.sub('<head.*?>.*?</head>', '', html, flags=re.M | re.S | re.I)
            text = re.sub('<a\s.*?>', ' HYPERLINK ', text, flags=re.M | re.S | re.I)
            text = re.sub('<.*?>', '', text, flags=re.M | re.S)
            text = re.sub(r'(\s*\n)+', '\n', text, flags=re.M | re.S)
            return unescape(text)

        x_date_list = [html_to_plain_text(i[0]) for i in hot_seach]

        max_num = hot_seach[0][1]

        for i in hot_seach:
            y_data_list.append([i[0], int(i[1] / max_num * 100), i[1]])

    return {"x_data": x_date_list, "y_data": y_data_list}


# 大屏展示 采集进度
def echarts_31():
    today = datetime.date.today()
    grabbed_account_task = WechatAccountTask.query.filter(
        and_(extract('year', WechatAccountTask.last_spider_time) == str(today).split('-')[0],
             extract('month', WechatAccountTask.last_spider_time) == str(today).split('-')[1],
             extract('day', WechatAccountTask.last_spider_time) == str(today).split('-')[2]),
        WechatAccountTask.is_zombie == 0
    ).count()  # 今日已经采集过的公众号的数量（最后采集日期等于今日）
    account_task = WechatAccountTask.query.filter_by(is_zombie=0).count()  # 非僵尸号的数量
    is_zombie_task = WechatAccountTask.query.filter_by(is_zombie=1).count()  # 僵尸号的数量
    x_date_list = ['已采集', '未采集', '僵尸号']

    y_data_list = []
    y_data_list.append({"value": grabbed_account_task, "name": '已采集'})
    y_data_list.append({"value": account_task - grabbed_account_task, "name": '未采集'})
    y_data_list.append({"value": is_zombie_task, "name": '僵尸号'})

    return {"x_data": x_date_list, "y_data": y_data_list}


# 大屏展示 原创分类
def echarts_32():
    x_date_list = ['原创', '普通', '转载', '其他']
    y_data_list = []
    yuanchuang_num = WechatArticleList.query.filter_by(copyright_stat=11).count()
    zhaunzai_num = WechatArticleList.query.filter(
        or_(WechatArticleList.copyright_stat == 201, WechatArticleList.copyright_stat == 101)).count()
    putong_num = WechatArticleList.query.filter_by(copyright_stat=100).count()
    qita_num = WechatArticleList.query.filter(and_(WechatArticleList.copyright_stat != 11,
                                                   WechatArticleList.copyright_stat != 100,
                                                   WechatArticleList.copyright_stat != 101,
                                                   WechatArticleList.copyright_stat != 201,
                                                   )).count()

    y_data_list.append({"value": yuanchuang_num, "name": '原创'})
    y_data_list.append({"value": putong_num, "name": '普通'})
    y_data_list.append({"value": zhaunzai_num, "name": '转载'})

    y_data_list.append({"value": qita_num, "name": '其他'})

    return {"x_data": x_date_list, "y_data": y_data_list}


# 大屏展示 公众号分类
def echarts_33():
    x_date_list = []
    y_data_list = []
    tags = WechatTag.query.all()
    for tag in tags:
        x_date_list.append(tag.tag_name)
        y_data_list.append({"value": len(tag.accounts), "name": tag.tag_name})
    return {"x_data": x_date_list, "y_data": y_data_list}


# 同步日志

def synchronization_log():
    from utils.zlcache import hlen, havls, hdel_all

    print(hlen())
    db_cache = []
    for per_log in havls():
        # print(eval(per_log.decode('utf-8')))
        db_cache.append(eval(per_log.decode('utf-8')))
    db.session.bulk_insert_mappings(User_Logs, db_cache)  # 一次性插入多条数据
    db.session.commit()
    hdel_all()


# 过滤原链接，清除个人链接的信息
def url_remove_info(wechat_url):
    '''
    chksm\scene\sessionid\key 去除这个可能代表个人的信息
    :param wechat_url: https://mp.weixin.qq.com/s?__biz=MzU4ODQ3NTM2OA==&mid=2247486203&idx=1&sn=3f48ca14c061ea44aac924eb8e6786f1&chksm=fddd747ccaaafd6ad0889cbf80d22e7cf1e4692a118cae776c46b803130353f993c95125ace8&scene=126&sessionid=1598928777&key=1fb38d1ad08361bbdf714d126c3e54
    :return: https://mp.weixin.qq.com/s?__biz=MzU4ODQ3NTM2OA==&mid=2247486203&idx=1&sn=3f48ca14c061ea44aac924eb8e6786f1
    '''
    pattern = '&chksm=.*&scene=\d+&sessionid=\d+&key=.*'
    no_info_url = re.sub(pattern=pattern, repl='', string=wechat_url)
    return no_info_url


# 过滤原链接，清除个人链接的信息
def url_remove_session(wechat_url):
    '''
    chksm\scene\sessionid\key 去除这个可能代表个人的信息
    :param wechat_url: https://mp.weixin.qq.com/s?__biz=MzU4ODQ3NTM2OA==&mid=2247486203&idx=1&sn=3f48ca14c061ea44aac924eb8e6786f1&chksm=fddd747ccaaafd6ad0889cbf80d22e7cf1e4692a118cae776c46b803130353f993c95125ace8&scene=126&sessionid=1598928777&key=1fb38d1ad08361bbdf714d126c3e54
    :return: https://mp.weixin.qq.com/s?__biz=MzU4ODQ3NTM2OA==&mid=2247486203&idx=1&sn=3f48ca14c061ea44aac924eb8e6786f1
    '''
    pattern = '&scene=\d+&sessionid=\d+&key=.*'
    no_info_url = re.sub(pattern=pattern, repl='', string=wechat_url)
    return no_info_url + '&scene=27#wechat_redirect'
