# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

# 钩子函数
from .views import bp
from flask import session, g, render_template
from models import Admin,TCommunityWechatAccount
from flask import current_app


@bp.before_request
def before_request():
    if current_app.config['CMS_USER_ID'] in session:
        user_id = session.get(current_app.config['CMS_USER_ID'])
        user = Admin.query.get(user_id)
        t_community_account_count = TCommunityWechatAccount.query.filter(
            TCommunityWechatAccount.status == '0').count()  # 社区提交公众号未审核数量
        if user:
            g.user = user
            g.t_community_account_count = t_community_account_count
    else:
        g.user = {"username": '旅行者'}


@bp.errorhandler(404)
def page_not_found(error):
    if current_app.config['CMS_USER_ID'] in session:
        user_id = session.get(current_app.config['CMS_USER_ID'])
        user = Admin.query.get(user_id)
        if user:
            g.user = user
    return render_template('admin/admin_404.html'), 404
