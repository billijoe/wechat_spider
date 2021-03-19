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

__all__ = ['InterfaceArticleList','InterfaceArticleFlag']
from flask import views
from sqlalchemy import and_
import config
from exts import db
from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.article.verify_article import ArticleListForm,ArticleFlagForm
from apps.admin.models import WechatArticle, WechatArticleList


class InterfaceArticleList(views.MethodView):
    '''
    文章管理的文章接口
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        form = ArticleListForm().validate_for_api()  # 验证表单
        page = int(form.page.data)
        limit = int(form.limit.data)
        date_end =form.date_end.data
        date_start =form.date_start.data
        flag =form.flag.data
        account_name =form.account_name.data
        title =form.title.data

        start = (page - 1) * limit
        end = start + limit

        article_data = []
        article_obj = WechatArticle.query
        # 条件查询
        if date_end:
            article_obj = article_obj.filter(WechatArticle.publish_time <= date_end)
        if date_start:
            article_obj = article_obj.filter(WechatArticle.publish_time >= date_start)
        if flag:
            article_obj = article_obj.filter(WechatArticle.flag == int(flag))
        if account_name or title:
            article_obj = article_obj.filter(
                and_(WechatArticle.account.like("%" + account_name + "%"),
                     WechatArticle.title.like("%" + title + "%"),
                     ))

        article_search = article_obj.order_by(WechatArticle.publish_time.desc())
        articles = article_search.slice(start, end)
        total = article_search.count()
        # 查询所有正在处于监听队列的数据做成字典
        for i in articles:
            # 查询是否原创：时间上可能会比较慢，看下线上情况
            wal = WechatArticleList.query.filter(WechatArticleList.sn == i.sn).first()
            if wal:
                if wal.copyright_stat == 11:
                    copyright_stat = '原创'
                elif wal.copyright_stat == 100 :
                    copyright_stat = '未声明'
                elif wal.copyright_stat == 201 or wal.copyright_stat == 101:
                    copyright_stat = '转载'
                else:
                    copyright_stat = wal.copyright_stat
                del_flag = wal.copyright_stat
            else:
                copyright_stat = '未知'
                del_flag = '未知'

            article = {}
            article['id'] = i.id
            article['account'] = i.account
            article['title'] = i.title
            article['url'] = i.url
            article['author'] = i.author
            article['digest'] = i.digest
            article['cover'] =config.base_config.IMG_CDN+ i.cover
            # article['content_html'] = filter_html(i.content_html)  # 做处理
            article['copyright_stat'] = copyright_stat
            article['del_flag'] = del_flag
            article['source_url'] = i.source_url
            article['comment_id'] = i.comment_id
            article['publish_time'] = str(i.publish_time)
            article['spider_time'] = str(i.spider_time)
            article['flag'] = i.flag
            article_data.append(article)

        return response_code.LayuiSuccess(message='查询成功！', data=article_data, count=total)

    # @api_version
    # def post(self, version):
    #     form = LoginForm().validate_for_api()  # 验证表单
    #     identity = models.Admin.verify(form.username.data, form.password.data)  # 验证数据库数据
    #     expiration = current_app.config['TOKEN_EXPIRATION']  # token存活周期
    #     access_token = generate_auth_token(identity['uid'],
    #                                        expiration).decode('ascii')  # 生成token
    #     return response_code.LayuiSuccess(data={'access_token': access_token}, message='Login success')


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

