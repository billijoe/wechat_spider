# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/9 15:42
@Auth ： AJay13
@File ：verify_article.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
from wtforms import StringField
from wtforms.validators import length, ValidationError, DataRequired, Email

from apis.common.form import BaseForm as Form


class SettingEmailForm(Form):
    smtp_server = StringField(validators=[length(min=1, max=100, message='超出范围')])  # todo IP正则表达式
    smtp_port = StringField(validators=[length(min=1, max=6, message='超出范围')])  # todo IP正则表达式

    smtp_username = StringField(validators=[length(min=1, max=100, message='超出范围')])  # todo IP正则表达式
    smtp_password = StringField(validators=[length(min=1, max=100, message='超出范围')])  # todo IP正则表达式

    smtp_sender = StringField(validators=[
        DataRequired(message='邮箱不许为空'),
        Email(message='invalidate email')
    ])

    def validate_smtp_port(self, field):
        try:
            port = int(field.data)
            if not 0 < port < 65535:
                raise ValidationError('超出范围')
        except:
            raise ValidationError(message='必须是数字')
