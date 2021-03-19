# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from datetime import datetime, date

from flask import (
    session,
    views,
    Blueprint,
    current_app
)
from sqlalchemy import or_, not_, extract, and_

import config
from apps.admin.models import WechatArticle, WechatArticleDynamic, WechatAccount
from exts import db
from models import WechatTag, TWechatAccount, Banner, Announcement, HotSearch,Donate
from utils import field, tools

bp = Blueprint('front', __name__, url_prefix='/')


def rules():
    filter_word = ['招聘%']
    rule = not_(*[WechatArticle.title.like(w) for w in filter_word])
    return rule


def anaysis(articless, flag=None):
    '''
    in查询文章的信息，falg不存在默认返回阅读量，查询的次数多一次。若flag存在只返回一个articles数据库中的信息
    :param articless:
    :param flag:
    :return:
    '''
    article_data = []
    if flag:
        for i in articless:
            article = {}
            article['title'] = i.title
            article['biz'] = i.__biz
            article['account_name'] = i.account
            article['id'] = i.sn
            article['publish_time'] = str(i.publish_time)
            article['url'] = tools.url_remove_info(i.url)
            article_data.append(article)
    else:
        dynamics = WechatArticleDynamic.query.filter(WechatArticleDynamic.sn.in_(set([x.sn for x in articless]))).all()
        for i in articless:
            # dynamic = WechatArticleDynamic.query.filter_by(sn=i.sn).first()
            article = {}
            if i.title == '' or i.title==None:
                article['title'] = '分享的图片、视频、链接'
            else:
                article['title'] = i.title
            if i.author == ''or i.author==None:
                article['author'] = '匿名'
            else:
                article['author'] = i.author
            if i.digest == ''or i.digest==None:
                article['digest'] = '&nbsp; &nbsp;'
            else:
                article['digest'] = i.digest
            article['biz'] = i.__biz
            article['cover'] = i.cover
            article['url'] = tools.url_remove_info(i.url)
            article['publish_time'] = str(i.publish_time)
            article['account_name'] = i.account
            article['id'] = i.sn

            for dynamic in dynamics:
                if dynamic.sn == i.sn:
                    if dynamic.read_num:
                        article['like'] = dynamic.like_num
                        article['read'] = dynamic.read_num
                    else:
                        article['like'] = 0
                        article['read'] = 0
                    break
                else:
                    article['like'] = 0
                    article['read'] = 0
            article_data.append(article)
    return article_data


@bp.route('/')
def index():
    today = date.today()
    tag = WechatTag.query.all()
    account_num = TWechatAccount.query.count()
    article_num = WechatArticle.query.count()
    new_num = WechatArticle.query.filter(extract('year', WechatArticle.publish_time) == today.year,
                                         extract('month', WechatArticle.publish_time) == today.month,
                                         extract('day', WechatArticle.publish_time) == today.day).count()
    announcement = Announcement.query.filter(Announcement.flag == 1).order_by(Announcement.time.desc()).first()
    tag_style = ['layui-badge layui-bg-blue', 'layui-badge', 'layui-badge layui-bg-orange',
                 'layui-badge layui-bg-green', 'layui-badge layui-bg-cyan', 'layui-badge layui-bg-black']
    banners = Banner.query.order_by(Banner.priority.desc()).all()
    context = {
        'tags': tag,
        'tag_style': tag_style,
        'account_num': account_num,
        'article_num': article_num,
        'new_num': new_num,
        'announcement': announcement,
        'banners': banners

    }
    return render_template('front/front_index.html', **context)


