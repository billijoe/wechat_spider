#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__author__ = 'AJay'
__mtime__ = '2019/8/17 0017'

"""

from flask import Flask

import config
from apps.common import bp as common_bp
from exts import db, mail


# 创建一个初始化部分数据库的app
def create_app():
    app = Flask(__name__)
    #app.config.from_object(config.config['development'])
    # app.config.from_object(config.config['testing'])
    app.config.from_object(config.config['production'])
    app.register_blueprint(common_bp)
    db.app = app
    db.init_app(app)
    mail.init_app(app)
    return app


app = create_app()

if __name__ == '__main__':
    app.run()
