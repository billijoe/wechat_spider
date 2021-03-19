# -*- coding: utf-8 -*-
"""
@project ： WechatTogether
@Time ： 2020/6/10 18:32
@Auth ： AJay13
@File ：test.py
@IDE ：PyCharm
@Motto：ABC(Always Be Coding)

"""
import os
from config import base_config
from qqwry import QQwry, updateQQwry


class IP2Region():
    '''
    解析ip地址：lookup(ip)方法将ip转化成（"省份","地区"）
    '''

    def __init__(self):
        self.filename = 'qqwry.dat'
        self.dat_path = os.path.join(base_config.BASE_PATH, 'utils', self.filename)
        self.q = QQwry()
        if os.path.exists(self.dat_path):
            self.q.load_file(self.dat_path)
            print(self.q)
        else:

            print('初始化更新ip库')
            self.update_dat()
            self.reload_dat()
            return

    def get_lastone(self):
        '''
        ﻿返回最后一条数据，最后一条通常为数据的版本号
        ﻿没有数据则返回一个None
        :return:
        '''
        version = self.q.get_lastone()
        return version

    def update_dat(self):
        '''
        异步更新，使用线程或者celery更新IP数据库源
        :return:(bool) 成功后返回一个正整数，是文件的字节数；失败则返回一个负整数。
        '''
        result = updateQQwry(self.dat_path)
        if result > 0:
            print('ip库更新成功')
            return True
        print('ip库更新失败，网络出现故障')
        return False

    def lookup(self, ip):
        '''
        解析ip地址
        :param ip(str): 要解析的ip地址
        :return: 找到则返回一个含有两个字符串的元组，如：('国家', '省份')﻿没有找到结果，则返回一个None
        '''
        return self.q.lookup(ip)

    def reload_dat(self):
        '''
        重载IP数据源，当IPdat数据更新的时候，使用此方法更新数据
        :return: (bool) 重载成功返回True，重载失败返回Flase
        '''
        self.q.clear()
        if not self.q.is_loaded():
            self.q.load_file(self.dat_path)
            return True
        return False


ip = IP2Region()

print(ip.get_lastone())
print(ip.lookup('127.0.0.1')[0])
print(ip.lookup('182.129.239.23')[0])
print(ip.lookup('101.231.39.65')[0])

