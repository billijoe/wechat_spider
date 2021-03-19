# -*- coding: UTF-8 -*-
__author__ = 'Joynice'
from enum import Enum, unique
from functools import wraps
from apis.common.response_code import *

@unique
class apiVersion(Enum):
    """
    api 版本枚举
    """
    version1 = 'v1'
    version2 = 'v2'

def verify_version(version):
    """
    API版本验证
    :param version: 版本信息
    :return:
    """
    if version == apiVersion.version1.value: #现在判断v1版本
        return True
    else:
        return False

def api_version(func):
    """
    API版本验证装饰器
    :param func:
    :return:
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 验证api版本
        verify_result = verify_version(kwargs.get('version'))
        if not verify_result:
            raise ApiVersionException() #抛出异常，返回结果状态码400, message:api version is invalid
        return func(*args, **kwargs)
    return wrapper