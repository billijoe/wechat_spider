# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/9 14:21
@Auth ： AJay13
@File ：interface_article_list.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

# 用户管理接口：用户日志、热门搜索、黑名单、留言板

## 用户日志：日志展示
## 热门搜索：搜索展示
## 黑名单：黑名单展示、添加黑名单、删除黑名单

__all__ = ['InterfaceHotSearchList', 'InterfaceArticleFlag']
from flask import views
from sqlalchemy import and_

from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.user.verify_hot_search import HostSearchListForm, ArticleFlagForm
from apps.admin.models import WechatArticle
from exts import db
from models import HotSearch


## 用户管理：热门搜索
class InterfaceHotSearchList(views.MethodView):
    '''
    搜索展示
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = HostSearchListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)

        ID = form.ID.data
        date_end = form.date_end.data
        date_start = form.date_start.data
        flag = form.flag.data

        start = (page - 1) * limit
        end = start + limit
        logs_data = []
        # 条件查询

        keyword_data = []

        hot_search_obj = HotSearch.query

        if date_end:
            hot_search_obj = hot_search_obj.filter(HotSearch.create_time < date_end)
        if date_start:
            hot_search_obj = hot_search_obj.filter(HotSearch.create_time > date_start)
        if flag:
            print(flag)
        hot_search = hot_search_obj.filter(
            and_(
                HotSearch.visitor_id.like("%" + ID + "%"),
            )).order_by(HotSearch.create_time.desc())

        keywords = hot_search.slice(start, end)
        total = hot_search.count()

        for i in keywords:
            data_dict = {}
            data_dict['id'] = i.id
            data_dict['visitor_id'] = i.visitor_id
            data_dict['search'] = i.search
            data_dict['create_time'] = str(i.create_time)
            data_dict['page'] = str(i.page)
            data_dict['count'] = str(i.count)
            keyword_data.append(data_dict)

        return response_code.LayuiSuccess(message='查询成功！', data=keyword_data, count=total)


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
