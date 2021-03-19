# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/9 14:21
@Auth ： AJay13
@File ：interface_article_list.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

# 统计的数据接口：

# 收录的文章总数、收录公众号、分类、评论数量
# 另外 社区提交公众号数、已收录公众号数量、监控公众号数量、已采集公众号数量、评论数量、爬取任务数量、带爬取文章数量、爬取中数量、抓取完毕数量、gituhb同步次数、贡献者人数、日志总访问次数、用户搜索次数、留言数量、黑名单数量

# echart数据

# 实时监控数据

__all__ = ['InterfaceCount', 'InterfaceSystemInfo','InterfaceTopSearch']
import datetime
from utils import tools
import psutil
from flask import views
from sqlalchemy import and_
from sqlalchemy import extract

from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.account.verify_account import ArticleFlagForm
from apis.v1.home.verify_home import HotSearchListForm,ArticleListForm
from apps.admin.models import WechatAccountTask, WechatArticleComment, WechatArticleTask, WechatArticle, WechatAccount,WechatArticleDynamic
from exts import db
from models import GitCommit, TCommunityWechatAccount, WechatTag, HotSearch, TWechatAccount, Announcement,User_Logs
from sqlalchemy import and_, extract, func, desc, or_

## 首页数据统计
class InterfaceCount(views.MethodView):
    '''
    统计数据接口
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        today = datetime.date.today()
        try:  # 当初始化的时候，后台不存在迁移的数据库。
            # if 1==1:
            wechat_article_num = WechatArticle.query.count()  # 文章数量
            tag_num = WechatTag.query.count()  # 分类数量
            account_num = WechatAccount.query.count()  # 微信数量
            comment_num = WechatArticleComment.query.count()  # 微信评论总数量
            article_task_num = WechatArticleTask.query.count()  # 公众号文章爬取任务数量
            to_grab_task_num = WechatArticleTask.query.filter_by(state=0).count()  # 待抓取公众号任务数量
            grabbed_task_num = WechatArticleTask.query.filter_by(state=1).count()  # 抓取完毕任务数量
            grabbing_task_num = WechatArticleTask.query.filter_by(state=2).count()  # 抓取中的任务数量
            contribution_num = TCommunityWechatAccount.query.with_entities(
                TCommunityWechatAccount.founder).distinct().count() - 1  # 贡献者人数总数量 -1位空白的人员
            grabbed_account_task = WechatAccountTask.query.filter(
                and_(extract('year', WechatAccountTask.last_spider_time) == str(today).split('-')[0],
                     extract('month', WechatAccountTask.last_spider_time) == str(today).split('-')[1],
                     extract('day', WechatAccountTask.last_spider_time) == str(today).split('-')[2]),
                WechatAccountTask.is_zombie == 0
            ).count()  # 今日已经采集过的公众号的数量（最后采集日期等于今日）
            account_task = WechatAccountTask.query.filter_by(is_zombie=0).count()  # 非僵尸号的数量
            account_is_zombie = WechatAccountTask.query.filter_by(is_zombie=1).count()  # 僵尸号的数量
        except Exception as e:
            print(e)
            wechat_article_num = 0
            tag_num = 0
            account_num = 0
            comment_num = 0
            article_task_num = 0
            to_grab_task_num = 0
            grabbing_task_num = 0
            grabbed_task_num = 0
            contribution_num = 0
            account_task = 0
            grabbed_account_task = 0
            account_is_zombie = 0

        b = account_task if account_task != 0 else 1
        loading = "%.2f%%" % (grabbed_account_task / b * 100)
        t_announcement = Announcement.query.filter(Announcement.flag == 1).order_by(
            Announcement.time.desc()).first()  # 公告信息
        t_account_num = TWechatAccount.query.count()  # 添加微信数量
        t_community_account_num = TCommunityWechatAccount.query.count()  # 社区提交公众号数量
        t_community_account = TCommunityWechatAccount.query.filter(
            TCommunityWechatAccount.status == '0').count()  # 社区提交公众号未审核
        t_account_start_num = TWechatAccount.query.filter_by(status='start').count()  # 监控微信数量
        git_commit_num = GitCommit.query.count()  # github同步次数
        context = {
            # 'announcement': t_announcement,  # 公告展示
            'wechat_article_num': wechat_article_num,  # 微信文章数量
            'article_task_num': article_task_num,  # 公众号文章爬取总任务数量
            'to_grab_task_num': to_grab_task_num,  # 待抓取文章任务数量
            'grabbing_task_num': grabbing_task_num,  # 抓取中的任务数量
            'grabbed_task_num': grabbed_task_num,  # 抓取完毕任务数量

            't_community_account_num': t_community_account_num,  # 社区提交公众号数量
            't_account_num': t_account_num,  # 收录公众号数量
            'account_num': account_num,  # 有效公众号
            't_account_start_num': t_account_start_num,  # 当前监控微信数量
            'account_is_zombie': account_is_zombie,  # 异常公众号
            't_community_account': t_community_account,  # 社区提交公众号未审核

            'tag_num': tag_num,  # 分类数量
            'git_commit_num': git_commit_num,  # git同步次数
            'contribution_num': contribution_num,  # 参与贡献者的人数数量
            'loading': loading,
            'comment_num': comment_num,  # 评论数量
        }
        return response_code.LayuiSuccess(message='查询成功！', data=context, count=0)


## cpu member数据统计
class InterfaceSystemInfo(views.MethodView):
    '''
    统计数据接口
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        context = {
            "cpu": cpu_percent,
            "memory": memory.percent,
        }
        return response_code.LayuiSuccess(message='查询成功！', data=context, count=0)


