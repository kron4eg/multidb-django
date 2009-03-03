# -*- coding: utf-8 -*-
from threading import local

_threading_local = local()

import django
import transaction

django.db.transaction = transaction
django.db.models.base.transaction = transaction
django.db.models.fields.related.transaction = transaction
django.db.models.query.transaction = transaction
