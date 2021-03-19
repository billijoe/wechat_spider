# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from flask_apscheduler import APScheduler
from flask_mail import Mail
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect

db = SQLAlchemy()
csrf = CSRFProtect()
scheduler = APScheduler()
mail = Mail()