# 公众号下的所有文章
@bp.route('articles/')
def account_articles():
    id = request.args.get('id')
    flag = request.args.get('flag')
    rule = rules()
    if id:
        article_obj = WechatArticle.query.filter_by(__biz=id).filter(rule).filter(WechatArticle.is_hide == 0).order_by(
            WechatArticle.publish_time.desc())
    else:
        article_obj = WechatArticle.query.filter(rule).filter(WechatArticle.is_hide == 0).order_by(
            WechatArticle.publish_time.desc())

    page = int(request.args.get('page'))
    limit = current_app.config['FRONT_ARTICLES']
    start = (page - 1) * limit
    end = start + limit
    articles = article_obj.slice(start, end)
    pages = int(article_obj.count() / limit) + 1
    if flag:
        article_data = anaysis(articles, flag=flag)
    else:
        article_data = anaysis(articles)
    return field.layui_success(message='', data=article_data, count=pages)


# 类型标签
@bp.route('tags/')
def tag_articles():
    cat_id = request.args.get('cat_id')
    rule = rules()
    cat = WechatTag.query.get(cat_id)
    # article_obj = []
    # for account in cat.accounts:
    #     article = WechatArticle.query.filter_by(__biz=account.account_id).filter(rule).order_by(WechatArticle.publish_time.desc())
    #     article_obj += article
    # article_obj = list(filter(lambda x:x.publish_time, article_obj))
    # article_obj.sort(key=lambda x:x.publish_time if x.publish_time else x.spider_time, reverse=True)  #时间排序
    # page = int(request.args.get('page'))
    # limit = config.config['production'].FRONT_ARTICLES
    # start = (page - 1) * limit
    # end = start + limit
    # articles = article_obj[start:end]  #切片查询
    # pages = int(len(article_obj) / limit) + 1
    # article_data = anaysis(articles)
    article = WechatArticle.query.filter(WechatArticle.__biz.in_(set([i.account_id for i in cat.accounts]))).filter(
        rule).filter(WechatArticle.is_hide == 0).order_by(WechatArticle.publish_time.desc())
    page = int(request.args.get('page'))
    limit = current_app.config['FRONT_ARTICLES']
    start = (page - 1) * limit
    end = start + limit
    data = article.slice(start, end)  # 切片查询
    pages = int(article.count() / limit) + 1
    article_data = anaysis(data)
    return field.layui_success(message='', data=article_data, count=pages)


# 获取指定ID文章的内容
@bp.route('article_id/')
def article_id():
    # TODO：必须登录用户才能够查看快照功能
    id = request.args.get('id')
    if id:
        article = WechatArticle.query.filter_by(sn=id).filter(WechatArticle.is_hide == 0).first()
        if article:
            article_dict = {}
            article_dict['title'] = article.title
            if article.author == '':
                article_dict['author'] = '匿名'
            else:
                article_dict['author'] = article.author
            article_dict['publish_time'] = str(article.publish_time)
            article_dict['account_name'] = article.account
            article_dict['url'] = article.url
            article_dict['content_html'] = tools.filter_html(article.content_html)
            article_dict['id'] = article.__biz
            return field.success(message='', data=article_dict)
        else:
            return field.params_error(message='没有该文章！')
    return field.params_error(message='参数错误！')


# 获取指定ID文章内容,用于首页文章跳转
@bp.route('article/')
def article():
    id = request.args.get('id')
    if id:
        article = WechatArticle.query.filter_by(sn=id).filter(WechatArticle.is_hide == 0).first()
        announcement = Announcement.query.order_by(Announcement.time.desc()).first()
        if article:
            context = {
                'article': article,
                'announcement': announcement
            }
            return render_template('front/front_article.html', **context)
        else:
            return field.params_error(message='没有找到相关文章！')
    else:
        return field.params_error(message='参数错误！')


