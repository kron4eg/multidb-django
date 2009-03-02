# -*- coding: utf-8 -*-
from threading import local

from django.conf import settings
from django.core import signals
from django.db.models import sql
from django.db.models.query import QuerySet, insert_query

from multidb import _threading_local


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


signals.request_started.connect(open_connection_pool)
signals.request_finished.connect(close_connection_pool)


def get_db_wrapper():
    if not hasattr(_threading_local, 'DB_POOL'):
        open_connection_pool()
    db_name = getattr(_threading_local, 'DATABASE', 'default')
    return _threading_local.DB_POOL[db_name]


def __init__(self, model=None, query=None):
     self.model = model
     self.query = query or sql.Query(self.model, get_db_wrapper())
     self._result_cache = None
     self._iter = None
     self._sticky_filter = False
QuerySet.__init__ = __init__


def multidb_insert_query(model, values, return_id=False, raw_values=False):
    query = sql.InsertQuery(model, get_db_wrapper())
    query.insert_values(values, raw_values)
    return query.execute_sql(return_id)

insert_query = multidb_insert_query
