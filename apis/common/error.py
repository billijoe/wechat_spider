# -*- coding: UTF-8 -*-

__author__ = 'Joynice'

from flask import json
from werkzeug.exceptions import HTTPException


class APIException(HTTPException):
    '''
    返回Api相应信息，默认信息如下：
    code = 500
    msg = 'sorry, we made a mistake (*￣︶￣)!'
    data = False
    success=False
    '''
    code = 500
    message = 'sorry, we made a mistake (*￣︶￣)!'
    data = False
    success = False

    def __init__(self, message=None, code=None, data=False, success=False):
        if code:
            self.code = code
        if message:
            self.message = message
        if data:
            self.data = data
        if success:
            self.success = success
        super(APIException, self).__init__(message, None)

    def get_body(self, environ=None):
        '''
        重写get_body返回json信息
        :param environ:
        :return:
        '''
        body = dict(  # 返回主体信息
            code=self.code,
            message=self.message,
            data=self.data,
            success=self.success
        )
        text = json.dumps(body)
        print('响应数据', text)
        return text

    def get_headers(self, environ=None):
        '''
        重写header头
        :param environ:
        :return:
        '''
        return [('Content-Type', 'application/json')]
