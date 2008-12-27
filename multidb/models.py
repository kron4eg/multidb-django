# -*- coding: utf-8 -*-
import thread
from threading import local

from django.conf import settings
from django.core import signals
from django.db.models import sql, Manager
from django.db.models.query import QuerySet
from django.db.transaction import savepoint_state

from lib import _threading_local


def get_db_wrapper():
    if not hasattr(_threading_local, 'DB_POOL'):
        _threading_local.DB_POOL = {}
    db = getattr(_threading_local, 'DATABASE', 'default')
    database = settings.DATABASES[db]
    if db in _threading_local.DB_POOL and \
            _threading_local.DB_POOL[db]._valid_connection():
        return _threading_local.DB_POOL[db]

    backend = __import__('django.db.backends.' + database['DATABASE_ENGINE']
        + ".base", {}, {}, ['base'])
    thread_settings = local()
    for key, value in database.iteritems():
        setattr(thread_settings, key, value)
    wrapper = backend.DatabaseWrapper()
    wrapper._cursor(thread_settings)
    del thread_settings
    _threading_local.DB_POOL[db] = wrapper
    return wrapper

def close_connection_pool(**kwargs):
    if hasattr(_threading_local, 'DB_POOL'):
        for db_name in _threading_local.DB_POOL:
            _threading_local.DB_POOL[db_name].close()
signals.request_finished.connect(close_connection_pool)


def __init__(self, model=None, query=None):
     self.model = model
     self.query = query or sql.Query(self.model, get_db_wrapper())
     self._result_cache = None
     self._iter = None
     self._sticky_filter = False
QuerySet.__init__ = __init__


def _insert(self, values, return_id=False, raw_values=False):
    query = sql.InsertQuery(self.model, get_db_wrapper())
    query.insert_values(values, raw_values)
    ret = query.execute_sql(return_id)
    query.connection._commit()
    thread_ident = thread.get_ident()
    if thread_ident in savepoint_state:
        del savepoint_state[thread_ident]
    return ret
Manager._insert = _insert
