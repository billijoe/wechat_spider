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

__all__ = ['InterfaceEmailUserList', 'InterfaceArticleFlag']
from flask import views
from sqlalchemy import and_

from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.user.verify_email_user import EmailUserListForm, ArticleFlagForm
from apps.admin.models import WechatArticle
from exts import db
from models import EmailUser


## 用户管理：展示接收告警信息的邮箱
class InterfaceEmailUserList(views.MethodView):
    '''
    展示邮箱
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = EmailUserListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)

        email = form.email.data

        start = (page - 1) * limit
        end = start + limit
        email_data = []
        # 条件查询

        emails_obj = EmailUser.query
        emails_search = emails_obj.filter(and_(EmailUser.email.like("%" + email + "%"), )).order_by(
            EmailUser.create_time.desc())
        emails = emails_search.slice(start, end)
        total = emails_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in emails:
            email = {}
            email['id'] = i.id
            email['email'] = i.email
            email['create_time'] = str(i.create_time)
            email_data.append(email)
        return response_code.LayuiSuccess(message='查询成功！', data=email_data, count=total)


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
