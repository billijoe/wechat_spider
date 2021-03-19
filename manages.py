# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

import datetime
import urllib.parse

import jieba.analyse
import matplotlib.pyplot as plt
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from pyecharts import options as opts
from pyecharts.charts import Bar
from pyecharts.charts import Bar3D
from pyecharts.charts import Line
from pyecharts.charts import Pie
from pyecharts.charts import Tab
from pyecharts.charts import Page
from pyecharts.faker import Faker
from sqlalchemy import and_, extract, func, desc,or_
from wordcloud import WordCloud

from __init__app import create_app  # 进行部分数据库初始化
from apps.admin.models import WechatArticle, WechatArticleList, WechatArticleComment, WechatArticleDynamic
# from app import create_app
from exts import db
from models import Admin, TWechatAccount, WechatTag, User_Logs
from utils import zlcache

app = create_app()

manager = Manager(app)
Migrate(app, db)
manager.add_command('db', MigrateCommand)


# 创建后台管理员用户
@manager.option('-u', '--username', dest='username')
@manager.option('-p', '--password', dest='password')
@manager.option('-e', '--email', dest='email')
def create_admin(username, password, email):
    # avatar = GithubAvatarGenerator()
    # path = '..' + sep +'static'+ sep+ 'admin'+sep +'image'+ sep + email +'.png'
    # avatar.save_avatar(filepath='.' + sep +'static'+ sep+ 'admin'+sep +'image'+ sep + email +'.png')
    user = Admin(username=username, password=password, email=email)
    db.session.add(user)
    db.session.commit()
    print('Admin添加成功！！！')


tags = [
    {'tag_name': '媒体社区类', 'tag_en': 'media', 'tag_summary': '媒体、资讯、社区'},
    {'tag_name': '安全公司类', 'tag_en': 'org', 'tag_summary': '安全公司官方微信'},
    {'tag_name': '应急响应类', 'tag_en': 'src', 'tag_summary': '应急响应中心、应急响应技术'},
    {'tag_name': '安全团队类', 'tag_en': 'team', 'tag_summary': '公司安全研究团队、实验室'},
    {'tag_name': '高校社团类', 'tag_en': 'school', 'tag_summary': '高校网络安全社团'},
    {'tag_name': 'CTF类', 'tag_en': 'ctf', 'tag_summary': 'CTF赛事、writeup、技巧'},
    {'tag_name': '个人类', 'tag_en': 'person', 'tag_summary': '个人、技术分享'},
    {'tag_name': 'web安全类', 'tag_en': 'web', 'tag_summary': 'web漏洞、业务安全、前端安全'},
    {'tag_name': '网络运维类', 'tag_en': 'operation', 'tag_summary': '运维、操作系统、加固'},
    {'tag_name': '安全研发类', 'tag_en': 'program', 'tag_summary': '开发、后端、业务安全、安全研发规范'},
    {'tag_name': '二进制安全类', 'tag_en': 'bin', 'tag_summary': '汇编、逆向、溢出、破解'},
    {'tag_name': '硬件安全类', 'tag_en': 'hardware', 'tag_summary': '路由器、工控、摄像头、无线电'},
    {'tag_name': '其他', 'tag_en': 'other', 'tag_summary': '杂项'},
]
accounts = [
    {"account_id": "MzI5MDQ2NjExOQ==", "account_name": "信安之路", "tag": 1},
    {"account_id": "MzI0NzEwOTM0MA==", "account_name": "雷神众测", "tag": 1},
    {"account_id": "MzAxNTcyNzAyOQ==", "account_name": "运维", "tag": 1},
    {"account_id": "Mzg5MTA3NTg2MA==", "account_name": "Secquan圈子社区", "tag": 1},
    {"account_id": "MzIzNjUxMzk2NQ==", "account_name": "高效开发运维", "tag": 1},
    {"account_id": "MzIxMzQ3MzkwMQ==", "account_name": "MottoIN", "tag": 1},
    {"account_id": "MzA5ODA0NDE2MA==", "account_name": "安全客", "tag": 1},
    {"account_id": "MjM5NTc2MDYxMw==", "account_name": "看雪学院", "tag": 1},
    {"account_id": "MzAxOTM1MDQ1NA==", "account_name": "黑鸟", "tag": 1},
]