# 前台搜索
@bp.route('search/', methods=["GET", "POST"])
def search():
    if request.method == 'GET':
        # 不在使用GET的请求方式
        keyword = request.args.get('keyword')
        print(keyword)
        if keyword:
            if "amp" in keyword:
                # 将查找关键字变为多条件合并查找；&分割关键字
                keyword_list = (keyword.strip()).split('amp')
                article_obj = WechatArticle.query
                for per_keyword in keyword_list:
                    find_filter = []
                    per_keyword = per_keyword
                    find_filter.append(WechatArticle.title.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.author.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.account.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.digest.like("%" + per_keyword + "%"))
                article_obj = article_obj.filter(WechatArticle.title.like("%" + "聚合" + "%"))
                # article_obj = article_obj.filter(or_(*find_filter)).filter(WechatArticle.title.like("%" + "聚合" + "%"))
                article_obj = article_obj.order_by(WechatArticle.publish_time.desc())
            else:

                # 将查找关键字变为多条件或查找；|分割关键字
                keyword_list = (keyword.strip()).split('|')
                find_filter = []
                for per_keyword in keyword_list:
                    per_keyword = per_keyword
                    find_filter.append(WechatArticle.title.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.author.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.account.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.digest.like("%" + per_keyword + "%"))

                article_obj = WechatArticle.query.filter(or_(*find_filter
                                                             )).order_by(WechatArticle.publish_time.desc())

            page = int(request.args.get('page'))
            limit = current_app.config['FRONT_ARTICLES']
            start = (page - 1) * limit
            end = start + limit
            articles = article_obj.slice(start, end)
            count = article_obj.count()
            pages = int(count / limit) + 1
            if count > 0:
                article_data = anaysis(articles)
                return field.layui_success(message='共查询到 {} 条相关信息'.format(count), data=article_data, count=pages)
            else:
                return field.layui_success(message='没有找到相关信息！', count=0)
    else:
        # 由于get的传参方式会将&隐藏所以我们尝试该传输参数的方式
        data = request.values
        keyword = data.get('keyword')
        page = int(data.get('page'))
        print(keyword)
        if keyword:
            if "&" in keyword:
                # 将查找关键字变为多条件合并查找；&分割关键字
                keyword_list = keyword.split('&')
                article_obj = WechatArticle.query
                article_obj = article_obj.filter(WechatArticle.is_hide == 0)
                all_filter = []
                for per_keyword in keyword_list:
                    find_filter = []
                    per_keyword = per_keyword.strip()
                    find_filter.append(WechatArticle.title.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.author.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.account.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.digest.like("%" + per_keyword + "%"))
                    all_filter.append(or_(*find_filter))
                article_obj = article_obj.filter(and_(*all_filter))
                article_obj = article_obj.order_by(WechatArticle.publish_time.desc())
            else:

                # 将查找关键字变为多条件或查找；|分割关键字
                keyword_list = keyword.split('|')
                find_filter = []
                for per_keyword in keyword_list:
                    per_keyword = per_keyword.strip()
                    find_filter.append(WechatArticle.title.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.author.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.account.like("%" + per_keyword + "%"))
                    find_filter.append(WechatArticle.digest.like("%" + per_keyword + "%"))

                article_obj = WechatArticle.query.filter(or_(*find_filter
                                                             )).filter(WechatArticle.is_hide == 0).order_by(
                    WechatArticle.publish_time.desc())
            limit = current_app.config['FRONT_ARTICLES']
            start = (page - 1) * limit
            end = start + limit
            articles = article_obj.slice(start, end)
            count = article_obj.count()
            pages = int(count / limit) + 1
            # 添加用户关键字记录
            visitor_id = session.get(current_app.config['VISITOR'])
            keyword_search = HotSearch(search=keyword, page=page, visitor_id=visitor_id, count=count)
            db.session.add(keyword_search)
            db.session.commit()
            if count > 0:
                article_data = anaysis(articles)
                return field.layui_success(message='共查询到 {} 条相关信息'.format(count), data=article_data, count=pages)
            else:
                return field.layui_success(message='没有找到相关信息！', count=0)


@bp.route('get_img/')
def get_img():
    account_id = request.args.get('account_id')
    if account_id:
        account = WechatAccount.query.filter_by(__biz=account_id.strip()).first()
        if account:
            img = account.qr_code
            return field.success(message='查询成功', data={'img': img})
        else:
            return field.params_error('')
    return field.params_error('参数错误')


