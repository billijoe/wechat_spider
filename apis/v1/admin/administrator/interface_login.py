# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/7 15:18
@Auth ： AJay13
@File ：interface_login.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
__all__ = ['InterfaceLogin']
from flask import views, current_app

import models
from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import generate_auth_token
from apis.v1.admin.administrator.verify_administrator import LoginForm


class InterfaceLogin(views.MethodView):
    '''
    管理员 登录
    '''

    @api_version
    def get(self, version):
        return '服务开启'

    @api_version
    def post(self, version):
        form = LoginForm().validate_for_api()  # 验证表单
        identity = models.Admin.verify(form.username.data, form.password.data)  # 验证数据库数据
        expiration = current_app.config['TOKEN_EXPIRATION']  # token存活周期
        access_token = generate_auth_token(identity['uid'],
                                           expiration).decode('ascii')  # 生成token
        return response_code.LayuiSuccess(data={'access_token': access_token}, message='Login success')
