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

__all__ = ['InterfaceBlockIPList', 'InterfaceArticleFlag']
import time

from flask import views
from sqlalchemy import and_

from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.user.verify_block_ip import BolckIPForm, ArticleFlagForm
from apps.admin.models import WechatArticle
from exts import db
from models import BlockIP


## 用户管理：展示用户日志
class InterfaceBlockIPList(views.MethodView):
    '''
    展示黑名单列表
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = BolckIPForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)

        ip = form.ip.data

        start = (page - 1) * limit
        end = start + limit

        # 条件查询
        ips_data = []

        block_ip_obj = BlockIP.query
        block_ip_search = block_ip_obj.filter(and_(BlockIP.ip.like("%" + ip + "%"), )).order_by(
            BlockIP.create_time.desc())

        # 查询的时间为大于  现在的时间-黑名单周期时间(只显示现在还在黑名单的数据)
        # live_time = (datetime.datetime.now()+datetime.timedelta(seconds=-config.base_config.BLOCK_IP_TIMEOUT)).strftime("%Y-%m-%d %H:%M:%S")
        # block_ips = block_ip_search.filter(BlockIP.create_time>live_time).slice(start, end)
        block_ips = block_ip_search.slice(start, end)
        total = block_ip_search.count()

        for i in block_ips:
            data_dict = {}
            data_dict['id'] = i.id
            data_dict['ip'] = i.ip
            data_dict['notes'] = i.notes
            data_dict['create_time'] = str(i.create_time)
            data_dict['end_time'] = str(i.end_time)
            data_dict['time'] = int(time.mktime(time.strptime(str(i.end_time), "%Y-%m-%d %H:%M:%S"))) * 1000
            print(data_dict['time'])
            ips_data.append(data_dict)

        return response_code.LayuiSuccess(message='查询成功！', data=ips_data, count=total)


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