# 周列表
class WeeklyView(views.MethodView):

    def get(self):
        tag = WechatTag.query.all()
        year = request.args.get('year', config.base_config.Default_YEAR)
        dayOfWeek = datetime.now().isocalendar()
        now_year = dayOfWeek[0]  # 今年的年份
        if config.base_config.Default_MIX_YEAR <= int(year) < now_year:  # 历史年份
            week = 52  # 每年52周
        elif int(year) == now_year:
            print(dayOfWeek)
            week = int(dayOfWeek[1])
            if int(dayOfWeek[2]) < config.base_config.Default_WEEKLY:
                week -= 1
        else:  # 本年分
            year = config.base_config.Default_YEAR
            week = config.base_config.Default_WEEK
        week_list = []
        for w in reversed(range(1, week + 1)):
            friday = (time.strptime('{}-{}-{}'.format(year, w - 1, config.base_config.Default_WEEKLY), '%Y-%U-%w'))
            week_list.append(
                {"year": year, "week": w, 'friday': '{}-{}-{}'.format(friday[0], friday[1], friday[2])}
            )
        content = {
            'week_list': week_list,
            'tags': tag
        }
        return render_template('front/front_weekly.html', year=dayOfWeek[0], week=int(dayOfWeek[1]), **content)

    def post(self):
        pass


# 每周精选文章详情
class WeeklyDetailView(views.MethodView):

    def get(self):
        tag = WechatTag.query.all()
        year = request.args.get('year', config.base_config.Default_YEAR)  # 2016 2018  2019 2020 20222
        week = request.args.get('week', config.base_config.Default_WEEK)
        year = int(year)
        week = int(week)

        dayOfWeek = datetime.now().isocalendar()
        now_year = dayOfWeek[0]  # 今年的年份
        now_week = int(dayOfWeek[1])

        if config.base_config.Default_MIX_YEAR <= year < now_year:  # 历史年份
            if 0 < week <= 52:
                week = week
            else:  # 默认年分
                year = config.base_config.Default_YEAR
                week = config.base_config.Default_WEEK
        elif year == now_year:  # 本年分
            if 0 < week < int(dayOfWeek[1]):
                week = week
            elif week == int(dayOfWeek[1]):
                if int(dayOfWeek[2]) < config.base_config.Default_WEEKLY:
                    week = config.base_config.Default_WEEK
                else:
                    week = week
            else:  # 默认年分
                year = config.base_config.Default_YEAR
                week = config.base_config.Default_WEEK
        else:  # 默认年分
            year = config.base_config.Default_YEAR
            week = config.base_config.Default_WEEK

        week_day = time.strptime('{year}-{week}-{Default_WEEKLY}'.format(year=year, week=week - 1,
                                                                         Default_WEEKLY=config.base_config.Default_WEEKLY),
                                 '%Y-%U-%w')
        wechat_article = WechatArticle.query.filter(WechatArticle.flag == 1).filter(WechatArticle.is_hide == 0).filter(
            and_(extract('year', WechatArticle.publish_time) == year,
                 extract('week', WechatArticle.publish_time) == int(week) - 1,
                 )).order_by(WechatArticle.publish_time.desc()).all()  #

        content = tools.weekily_work(year=year, week=week, week_day=week_day, wechat_article=wechat_article)  # 周报排版
        return render_template('front/front_weekly_detail.html', content=content, tags=tag)

    def post(self):
        pass


# 公告内容
class AnnouncementView(views.MethodView):

    def get(self):
        tag = WechatTag.query.all()
        annocuncements = Announcement.query.filter(Announcement.flag == 1).order_by(Announcement.time.desc()).all()
        return render_template('front/front_announcement.html', annocuncements=annocuncements, tags=tag)

    def post(self):
        pass


