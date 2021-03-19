# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/9 14:21
@Auth ： AJay13
@File ：interface_article_list.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""

# 设置接口：邮件配置设置、网站设置（没有用前后端分离--比较麻烦）、个人设置、修改密码

## 邮件设置：邮件配置展示，修改配置
## 个人设置：查看个人信息，修改个人信息
## 修改密码： 修改个人密码


__all__ = ['InterfaceEmailShow', 'InterfaceEmailEdit']

from flask import views

from apis.common import response_code
from apis.common.api_version import api_version
from apis.common.auth import login_required
from apis.v1.setting.verify_setting import SettingEmailForm
from exts import db
from models import System_Settings


## 邮件设置：邮件配置展示，
class InterfaceEmailShow(views.MethodView):
    '''
    邮件配置展示
    '''

    @api_version
    # @login_required  # 自动完成认证
    def get(self, version):
        data_dict = {}
        data_dict['smtp_server']=''
        data_dict['smtp_port']=''
        data_dict['smtp_sender']=''
        data_dict['smtp_username']=''
        data_dict['smtp_password']=''
        setting_email_obj = System_Settings.query.order_by(System_Settings.create_time.desc()).first()
        if setting_email_obj:
            data_dict = {}
            data_dict['smtp_server'] = setting_email_obj.smtp_server
            data_dict['smtp_port'] = setting_email_obj.smtp_port
            data_dict['smtp_sender'] = setting_email_obj.smtp_sender
            data_dict['smtp_username'] = setting_email_obj.smtp_username
            data_dict['smtp_password'] = setting_email_obj.smtp_password

            return response_code.LayuiSuccess(message='查询成功！', data=data_dict)
        else:
            return response_code.LayuiSuccess(message='查询成功！', data=data_dict)

## 邮件设置：修改配置
class InterfaceEmailEdit(views.MethodView):
    '''
    # 邮件设置：修改配置,若修改的数据为空，则增加数据
    '''

    @api_version
    @login_required  # 自动完成认证
    def post(self, version):
        form = SettingEmailForm().validate_for_api()  # 验证表单

        smtp_server = form.smtp_server.data
        smtp_port = form.smtp_port.data
        smtp_username = form.smtp_username.data
        smtp_password = form.smtp_password.data
        smtp_sender = form.smtp_sender.data

        setting_email_obj = System_Settings.query.order_by(System_Settings.create_time.desc()).first()

        if setting_email_obj:
            setting_email_obj.smtp_server = smtp_server
            setting_email_obj.smtp_port = smtp_port
            setting_email_obj.smtp_username = smtp_username
            setting_email_obj.smtp_password = smtp_password
            setting_email_obj.smtp_sender = smtp_sender

            db.session.commit()
            # 重新加载mail实例化的配置
            return response_code.LayuiSuccess(message='修改成功！')
        else:
            setting = System_Settings(smtp_server=smtp_server, smtp_port=smtp_port, smtp_username=smtp_username,
                                      smtp_password=smtp_password, smtp_sender=smtp_sender)
            db.session.add(setting)
            db.session.commit()
            return response_code.ParameterException(message='修改失败！')
