# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from flask import jsonify

from apis.common.error import APIException


class HttpCode(object):
    layuiok = 0
    getok = 200
    postok = 201
    delok = 202
    paramserror = 400
    unautherror = 401
    forbiderror = 403
    notfoundserror = 404
    methoderror = 405
    servererror = 500


def restful_result(code, message, data, count):
    return jsonify({"code": code, "message": message, "count": count, "data": data or {}})


class GetSuccess(APIException):
    code = HttpCode.getok
    message = 'ok'
    data = {}
    success = True


def LayuiSuccess(message="", data=None, count=None):
    return restful_result(code=0, message=message, data=data, count=count)


class PostSuccess(APIException):
    code = HttpCode.postok
    message = 'ok'
    data = {}
    success = True


class DeleteSuccess(APIException):
    code = HttpCode.delok
    message = 'delete success'
    data = {}
    success = True


class ServerError(APIException):
    code = HttpCode.servererror
    message = 'sorry, we made a mistake (*￣︶￣)!'


class ApiVersionException(APIException):
    code = HttpCode.paramserror
    message = 'api version is invalid'


class ParameterException(APIException):
    code = HttpCode.paramserror
    message = 'invalid parameter'


class NotFound(APIException):
    code = HttpCode.notfoundserror
    message = 'the resource are not found O__O...'


class AuthFailed(APIException):
    code = HttpCode.unautherror
    message = 'authorization failed'


class Forbidden(APIException):
    code = HttpCode.forbiderror
    message = 'forbidden, not in scope'