# 捐助信息
class DonateView(views.MethodView):

    def get(self):
        donates = Donate.query.filter(Donate.hide == 0).order_by(Donate.pay_time.desc()).all()
        return render_template('front/front_donate.html', donates=donates)

    def post(self):
        pass

# 快速关注公众号 wechat_github
class WechatGithubView(views.MethodView):

    def get(self):
        tag = WechatTag.query.all()
        content = tools.follow_wechat()
        return render_template('front/front_wechat_github.html', content=content, tags=tag)


# 年报总结 year_report
class YearReportView(views.MethodView):

    def get(self):
        return render_template('front/2019.html')


# 公众号展示 account_list

class AccountListView(views.MethodView):
    '''
    [ {'tag':'asd','accounts':[{'name':'xx','img':'img'}]}]
    '''

    def get(self):
        tags = WechatTag.query.all()
        new_tags = []
        for tag in tags:
            tag_dict = dict()
            account_list = list()
            account = WechatAccount.query.filter(
                getattr(WechatAccount, '__biz').in_(set([i.account_id for i in tag.accounts])))
            for i in account:
                account_dict = dict()
                account_dict['account'] = i.account
                account_dict['head_url'] = i.head_url

                account_dict['summary'] = i.summary
                account_dict['qr_code'] = i.qr_code
                account_dict['verify'] = i.verify
                print(i.verify)
                account_dict['spider_time'] = i.spider_time
                account_list.append(account_dict)
            tag_dict['tag_name'] = tag.tag_name
            tag_dict['accounts'] = account_list
            new_tags.append(tag_dict)
        return render_template('front/front_account_list.html', tags=new_tags)


# 精选文章
bp.add_url_rule('weekly/', view_func=WeeklyView.as_view('weekly'))  # 周列表
bp.add_url_rule('weekly_detail/', view_func=WeeklyDetailView.as_view('weekly_detail'))  # 每周精选文章详情

# 公告模块
bp.add_url_rule('announcement/', view_func=AnnouncementView.as_view('announcement'))  # 公告展示

# 捐助模块
bp.add_url_rule('donate/', view_func=DonateView.as_view('donate'))  # 捐助展示

# 快速关注公众号（彩蛋 ）
bp.add_url_rule('wechat_github/', view_func=WechatGithubView.as_view('wechat_github'))  # 快速关注公众号

# 2019年报（公众号图表总结 ）
bp.add_url_rule('year_report/', view_func=YearReportView.as_view('year_report'))  # 年报总结

# 公众号展示
bp.add_url_rule('account_list/', view_func=AccountListView.as_view('account_list'))  # 公众号展示

# 前端过滤器
bp.add_app_template_filter(tools.filter_html, 'Html')
bp.add_app_template_filter(tools.markdown2html, 'markdown2html')
bp.add_app_template_filter(tools.url_remove_info, 'url_remove_info')

# 监控内容

from flask import render_template, jsonify, request

from pyecharts.charts import Line, Gauge
import pyecharts.options as opts
import time
import psutil

cpu_percent_dict = {}
net_io_dict = {'net_io_time': [], 'net_io_sent': [], 'net_io_recv': [], 'pre_sent': 0, 'pre_recv': 0, 'len': -1}
disk_dict = {'disk_time': [], 'write_bytes': [], 'read_bytes': [], 'pre_write_bytes': 0, 'pre_read_bytes': 0, 'len': -1}


def cpu():
    now = time.strftime('%H:%M:%S', time.localtime(time.time()))
    cpu_percent = psutil.cpu_percent()
    cpu_percent_dict[now] = cpu_percent
    # 保持在图表中 10 个数据
    if len(cpu_percent_dict.keys()) == 11:
        cpu_percent_dict.pop(list(cpu_percent_dict.keys())[0])


