# -*- coding: utf-8 -*-
from django.conf import settings

from lib import _threading_local

def get_object_anywhere(model, databases=None, **kwargs):
    if not databases:
        databases = (x for x in settings.DATABASES.iterkeys())
    for db in databases:
        _threading_local.DATABASE = db
        try:
            return model.objects.get(**kwargs)
        except model.DoesNotExist:
            continue
    return None

def switch_db(dbname):
    _threading_local.DATABASE = dbname
