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

__all__ = ['InterfaceCommunityAccountList','InterfaceArticleFlag']
from flask import views
from sqlalchemy import and_
import config
from exts import db
from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.account.verify_community_account import CommunityAccountListForm,ArticleFlagForm
from apps.admin.models import WechatArticle, WechatArticleList,WechatAccount
from models import TCommunityWechatAccount

## 公众号采集：展示公众号
class InterfaceCommunityAccountList(views.MethodView):
    '''
    社区公众号管理的展示公众号接口
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = CommunityAccountListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)

        account =form.account.data
        contributor =form.contributor.data
        tip =form.tip.data
        status =form.status.data

        start = (page - 1) * limit
        end = start + limit

        # 条件查询

        account_data = []

        community_account_obj = TCommunityWechatAccount.query

        account_search = community_account_obj.filter(
            and_(TCommunityWechatAccount.account_name.like("%" +account + "%"),
                 TCommunityWechatAccount.founder.like("%" + contributor+ "%"),
                 TCommunityWechatAccount.tag.like("%" +tip + "%"),
                 TCommunityWechatAccount.status.like("%" + status + "%"))).order_by(
            TCommunityWechatAccount.create_time.desc())

        community_accounts = account_search.slice(start, end)
        total = account_search.count()
        if total != 0:
            # 查询所有的数据做成字典
            for i in community_accounts:
                accounts = {}
                accounts['id'] = i.id
                accounts['account_name'] = i.account_name
                accounts['account_id'] = i.account_id
                accounts['account_link'] = i.account_link
                accounts['tag_name'] = i.Ctags.tag_name
                accounts['founder'] = i.founder
                accounts['create_time'] = str(i.create_time)
                accounts['status'] = i.status
                account_data.append(accounts)

            return  response_code.LayuiSuccess(message='查询成功！', data=account_data, count=total)
        return response_code.LayuiSuccess(message='未查到相关信息', count=0)







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