def cpu_line() -> Line:
    now = time.strftime('%Y-%m-%d', time.localtime(time.time()))
    cpu()
    c = (
        Line()
            .add_xaxis(list(cpu_percent_dict.keys()))
            .add_yaxis('', list(cpu_percent_dict.values()), areastyle_opts=opts.AreaStyleOpts(opacity=0.5))
            .set_global_opts(title_opts=opts.TitleOpts(title=now + "CPU负载", pos_left="center"),
                             yaxis_opts=opts.AxisOpts(min_=0, max_=100, split_number=10, type_="value", name='%'))
    )
    return c


def memory():
    memory = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return memory.total, memory.total - (
            memory.free + memory.inactive), memory.free + memory.inactive, swap.total, swap.used, swap.free, memory.percent


def memory_liquid() -> Gauge:
    mtotal, mused, mfree, stotal, sused, sfree, mpercent = memory()
    c = (
        Gauge()
            .add("", [("", mpercent)])
            .set_global_opts(title_opts=opts.TitleOpts(title="内存负载", pos_left="center"))
    )
    return mtotal, mused, mfree, stotal, sused, sfree, c


def net_io():
    now = time.strftime('%H:%M:%S', time.localtime(time.time()))
    # 获取网络信息
    count = psutil.net_io_counters()
    g_sent = count.bytes_sent
    g_recv = count.bytes_recv

    # 第一次请求
    if net_io_dict['len'] == -1:
        net_io_dict['pre_sent'] = g_sent
        net_io_dict['pre_recv'] = g_recv
        net_io_dict['len'] = 0
        return

    # 当前网络发送/接收的字节速率 = 现在网络发送/接收的总字节 - 前一次请求网络发送/接收的总字节
    net_io_dict['net_io_sent'].append(g_sent - net_io_dict['pre_sent'])
    net_io_dict['net_io_recv'].append(g_recv - net_io_dict['pre_recv'])
    net_io_dict['net_io_time'].append(now)
    net_io_dict['len'] = net_io_dict['len'] + 1

    net_io_dict['pre_sent'] = g_sent
    net_io_dict['pre_recv'] = g_recv

    # 保持在图表中 10 个数据
    if net_io_dict['len'] == 11:
        net_io_dict['net_io_sent'].pop(0)
        net_io_dict['net_io_recv'].pop(0)
        net_io_dict['net_io_time'].pop(0)
        net_io_dict['len'] = net_io_dict['len'] - 1


def net_io_line() -> Line:
    net_io()

    c = (
        Line()
            .add_xaxis(net_io_dict['net_io_time'])
            .add_yaxis("发送字节数", net_io_dict['net_io_sent'], is_smooth=True)
            .add_yaxis("接收字节数", net_io_dict['net_io_recv'], is_smooth=True)
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="网卡IO", pos_left="center"),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            yaxis_opts=opts.AxisOpts(type_="value", name='B/2S'),
            legend_opts=opts.LegendOpts(pos_left="left"),
        ))
    return c


def process():
    result = []
    process_list = []
    pid = psutil.pids()
    for k, i in enumerate(pid):
        try:
            proc = psutil.Process(i)
            ctime = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(proc.create_time()))
            process_list.append((str(i), proc.name(), proc.cpu_percent(), proc.memory_percent(), ctime))
        except psutil.AccessDenied:
            pass
        except psutil.NoSuchProcess:
            pass
        except SystemError:
            pass

        process_list.sort(key=process_sort, reverse=True)
    for i in process_list:
        result.append({'PID': i[0], 'name': i[1], 'cpu': i[2], 'mem': "%.2f%%" % i[3], 'ctime': i[4]})

    return jsonify({'list': result})


def process_sort(elem):
    return elem[3]