@manager.option('-i', '--init', dest='init')
def init_db(init):
    # 初始化数据库
    user = Admin(username='1111111', password='1111111', email='1111111@qq.com')
    db.session.add(user)
    db.session.commit()
    for tag in tags:
        add_tag = WechatTag(tag_name=tag.get('tag_name'), tag_en=tag.get('tag_en'), tag_summary=tag.get('tag_summary'))
        db.session.add(add_tag)
        print('添加标签{}'.format(tag.get('tag_name')))
    db.session.commit()
    for account in accounts:
        add_account = TWechatAccount(account_id=account.get("account_id"), account_name=account.get('account_name'),
                                     tag=account.get('tag'))
        db.session.add(add_account)
    db.session.commit()

    print('添加成功')


@manager.option('-t', '--test', dest='test')
def add_account(test):
    # 读取公众号的列表
    print('添加成功')


# h获得历史天数收录的文章数
@manager.option('-y', '--year', dest='year')
@manager.option('-m', '--month', dest='month')
@manager.option('-d', '--day', dest='day')
def get_articles_num(year, month, day):
    starttime = datetime.datetime.strptime('{}-{}-{}'.format(year, month, day), '%Y-%m-%d')
    endtime = datetime.datetime.now()

    while starttime < endtime:
        articles_num = WechatArticle.query.filter(
            and_(extract('year', WechatArticle.spider_time) == str(starttime).split('-')[0],
                 extract('month', WechatArticle.spider_time) == str(starttime).split('-')[1],
                 extract('day', WechatArticle.spider_time) == str(starttime).split('-')[2],
                 )).count()

        zlcache.set(key=str(starttime)[0:10], value=articles_num, timeout=None)
        starttime += datetime.timedelta(days=1)


# 生词词云 某年 某月的标题
@manager.option('-t', '--top', dest='top')
def account_title_wc(top):
    print('正在获取标题词云')
    articles = WechatArticleList.query.filter(
        and_(extract('year', WechatArticleList.publish_time) == '2020',

             )).with_entities(WechatArticleList.title).all()
    print('正在生成标题词云')
    text = ','.join([i.title for i in articles])
    result = jieba.analyse.textrank(text, topK=int(top), withWeight=True)
    keywords = dict()
    for i in result:
        keywords[i[0]] = i[1]
    wc = WordCloud(font_path='./utils/captcha/simhei.ttf', max_words=int(top), width=805, height=304)
    wc.generate_from_frequencies(keywords)
    plt.imshow(wc)
    plt.axis("off")
    wc.to_file('./static/front/img/dream.png')
    print('词云图生成完成')


# 每个公众号发的文章数分析。年度最勤快公众号（）
@manager.command
def account_article_num():
    account = db.session.query(WechatArticle.account, func.count(WechatArticle.id)) \
        .filter(extract('year', WechatArticle.publish_time) == '2019').group_by(
        WechatArticle.account).order_by(desc(func.count(WechatArticle.id))).all()
    keys = []
    values = []
    for key, value in account:
        keys.append(key)
        values.append(value)
    print('文章公众号总数',len(keys),sum(values), values)
    bar = (
        Bar({"width": "1500px", "height": "700px"})
            .add_xaxis(keys)
            .add_yaxis(series_name="文章数量(/篇)", yaxis_data=values, category_gap='10%')
            .set_global_opts(
            title_opts=opts.TitleOpts(title="2019年公众号收录文章数", pos_top='10%', pos_left='43%'),
            xaxis_opts=opts.AxisOpts(name='公众号名称', name_rotate=-90,
                                     axislabel_opts={'rotate': -45}),
            yaxis_opts=opts.AxisOpts(name="文章数量(/篇)"),
            legend_opts=opts.LegendOpts(is_show=False),
            datazoom_opts=[opts.DataZoomOpts(type_="inside")],
        )
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ), ))
    # bar.render(path='./static/year/account_article_num.html')
    print('生成公众号收录文章数')
    return bar


