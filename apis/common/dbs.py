# -*- coding: UTF-8 -*-
__author__ = 'Joynice'

from contextlib import contextmanager

from flask_sqlalchemy import SQLAlchemy as _SQLAlchemy, BaseQuery

from api.common.response_code import NotFound


class SQLAlchemy(_SQLAlchemy):
    @contextmanager
    def auto_commit(self):
        try:
            yield
            self.session.commit()
        except Exception as e:
            api_db.session.rollback()
            raise e


class Query(BaseQuery):
    def filter_by(self, **kwargs):
        if 'status' not in kwargs.keys():
            kwargs['status'] = 1
        return super(Query, self).filter_by(**kwargs)

    def get_or_404(self, ident):
        rv = self.get(ident)
        if not rv:
            raise NotFound()
        return rv

    def first_or_404(self):
        rv = self.first()
        if not rv:
            raise NotFound()
        return rv


api_db = SQLAlchemy(query_class=Query)


class Base(api_db.Model):
    __abstract__ = True

    # create_time = Column(DateTime, default=datetime.now(), comment='创建时间')
    # smart_move = Column(SmallInteger, default=1, comment='用于软删除')

    def __getitem__(self, item):
        return getattr(self, item)

    def set_attrs(self, attrs_dict):
        for key, value in attrs_dict.items():
            if hasattr(self, key) and key != 'id':
                setattr(self, key, value)

    def delete(self):
        self.status = 0

    def keys(self):
        return self.fields

    def hide(self, *keys):
        for key in keys:
            self.fields.remove(key)
        return self

    def append(self, *keys):
        for key in keys:
            print(key)
            print(self.fields)
            self.fields.append(key)
        return self
