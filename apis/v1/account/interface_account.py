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

__all__ = ['InterfaceAccountList','InterfaceArticleFlag']
from flask import views
from sqlalchemy import and_
import config
from exts import db
from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.account.verify_account import AccountListForm,ArticleFlagForm
from apps.admin.models import WechatArticle, WechatArticleList,WechatAccount

## 公众号采集：展示公众号
class InterfaceAccountList(views.MethodView):
    '''
    公众号管理的展示公众号接口
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = AccountListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)

        account_name =form.account_name.data

        start = (page - 1) * limit
        end = start + limit

        # 条件查询


        account_data = []

        account_obj = WechatAccount.query
        if account_name:
            account_search = account_obj.filter(
                and_(WechatAccount.account.like("%" + account_name + "%"),
                     )).order_by(
                WechatAccount.spider_time.desc())
        else:
            account_search = account_obj.order_by(WechatAccount.spider_time.desc())
        accounts = account_search.slice(start, end)
        total = account_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in accounts:
            account = {}
            account['id'] = i.id
            account['account_name'] = i.account
            account['account_id'] = getattr(i,'__biz')
            account['head_url'] = i.head_url
            account['summary'] = i.summary
            account['qr_code'] = i.qr_code
            account['verify'] = i.verify
            account['spider_time'] = str(i.spider_time)

            account_data.append(account)

        return response_code.LayuiSuccess(message='查询成功！', data=account_data, count=total)





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

