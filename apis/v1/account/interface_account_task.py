# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/9 14:21
@Auth ： AJay13
@File ：interface_article_list.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

# 文章管理的接口：文章列表、删除文章、修改文章、文章加如周报、文章前台隐藏、批量删除文章
# 公众号管理接口：社区提交公众号、公众号任务、公众号采集

## 社区提交公众号展示：社区公众号展示、社区添加公众号、删除社区公众号、修改社区公众号、收录社区公众号
## 公众号任务：公众号展示、添加公众号、删除公众号、同步公众号、复活僵尸号、监控公众号、修改公众号
## 公众号采集：展示公众号、删除公众号

__all__ = ['InterfaceAccountTaskList','InterfaceArticleFlag']
from flask import views
from sqlalchemy import and_
import config
from exts import db
from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.account.verify_account_task import AccountTaskListForm,ArticleFlagForm
from apps.admin.models import WechatArticle, WechatArticleList,WechatAccount,WechatAccountTask
from  models import TWechatAccount

## 公众号采集：展示公众号任务
class InterfaceAccountTaskList(views.MethodView):
    '''
    公众号任务管理的展示公众号接口
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = AccountTaskListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)

        account_name =form.account_name.data
        account_id =form.account_id.data
        tip =form.tip.data
        status =form.status.data

        start = (page - 1) * limit
        end = start + limit

        # 条件查询

        account_task_data = []
        account_task_obj = TWechatAccount.query
        account_task_search = account_task_obj.filter(
            and_(TWechatAccount.account_name.like("%" + account_name + "%"),
                 TWechatAccount.account_id.like("%" + account_id + "%"),
                 TWechatAccount.tag.like("%" + tip+ "%"),
                 TWechatAccount.status.like("%" + status + "%"))).order_by(
            TWechatAccount.create_time.desc())

        account_tasks = account_task_search.slice(start, end)
        total = account_task_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in account_tasks:
            wat = WechatAccountTask.query.filter_by(__biz=i.account_id).first()
            last_publish_time = ''
            last_spider_time = ''
            is_zombie = '未知'
            if wat:
                last_publish_time = str(wat.last_publish_time)
                last_spider_time = str(wat.last_spider_time)
                is_zombie = wat.is_zombie
            task = {}
            task['id'] = i.id
            task['account_name'] = i.account_name
            task['account_id'] = i.account_id
            task['tag_name'] = i.tags.tag_name
            task['founder'] = 'admin'
            task['create_time'] = str(i.create_time)
            task['last_publish_time'] = last_publish_time
            task['last_spider_time'] = last_spider_time
            task['is_zombie'] = is_zombie
            task['status'] = i.status

            account_task_data.append(task)

        return response_code.LayuiSuccess(message='查询成功！', data=account_task_data, count=total)





class InterfaceArticleFlag(views.MethodView):
    '''
    # 如果flag=1 精华文章。else 普通文章
    '''

    @api_version
    @login_required  # 自动完成认证
    def post(self, version):
        form = ArticleFlagForm().validate_for_api()  # 验证表单
        id =form.id.data
        flag =form.flag.data

        wechat_article = WechatArticle.query.get(id)
        if wechat_article:
            if wechat_article.flag != flag:
                wechat_article.flag = flag
                db.session.commit()
                return response_code.LayuiSuccess(message='文章：“{}”修改成功！'.format(wechat_article.title))

            return response_code.ParameterException(message='已经被被人修改，刷新看看！！')
        return response_code.ParameterException(message='修改失败！')

