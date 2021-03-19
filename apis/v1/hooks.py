# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/9/8 10:16
@Auth ： AJay13
@File ：hooks.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
from apis.common.log import lg
from apis.common.response_code import *
from werkzeug.exceptions import HTTPException
from . import api_bp




@api_bp.errorhandler(Exception)
def framework_error(e):
    if isinstance(e, APIException):
        return e, 200
    if isinstance(e, HTTPException):
        code = e.code
        msg = e.description
        success = False
        data = None
        return APIException(msg, code, data, success)
    else:
        # 调试模式
        # log
        lg.error(e)
        # if not app.config['DEBUG']:
        #     return ServerError()
        # else:
        raise e