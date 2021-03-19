# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/9 15:42
@Auth ： AJay13
@File ：verify_article.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
from apis.common.form import BaseForm as Form
from wtforms import StringField, IntegerField, DateTimeField,DateField
from wtforms.validators import DataRequired, length, Email, Length, Regexp, InputRequired, ValidationError, Length, \
    NumberRange, AnyOf


class AccountTaskListForm(Form):

    account_name = StringField(validators=[length(min=0, max=100, message='超出范围')])
    account_id = StringField(validators=[length(min=0, max=20, message='超出范围')])
    tip = StringField(validators=[length(min=0, max=20, message='超出范围')])
    status = StringField(validators=[AnyOf(['1','0',''])],default='')

    page = StringField(validators=[], default=1)
    limit = StringField(validators=[], default=10)

    def validate_page(self, field):
        try:
            page = int(field.data)
            if not 0 < page:
                raise ValidationError('超出范围')
        except:
            raise ValidationError(message='必须是数字')

    def validate_limit(self, field):
        try:
            limit = int(field.data)
            if not 0 < limit < 100:
                raise ValidationError('超出范围')
        except:
            raise ValidationError(message='必须是数字')

class ArticleFlagForm(Form):
    id = StringField(validators=[],default='')
    flag = StringField(validators=[AnyOf(['1','0'])],default='')
