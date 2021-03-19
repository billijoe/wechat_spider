# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/9 14:21
@Auth ： AJay13
@File ：interface_article_list.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

# 分类管理接口： 分类列表、删除分类、修改分离、添加分类

__all__ = ['InterFaceWechtTagList','InterfaceArticleFlag']
from flask import views
from sqlalchemy import and_
import config
from exts import db
from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.tags.verify_tag import TagListForm,ArticleFlagForm
from apps.admin.models import WechatArticle, WechatArticleList
from models import WechatTag


class InterFaceWechtTagList(views.MethodView):
    '''
    公众号分类的接口
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = TagListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)
        start = (page - 1) * limit
        end = start + limit
        tag_data = []

        tag_obj = WechatTag.query
        tags = tag_obj.slice(start, end)
        total = tag_obj.count()

        for i in tags:
            tag = {}
            tag['id'] = i.id
            tag['tag_name'] = i.tag_name
            tag['tag_en'] = i.tag_en
            tag['tag_summary'] = i.tag_summary
            tag['create_time'] = i.create_time
            tag_data.append(tag)

        return response_code.LayuiSuccess(message='查询成功！', data=tag_data, count=total)




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

