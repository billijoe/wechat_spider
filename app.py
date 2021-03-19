# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

import socket

from flask import Flask
from flask_cors import CORS

import config
from apps.admin import bp as admin_bp
from apis import api_bp as api_bp
from apps.common import bp as common_bp
from apps.front import bp as front_bp
from exts import db, csrf, scheduler, mail
from utils import scheduler_job


def create_app():
    app = Flask(__name__)
    CORS(api_bp, resources=r'/*')  # api接口允许跨域请求
    csrf.exempt(api_bp)  # api接口去除csrf保护
    # app.config.from_object(config.config['development'])   #初始化开发环境配置1
    #app.config.from_object(config.config['testing'])  # 初始化测试环境配置
    app.config.from_object(config.config['production'])
    app.config.from_object(scheduler_job.Config())
    app.register_blueprint(api_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(common_bp)
    app.register_blueprint(front_bp)
    db.app = app
    mail.app = app

    db.init_app(app)
    mail.init_app(app)
    csrf.init_app(app)

    return app


app = create_app()
# Fix to ensure only one Gunicorn worker grabs the scheduled task
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 47200))
except socket.error:
    pass
else:
    scheduler.init_app(app)
    scheduler.start()
if __name__ == '__main__':
    # scheduler.start()
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