def disk():
    disk_usage = psutil.disk_usage('/')
    disk_used = 0
    # 磁盘已使用大小 = 每个分区的总和
    partitions = psutil.disk_partitions()
    for partition in partitions:
        partition_disk_usage = psutil.disk_usage(partition[1])
        disk_used = partition_disk_usage.used + disk_used

    now = time.strftime('%H:%M:%S', time.localtime(time.time()))
    count = psutil.disk_io_counters()
    read_bytes = count.read_bytes
    write_bytes = count.write_bytes

    # 第一次请求
    if disk_dict['len'] == -1:
        disk_dict['pre_write_bytes'] = write_bytes
        disk_dict['pre_read_bytes'] = read_bytes
        disk_dict['len'] = 0
        return disk_usage.total, disk_used, disk_usage.free

    # 当前速率=现在写入/读取的总字节-前一次请求写入/读取的总字节
    disk_dict['write_bytes'].append((write_bytes - disk_dict['pre_write_bytes']) / 1024)
    disk_dict['read_bytes'].append((read_bytes - disk_dict['pre_read_bytes']) / 1024)
    disk_dict['disk_time'].append(now)
    disk_dict['len'] = disk_dict['len'] + 1

    # 把现在写入/读取的总字节放入前一个请求的变量中
    disk_dict['pre_write_bytes'] = write_bytes
    disk_dict['pre_read_bytes'] = read_bytes

    # 保持在图表中 50 个数据
    if disk_dict['len'] == 51:
        disk_dict['write_bytes'].pop(0)
        disk_dict['read_bytes'].pop(0)
        disk_dict['disk_time'].pop(0)
        disk_dict['len'] = disk_dict['len'] - 1

    return disk_usage.total, disk_used, disk_usage.free


def disk_line() -> Line:
    total, used, free = disk()

    c = (
        Line(init_opts=opts.InitOpts(width="1680px", height="800px"))
            .add_xaxis(xaxis_data=disk_dict['disk_time'])
            .add_yaxis(
            series_name="写入数据",
            y_axis=disk_dict['write_bytes'],
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            linestyle_opts=opts.LineStyleOpts(),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .add_yaxis(
            series_name="读取数据",
            y_axis=disk_dict['read_bytes'],
            yaxis_index=1,
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
            linestyle_opts=opts.LineStyleOpts(),
            label_opts=opts.LabelOpts(is_show=False),
        )
            .extend_axis(
            yaxis=opts.AxisOpts(
                name_location="start",
                type_="value",
                is_inverse=True,
                axistick_opts=opts.AxisTickOpts(is_show=True),
                splitline_opts=opts.SplitLineOpts(is_show=True),
                name='KB/2S'
            )
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(
                title="磁盘IO",
                pos_left="center",
                pos_top="top",
            ),
            tooltip_opts=opts.TooltipOpts(trigger="axis", axis_pointer_type="cross"),
            legend_opts=opts.LegendOpts(pos_left="left"),
            xaxis_opts=opts.AxisOpts(type_="category", boundary_gap=False),
            yaxis_opts=opts.AxisOpts(type_="value", name='KB/2S'),
        )
            .set_series_opts(
            axisline_opts=opts.AxisLineOpts(),
        )
    )

    return total, used, free, c


@bp.route("/cpu/")
def get_cpu_chart():
    c = cpu_line()
    return c.dump_options_with_quotes()


@bp.route("/memory/")
def get_memory_chart():
    mtotal, mused, mfree, stotal, sused, sfree, c = memory_liquid()
    return jsonify({'mtotal': mtotal, 'mused': mused, 'mfree': mfree, 'stotal': stotal, 'sused': sused, 'sfree': sfree,
                    'liquid': c.dump_options_with_quotes()})


@bp.route("/netio/")
def get_net_io_chart():
    c = net_io_line()
    return c.dump_options_with_quotes()


@bp.route("/process/")
def get_process_tab():
    c = process()
    return c


# # 杀死进程删除
# @bp.route("/delprocess")
# def del_process():
#     pid = request.args.get("pid")
#     os.kill(int(pid), signal.SIGKILL)
#     return jsonify({'status': 'OK'})

@bp.route("/disk/")
def get_disk_chart():
    total, used, free, c = disk_line()
    return jsonify({'total': total, 'used': used, 'free': free, 'line': c.dump_options_with_quotes()})
