# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

class Scope:
    allow_api = []

    def __add__(self, other):
        self.allow_api = self.allow_api + other.allow_api
        self.allow_api = list(set(self.allow_api))
        # 运算符重载
        return self

class UserScope(Scope):
    allow_api = ['user.login', 'user.register']


class AdminScope(Scope):
    allow_api = ['challenges.challenges']

    def __init__(self):
        self + UserScope()
        print(self.allow_api)


class AdministratorsScope(Scope):
    allow_api = []

    def __init__(self):
        self + AdminScope()



def is_in_scope(scope, endpoint):
    # scope()
    # 反射
    # globals
    # v1.view_func   v1.module_name+view_func
    # v1.red_name+view_func
    print(scope)
    scope = globals()[scope]()
    print(scope.allow_api)
    print(endpoint)
    if endpoint in scope.allow_api:
        return True
    else:
        return False
