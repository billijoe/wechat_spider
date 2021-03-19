# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from flask import request
from wtforms import Form

from .response_code import ParameterException


class BaseForm(Form):
    # 接收Jason参数
    def __init__(self):
        formdata = request.form
        data = request.get_json(silent=True)
        args = request.args
        if not formdata:
            super(BaseForm, self).__init__(formdata=args, data=data, )
        else:
            super(BaseForm, self).__init__(formdata=formdata, data=data, )

    def get_error(self):
        message = None
        print(self.errors)
        if self.errors == {}:
            pass
        else:
            message = self.errors.popitem()[1][0]
        return message

    # 对验证错误的参数抛出异常
    def validate_for_api(self):
        valid = super(BaseForm, self).validate()
        if not valid:
            # form errors
            raise ParameterException(message=self.get_error())
        return self