# 每天发布文章的数量
@manager.command
def article_day_num():
    today = datetime.datetime.strptime('2019-12-31', '%Y-%m-%d')
    date_list = [(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d') for i in range(365)]
    date_list.reverse()

    data_list = [WechatArticle.query.filter(
        and_(extract('year', WechatArticle.publish_time) == str(date).split('-')[0],
             extract('month', WechatArticle.publish_time) == str(date).split('-')[1],
             extract('day', WechatArticle.publish_time) == str(date).split('-')[2],
             )).count() for date in date_list]

    c = (
        Line({"width": "1500px", "height": "700px"})
            .add_xaxis(xaxis_data=date_list)
            .add_yaxis("文章数(篇)", data_list, is_smooth=True, color='#66CDAA',
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="2019年每天收录文章统计", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    c.render(path='./static/year/article_day_num.html')
    print('生成每天收录文章统计')
    return c


# 公众号发布文章的时间段
@manager.command
def article_hour_num():
    logs_num = [WechatArticle.query.filter(
        and_(extract('year', WechatArticle.publish_time) == '2019',
             extract('hour', WechatArticle.publish_time) == str(i),
             )).count() for i in range(25)]
    c = (
        Line({"width": "1500px", "height": "700px"})
            .add_xaxis(['{}:00'.format(i) for i in range(25)])
            .add_yaxis("发布数量（篇）", logs_num, is_smooth=True,
                       label_opts=opts.LabelOpts(is_show=False))
            .set_series_opts(
            areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="2019年微信公众号文章发布时间段", pos_left='43%', pos_top='8%'),
            xaxis_opts=opts.AxisOpts(
                axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
                is_scale=False,
                boundary_gap=False,
            ),
            legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    c.render(path='./static/year/article_hour_num.html')
    print('生成文章发布时间段')
    return c


# 公众号文章是否有原文？原文链接中各大平台占比例
@manager.command
def article_source_url():
    article_num = WechatArticle.query.filter(extract('year', WechatArticle.publish_time) == '2019', ).count()
    article_source_url_num = WechatArticle.query.filter(
        and_(WechatArticle.source_url != '', extract('year', WechatArticle.publish_time) == '2019', )).count()
    article_source_url_list = WechatArticle.query.filter(
        and_(WechatArticle.source_url != '', extract('year', WechatArticle.publish_time) == '2019', )).with_entities(
        WechatArticle.source_url).all()
    resoult = {}
    print(article_source_url_list)
    domains = [urllib.parse.urlparse(_.source_url).hostname for _ in article_source_url_list]
    import re
    new_domain = []
    for _ in domains:
        if re.match(r"^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$", _):
            new_domain.append(_)
            continue
        print(_)
        if _.endswith('cn'):
            try:
                new_domain.append(_.split('.')[-3] + '.' + (_.split('.')[-2] + '.' + _.split('.')[-1]))
            except:
                new_domain.append((_.split('.')[-2] + '.' + _.split('.')[-1]))
        else:
            new_domain.append((_.split('.')[-2] + '.' + _.split('.')[-1]))
    print(new_domain)
    for _ in new_domain:
        print(_)
        resoult[_] = new_domain.count(_)
    print(resoult)

    from operator import itemgetter
    l = (sorted(resoult.items(), key=itemgetter(1), reverse=True))
    # zip1 = zip(resoult.keys(), resoult.values(), )  # zip
    # l = list(zip1)
    # res = sorted(l, reverse=True)

    # print(dict(res))

    print(article_num)
    print(article_source_url_num)
    c = (
        Pie({"width": "1700px", "height": "900px"})
            .add(
            series_name="文章来源",
            data_pair=[('有原文文章数', article_source_url_num), ('无原文文章数', article_num - article_source_url_num)],
            radius=[0, "30%"],
            is_clockwise=False,
            label_opts=opts.LabelOpts(position="inner")
        )
            .add(
            series_name="平台来源",
            radius=["40%", "55%"],
            is_clockwise=False,
            data_pair=l[0:30],
            label_opts=opts.LabelOpts(
                position="outside", ))
            .add(
            series_name="小众来源",
            radius=["65%", "85%"],
            is_clockwise=False,
            data_pair=l[31:],
            label_opts=opts.LabelOpts(is_show=False),
        )
            .set_global_opts(title_opts=opts.TitleOpts(title="2019年微信公众号文章原文数占比", pos_left='center'),
                             legend_opts=opts.LegendOpts(type_='scroll', is_show=True, pos_left="5%", pos_top='5%',
                                                         orient="vertical"))
            .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
    )
    c.render(path='./static/year/article_source_url2.html')
    print('生成公众号文章来源')
    return c


# 柱状图L:类似于公众号发文章

# 最奋进的作者（top20）柱状图展示了作者本年度发布文章的数量
@manager.command
def article_author():
    authors = db.session.query(WechatArticle.author, func.count(WechatArticle.id)).filter(
        (and_(WechatArticle.author != '', extract('year', WechatArticle.publish_time) == '2019', ))).group_by(
        WechatArticle.author).order_by(desc(func.count(WechatArticle.id))).all()
    keys = []
    values = []
    for key, value in authors:
        keys.append(key)
        values.append(value)
    print('作者总数量',len(keys), values)
    bar = (
        Bar({"width": "1500px", "height": "700px"})
            .add_xaxis(keys)
            .add_yaxis(series_name="文章数量(/篇)", yaxis_data=values, category_gap='10%')
            .set_global_opts(
            title_opts=opts.TitleOpts(title="勤奋作者", pos_top='10%', pos_left='43%'),
            xaxis_opts=opts.AxisOpts(name='作 者 名 称', name_rotate=-90,
                                     axislabel_opts={'rotate': -45}),
            yaxis_opts=opts.AxisOpts(name="文章数量(/篇)"),
            legend_opts=opts.LegendOpts(is_show=False),
            datazoom_opts=[opts.DataZoomOpts(type_="inside")],
        )
            .set_series_opts(
            label_opts=opts.LabelOpts(is_show=False),
            markline_opts=opts.MarkLineOpts(
                data=[
                    opts.MarkLineItem(type_="average", name="平均值"),
                ]
            ), ))
    # bar.render(path='./static/year/article_author.html')
    print('生成勤奋作者')
    return bar


# 评论的情感分析（正、负、中）

# 评论都在说些什么
@manager.command
def get_commend():
    commends = db.session.query(WechatArticleComment.content).with_entities(WechatArticleComment.content).all()
    for content in commends:
        print(content)
        with open('comment.txt', 'a+', encoding='utf-8', errors='ignore')as f:
            f.write(content[0] + '\n')


# 平台访问地址（地图展示）
@manager.command
def map():
    today = datetime.datetime.now()
    areas = db.session.query(User_Logs.area, func.count(User_Logs.id)).filter(User_Logs.area != '').filter(
        and_(extract('year', User_Logs.create_time) == str(today).split('-')[0],
             extract('month', User_Logs.create_time) == str(today).split('-')[1],
             extract('day', User_Logs.create_time) == str(today).split('-')[2],
             )
    ).group_by(
        User_Logs.area).order_by(desc(func.count(User_Logs.id))).all()
    for k, v in areas:
        print(k, v)


# 阅读量最多、微信点赞数量最多（上半年）  点赞最多的评论。（decon）
@manager.command
def max_read():
    reads = db.session.query(WechatArticleDynamic).order_by(WechatArticleDynamic.read_num.desc()).limit(100).all()
    article_list = db.session.query(WechatArticleList).filter(
        WechatArticleList.sn.in_(set([read.sn for read in reads]))).all()
    for article in article_list:
        print(article.title, )


def max_like():
    likes = db.session.query(WechatArticleDynamic).order_by(WechatArticleDynamic.like_num.desc()).limit(100).all()
    article_list = db.session.query(WechatArticleList).filter(
        WechatArticleList.sn.in_(set([like.sn for like in likes]))).all()
    for article in article_list:
        print(article.title, )


def max_command():
    comments = db.session.query(WechatArticleDynamic).order_by(WechatArticleDynamic.comment_count.desc()).limit(
        100).all()
    article_list = db.session.query(WechatArticleList).filter(
        WechatArticleList.sn.in_(set([comment.sn for comment in comments]))).all()
    for article in article_list:
        print(article.title, )


# 每天收录公众号的3D统计图，每周7天，每52周，每天收录的数量
@manager.command
def article_day_3d():
    today = datetime.datetime.strptime('2019-12-31', '%Y-%m-%d')
    date_list = [[(today - datetime.timedelta(days=i)).strftime('%Y-%m-%d'),
                  (today - datetime.timedelta(days=i)).isocalendar()[1],
                  (today - datetime.timedelta(days=i)).isocalendar()[2]] for i in range(365)]
    date_list.reverse()

    data = [[date[1], date[2], WechatArticle.query.filter(
        and_(extract('year', WechatArticle.publish_time) == str(date[0]).split('-')[0],
             extract('month', WechatArticle.publish_time) == str(date[0]).split('-')[1],
             extract('day', WechatArticle.publish_time) == str(date[0]).split('-')[2],
             )).count()] for date in date_list]
    c = (
        Bar3D()
            .add(
            "",
            [[d[0], d[1]-1, d[2]] for d in data],
            xaxis3d_opts=opts.Axis3DOpts(data=[i for i in range(1, 53)], type_="category",name='一年周期',name_gap=30),
            yaxis3d_opts=opts.Axis3DOpts(data=Faker.week_en, type_="category",name='week'),
            zaxis3d_opts=opts.Axis3DOpts(type_="value",name='每天数量'),
            grid3d_opts=opts.Grid3DOpts(width=300, height=120,depth=120,
                rotate_speed=10, is_rotate=True
            ),
        )
            .set_global_opts(
            visualmap_opts=opts.VisualMapOpts(max_=210, range_color=Faker.visual_color),
            title_opts=opts.TitleOpts(title="2019公众号文章发布统计",pos_top='10%', pos_left='43%'),
            legend_opts=opts.LegendOpts(item_gap=20, item_width=20),
        )
    )
    c.render(path='./static/year/article_day_3d.html')
    print('生成3D文章发布统计')
    return c

def pip_data(keyword='招聘'):


    account = db.session.query(WechatArticle.account, func.count(WechatArticle.id)) \
        .filter(or_(WechatArticle.title.like("%" + keyword + "%"),  # 题目
                                                 WechatArticle.author.like("%" + keyword + "%"),  # 作者
                                                 # WechatArticle.content_html.like("%" + keyword + "%"),
                                                 WechatArticle.account.like("%" + keyword + "%"),  # 公众号
                                                 WechatArticle.digest.like("%" + keyword + "%")  # 描述
                                                 )).group_by(
        WechatArticle.account).order_by(desc(func.count(WechatArticle.id))).all()
    # print(account)
    data =[]
    account_dict ={}
    for k, v in account:
        account_dict[k]= v
    for k,v in account:
        # print(k,v)
        data.append(k)
    return data,account_dict

# 统计发招聘公众号的扇形图
@manager.command
def zhaopin():
    zhaopin_data ,zhaopin_account= pip_data(keyword='招聘')
    cve_data,cve_account = pip_data(keyword='cve')
    yujing_data ,yujing_account= pip_data(keyword='预警')
    loudong_data,loudong_account = pip_data(keyword='漏洞')
    fuxain_data ,fuxain_account= pip_data(keyword='复现')
    zongjie_data,zongjie_account = pip_data(keyword='总结')
    paixu ={}
    quanneng ={}
    accounts_list = list(set(cve_data[0:20]+yujing_data[0:20]+loudong_data[0:20]+fuxain_data[0:20]+zongjie_data[0:20]))
    for i in list(set(cve_data[0:20]+yujing_data[0:20]+loudong_data[0:20]+fuxain_data[0:20]+zongjie_data[0:20])):
        print(i)
        paixu[i]=cve_account.get(i,0)/1094/5+\
        yujing_account.get(i,0)/834/5+\
        loudong_account.get(i,0)/5399/5+\
        fuxain_account.get(i,0)/255/5+\
        zongjie_account.get(i,0)/603/5
        quanneng[i] =[cve_account.get(i,0)/1094*100,
        yujing_account.get(i,0)/834*100,
        loudong_account.get(i,0)/5399*100,
        fuxain_account.get(i,0)/255*100,
        zongjie_account.get(i,0)/603*100,]
        print(cve_account.get(i,0)/1094,
        yujing_account.get(i,0)/834,
        loudong_account.get(i,0)/5399,
        fuxain_account.get(i,0)/255,
        zongjie_account.get(i,0)/603,)

    from operator import itemgetter
    print(sorted(paixu.items(),key=itemgetter(1),reverse=True))
    print('招聘信息条数',(sum(x for x in zhaopin_account.values())))

    print('cve信息条数top20',(sum(cve_account.get(x,0) for x in cve_data[0:20])))
    print('预警信息条数top20',(sum(yujing_account.get(x,0) for x in yujing_data[0:20])))
    print('漏洞信息条数top20',(sum(loudong_account.get(x,0) for x in loudong_data[0:20])))
    print('复现信息条数top20',(sum(fuxain_account.get(x,0) for x in fuxain_data[0:20])))
    print('总结信息条数top20',(sum(zongjie_account.get(x,0) for x in zongjie_data[0:20])))
    print('预警信息条数',(sum(x for x in yujing_account.values())))
    print('漏洞信息条数',(sum(x for x in loudong_account.values())))
    print('复现信息条数',(sum(x for x in fuxain_account.values())))
    print('总结信息条数',(sum(x for x in zongjie_account.values())))
#     c = (
#         Pie({"width": "1700px", "height": "900px"})
#
#         .add(
#             "‘cve’发布统计",
#
#             cve_data[0:20],
#             radius=[46, 80],
#             center=["30%", "30%"],
#             is_clockwise=False,
#             label_opts=opts.LabelOpts(is_show=False),
#         )
#
#             .add(
#             "‘预警’发布统计",
#             yujing_data[0:20],
#             radius=[46, 80],
#             center=["58%", "30%"],
#             is_clockwise=False,
#             label_opts=opts.LabelOpts(is_show=False),
#         )
#             .add(
#             "‘漏洞’发布统计",
#             loudong_data[0:20],
#             radius=[46, 80],
#             center=["85%", "30%"],
#             is_clockwise=False,
#             label_opts=opts.LabelOpts(is_show=False),
#         )
#             .add(
#             "‘复现’发布统计",
#             fuxain_data[0:20],
#             radius=[46, 80],
#             center=["30%", "70%"],
#             is_clockwise=False,
#             label_opts=opts.LabelOpts(is_show=False),
#         )
#             .add(
#             "‘总结’发布统计",
#             zongjie_data[0:20],
#             radius=[46, 80],
#             center=["58%", "70%"],
#             is_clockwise=False,
#             label_opts=opts.LabelOpts(is_show=False),
#         )
#             .add(
#             "‘招聘’发布统计",
#             zhaopin_data[0:20],
#             radius=[46, 80],
#             center=["85%", "70%"],
#             is_clockwise=False,
#             label_opts=opts.LabelOpts(is_show=False),
#         )
#         .set_global_opts(title_opts=opts.TitleOpts(title="2019年微信公众号文章主题数据统计图(top20)", pos_left='center'),
#                              legend_opts=opts.LegendOpts(type_='scroll', is_show=True, pos_left="5%", pos_top='5%',
#                                                          orient="vertical"))
#             .set_series_opts(label_opts=opts.LabelOpts(formatter="{b}: {c}"))
#     )
#
#
# #    page = Page(layout=Page.SimplePageLayout)
#     # 需要自行调整每个 chart 的 height/width，显示效果在不同的显示器上可能不同
#  #   page.add(c)
#  #    c.render(path='./static/year/pie.html')
#     return c
    c = (
        Line({"width": "1500px", "height": "700px"})
            .add_xaxis(['cve','预警','漏洞','复现','总结'])
            .add_yaxis("嘶吼专业版", quanneng['嘶吼专业版'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("FreeBuf", quanneng['FreeBuf'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("邑安全", quanneng['邑安全'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("山石瞭望", quanneng['山石瞭望'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("360CERT", quanneng['360CERT'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("腾讯御见威胁情报中心", quanneng['腾讯御见威胁情报中心'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("绿盟科技", quanneng['绿盟科技'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("Timeline&nbsp;Sec", quanneng['Timeline&nbsp;Sec'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("长亭安全课堂", quanneng['长亭安全课堂'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("合天智汇", quanneng['合天智汇'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("绿盟科技安全情报", quanneng['绿盟科技安全情报'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("E安全", quanneng['E安全'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("信安之路", quanneng['信安之路'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("黑白之道", quanneng['Seebug漏洞平台'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("维他命安全", quanneng['维他命安全'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("无级安全", quanneng['无级安全'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("安全客", quanneng['安全客'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("弥天安全实验室", quanneng['弥天安全实验室'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("HACK学习呀", quanneng['HACK学习呀'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("Tide安全团队", quanneng['Tide安全团队'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("SecPulse安全脉搏", quanneng['SecPulse安全脉搏'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("雷神众测", quanneng['雷神众测'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("安全祖师爷", quanneng['安全祖师爷'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("洛米唯熊", quanneng['洛米唯熊'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("飓风网络安全", quanneng['飓风网络安全'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("网信防务", quanneng['网信防务'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("小白帽学习之路", quanneng['小白帽学习之路'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))
            .add_yaxis("西子实验室", quanneng['西子实验室'], is_smooth=True,label_opts=opts.LabelOpts(is_show=False))

        #     .set_series_opts(
        #     areastyle_opts=opts.AreaStyleOpts(opacity=0.5),
        # )
            .set_global_opts(
            title_opts=opts.TitleOpts(title="2019年微信公众号主题折线图", pos_left='43%', pos_top='8%'),
            # xaxis_opts=opts.AxisOpts(
            #     axistick_opts=opts.AxisTickOpts(is_align_with_label=True),
            #     is_scale=False,
            #     boundary_gap=False,
            # ),
            # legend_opts=opts.LegendOpts(is_show=False),
        )
    )
    c.render(path='./static/year/quanneng.html')
    print('生成全能公众号')


# 统计发cve公众号的扇形图
@manager.command
def cve():
    cve_data = pip_data(keyword='cve')
    print(cve_data)

# 统计发复现公众号的扇形图
@manager.command
def fuxian():
    fuxain_data = pip_data(keyword='复现')
    print(fuxain_data)

# 综合图表展示
# 将所有的图表展示在一张html中。
@manager.command
def all():
    tab = Tab(page_title='2019年安全公众号统计分析')
    tab.add(article_day_3d(), "公众号文章发布统计")
    tab.add(account_article_num(), "公众号收录文章数")
    tab.add(article_day_num(), "每天收录文章统计")
    tab.add(article_hour_num(), "文章发布时间段")
    tab.add(article_source_url(), "公众号文章来源")
    tab.add(zhaopin(), "公众号文章主题统计")
    tab.add(article_author(), "勤奋作者")
    tab.render(path='./static/year/2019.html')
    print('生成完毕')

#  日志更新地址
@manager.command
def email():
    from utils import send_email

    send_email.send_reemail(['1599121712@qq.com'])
    # send_email.asy_send_email(['1599121712@qq.com'])
    print('发送邮件')
if __name__ == '__main__':
    manager.run()
