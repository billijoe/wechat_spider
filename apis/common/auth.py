# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

"""
 Created by 七月 on 2018/5/7.
 微信公众号：林间有风
"""
from collections import namedtuple
from functools import wraps

from flask import current_app
from flask import g, request
from flask_httpauth import HTTPBasicAuth
from itsdangerous import TimedJSONWebSignatureSerializer \
    as Serializer, BadSignature, SignatureExpired

from apis.common.response_code import AuthFailed

auth = HTTPBasicAuth()

User = namedtuple('User', ['uid', 'scope'])


@auth.verify_password
def verify_password(token, passowrd):
    # token
    # HTTP 账号密码
    # header key:value
    # account  qiyue
    # 123456
    # key=Authorization
    # value =basic base64(qiyue:123456)
    print('token值', token)
    user_info = verify_auth_token(token)
    if not user_info:
        return False
    else:
        # request
        g.user = user_info
        return True


def generate_auth_token(uid, scope=None, expiration=7200):
    """生成令牌"""
    s = Serializer(current_app.config['SECRET_KEY'],
                   expires_in=expiration)
    return s.dumps({
        'uid': uid,
        'scope': scope
    })


def verify_auth_token(token):
    """验证token，传入token使用Serializer检测token是否有效或者过期"""
    s = Serializer(current_app.config['SECRET_KEY'])  # 传入secrte_key产生一个序列化对象
    try:
        data = s.loads(token)  # 进行token反序列化，获取其中信息
    except BadSignature:  # 如果返回BadSignature，token无效
        raise AuthFailed(message='token is invalid')
    except SignatureExpired:  # 如果返回SignatureExpired，token失效
        raise AuthFailed(message='token is expired')
    print(data)
    uid = data['uid']  # 获取user id
    scope = data['scope']  # 获取用户权限作用域
    print(uid, scope)
    # request 视图函数
    # allow = is_in_scope(scope, request.endpoint)   #鉴权 传入用户作用域，以及当前访问的路由定于的函数名
    # if not allow:
    #     raise Forbidden()
    return User(uid, scope)


def login_required(func):
    '''登录判断，获取请求头的token值，进行token检测'''
    @wraps(func)
    def inner(*args, **kwargs):
        headers_token = request.headers.get('access_token')
        if headers_token:
            user_info = verify_auth_token(headers_token)
            if not user_info:
                return AuthFailed(message='token is invalid')
            else:
                g.user = user_info
                return func(*args, **kwargs)
        else:
            return AuthFailed(message='token is missing')

    return inner