# 今日热搜  top_search
class InterfaceTopSearch(views.MethodView):
    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = HotSearchListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)
        print(tools.get_day_zero_time(datetime.datetime.now().date()))
        start = (page - 1) * limit
        end = start + limit
        keyword_data = []
        hot_search = db.session.query(HotSearch.search, func.count(HotSearch.id),func.count(HotSearch.visitor_id)).group_by(
            HotSearch.search).filter(HotSearch.create_time > tools.get_day_zero_time(datetime.datetime.now().date()),
                                     ).order_by(
            desc(func.count(HotSearch.id)))
        print(hot_search)
        keywords = hot_search.slice(start, end).all()
        total = hot_search.count()
        print(keywords)
        for i in keywords:
            data_dict = {}
            data_dict['keywords'] = i[0]
            data_dict['frequency'] = i[1]
            data_dict['userNums'] = i[2]
            keyword_data.append(data_dict)

        return response_code.LayuiSuccess(message='查询成功！', data=keyword_data, count=total)


# 今日热文 今天收录的阅读量比较高得文章，目前看没啥用得
class InterfaceTopArticle(views.MethodView):
    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = ArticleListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)
        print(tools.get_day_zero_time(datetime.datetime.now().date()))
        start = (page - 1) * limit
        end = start + limit
        article_data = []
        article_obj = WechatArticle.query
        article_search = article_obj.filter(WechatArticle.publish_time > tools.get_day_zero_time(datetime.datetime.now().date()),
                                     ).order_by(WechatArticle.publish_time.desc())


        articles = article_search.slice(start, end).all()
        total = article_search.count()

        for i in articles:
            data_dict = {}
            data_dict['id'] = i.id
            data_dict['author'] = i.author
            data_dict['title'] = i.title
            data_dict['account_name'] = i.account
            data_dict['url'] = i.url
            data_dict['digest'] = i.digest
            data_dict['publish_time'] = str(i.publish_time)
            article_data.append(data_dict)

        return response_code.LayuiSuccess(message='查询成功！', data=article_data, count=total)

# 今日访客流量分布： pv uv
class InterfaceLogVisitorEcharts(views.MethodView):
    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        today = datetime.date.today()
        uv_num = [User_Logs.query.with_entities(User_Logs.visitor_id).filter(
            and_(extract('year', User_Logs.create_time) == str(today).split('-')[0],
                 extract('month', User_Logs.create_time) == str(today).split('-')[1],
                 extract('day', User_Logs.create_time) == str(today).split('-')[2],
                 extract('hour', User_Logs.create_time) == str(i),
                 )).distinct().count() for i in range(25)]
        pv_num = [User_Logs.query.filter(
            and_(extract('year', User_Logs.create_time) == str(today).split('-')[0],
                 extract('month', User_Logs.create_time) == str(today).split('-')[1],
                 extract('day', User_Logs.create_time) == str(today).split('-')[2],
                 extract('hour', User_Logs.create_time) == str(i),
                 )).count() for i in range(25)]
        x_date_list = ['{}:00'.format(i) for i in range(25)]

        data = {"x_data": x_date_list, "pv_num": pv_num,"uv_num":uv_num}
        return response_code.LayuiSuccess(message='查询成功！', data=data, count=0)

class InterfaceArticleFlag(views.MethodView):
    '''
    # 如果flag=1 精华文章。else 普通文章
    '''

    @api_version
    @login_required  # 自动完成认证
    def post(self, version):
        form = ArticleFlagForm().validate_for_api()  # 验证表单
        id = form.id.data
        flag = form.flag.data

        wechat_article = WechatArticle.query.get(id)
        if wechat_article:
            if wechat_article.flag != flag:
                wechat_article.flag = flag
                db.session.commit()
                return response_code.LayuiSuccess(message='文章：“{}”修改成功！'.format(wechat_article.title))

            return response_code.ParameterException(message='已经被被人修改，刷新看看！！')
        return response_code.ParameterException(message='修改失败！')
