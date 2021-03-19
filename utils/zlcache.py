# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

import redis
from flask import current_app

from exts import db

with db.app.app_context():
    cache = redis.Redis(host=current_app.config['REDIS_HOST'], port=current_app.config['REDIS_PORT'],
                        db=current_app.config['REDIS_DB_MEM'], password=current_app.config['REDIS_PWD'])


    def set(key, value, timeout=current_app.config['MEMCACHE_TIMEOUT']):
        return cache.set(key, value, timeout)


    def get(key):
        return cache.get(key)


    def ipset(key, value, timeout=current_app.config['BLOCK_IP_TIMEOUT']):
        return cache.set(key, value, timeout)


    def ipget(key):
        return cache.get(key)


    def mget(keys):
        return cache.mget(keys)


    def delete(key):
        return cache.delete(key)


    def zset(value):
        return cache.zadd('logs:logs', value, 0)


    def hset(key, value):
        return cache.hset('logs:logs', key, value)


    def hlen():
        return cache.hlen('logs:logs')


    def havls():
        return cache.hvals('logs:logs')


    def hdel_all():
        return cache.delete('logs:logs')
