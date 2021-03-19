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

__all__ = ['InterfaceMsgBoardList', 'InterfaceArticleFlag']
from flask import views
from sqlalchemy import and_

from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.user.verify_msg_board import MsgBoardListForm, ArticleFlagForm
from apps.admin.models import WechatArticle
from exts import db
from models import MsgBoard


## 用户管理：展示留言板
class InterfaceMsgBoardList(views.MethodView):
    '''
    展示留言板
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = MsgBoardListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)
        start = (page - 1) * limit
        end = start + limit

        visitor_id = form.visitor_id.data
        ip = form.ip.data
        area = form.area.data
        content = form.content.data

        # 条件查询
        amsg_board_data = []
        msg_board_obj = MsgBoard.query
        msg_board_search = msg_board_obj.filter(
            and_(MsgBoard.visitor_id.like("%" + visitor_id + "%"),
                 MsgBoard.ip.like("%" + ip + "%"),
                 MsgBoard.area.like("%" + area + "%"),
                 MsgBoard.content.like("%" + content + "%"))).order_by(
            MsgBoard.create_time.desc())
        msgs = msg_board_search.slice(start, end)
        total = msg_board_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in msgs:
            task = {}
            task['id'] = i.id
            task['visitor_id'] = i.visitor_id
            task['ip'] = i.ip
            task['content'] = i.content
            task['area'] = i.area
            task['create_time'] = str(i.create_time)
            amsg_board_data.append(task)
        return response_code.LayuiSuccess(message='查询成功！', data=amsg_board_data, count=total)


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
