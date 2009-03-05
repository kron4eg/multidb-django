# -*- coding: utf-8 -*-
from threading import local

import django
from django.conf import settings
from django.core import signals

from multidb import _threading_local


class ProxyConnection(object):
    def __getattribute__(self, arg):
        return getattr(get_db_wrapper(), arg)

    def __setattr__(self, name, value):
        setattr(get_db_wrapper(), name, value)

    def __repr__(self):
        db_name = getattr(_threading_local, 'DATABASE', 'default')
        return u'%s: %s' % (db_name, get_db_wrapper().__repr__())

fake_connection = ProxyConnection()
django.db.connection = fake_connection
django.db.models.base.connection = fake_connection
django.db.models.connection = fake_connection
django.db.models.fields.connection = fake_connection
django.db.models.fields.related.connection = fake_connection
django.db.models.sql.expressions.connection = fake_connection
django.db.models.sql.query.connection = fake_connection
django.db.models.sql.where.connection = fake_connection
django.db.models.query.connection = fake_connection
django.db.transaction.connection = fake_connection

def open_connection_pool(**kwargs):
    if not hasattr(_threading_local, 'DB_POOL'):
        _threading_local.DB_POOL = {}
    for db_name in settings.DATABASES:
        database = settings.DATABASES[db_name]
        backend = __import__('django.db.backends.' + database['DATABASE_ENGINE'] + ".base", {}, {}, ['base'])
        thread_settings = local()
        for key, value in database.iteritems():
            setattr(thread_settings, key, value)
        wrapper = backend.DatabaseWrapper()
        wrapper._cursor(thread_settings)
        _threading_local.DB_POOL[db_name] = wrapper

def close_connection_pool(**kwargs):
    if hasattr(_threading_local, 'DB_POOL'):
        for db_name in _threading_local.DB_POOL:
            _threading_local.DB_POOL[db_name]._commit()
            _threading_local.DB_POOL[db_name].close()
        del _threading_local.DB_POOL
signals.request_finished.connect(close_connection_pool)

def get_db_wrapper():
    if not hasattr(_threading_local, 'DB_POOL'):
        open_connection_pool()
    db_name = getattr(_threading_local, 'DATABASE', 'default')
    _threading_local.DATABASE = db_name
    return _threading_local.DB_POOL[db_name]
