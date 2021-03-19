# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/8 17:45
@Auth ： AJay13
@File ：interface_info.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

__all__ = ['InterfaceAdminInfo']
from flask import views, current_app, g


from models import Admin
from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.common.auth import generate_auth_token
from apis.v1.admin.administrator.verify_administrator import LoginForm


class InterfaceAdminInfo(views.MethodView):
    '''
    管理员 信息
    '''

    @api_version
    @login_required  # 自动完成认证
    def get(self, version):
        print(g.user)
        user_id =g.user.uid
        user = Admin.query.get(user_id)
        data = {
            'username': user.username,
            'sex': '男',
            'role': '1'
        }
        return response_code.LayuiSuccess(data=data)

    @api_version
    def post(self, version):
        form = LoginForm().validate_for_api()  # 验证表单
        identity = models.Admin.verify(form.username.data, form.password.data)  # 验证数据库数据
        expiration = current_app.config['TOKEN_EXPIRATION']  # token存活周期
        access_token = generate_auth_token(identity['uid'],
                                           expiration).decode('ascii')  # 生成token
        return response_code.LayuiSuccess(data={'access_token': access_token}, message='Login success')
