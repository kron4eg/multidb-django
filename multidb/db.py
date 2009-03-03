# -*- coding: utf-8 -*-
from django.conf import settings

from multidb import _threading_local

def get_object_anywhere(model, **kwargs):
    databases = (x for x in settings.DATABASES.iterkeys())
    return get_object_from(databases, model, **kwargs)

def get_object_from(databases, model, **kwargs):
    current = getattr(_threading_local, 'DATABASE', 'default')
    for db in databases:
        _threading_local.DATABASE = db
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            continue
    #restore original database in case if failure
    _threading_local.DATABASE = current
    return None

def switch_db(dbname):
    _threading_local.DATABASE = dbname
