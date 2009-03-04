from django.conf import settings

from multidb import _threading_local


def debug(request):
    "Returns context variables helpful for debugging."
    context_extras = {}
    if settings.DEBUG and request.META.get('REMOTE_ADDR') in settings.INTERNAL_IPS:
        current_db = getattr(_threading_local, 'DATABASE', 'default')
        context_extras['debug'] = True
        context_extras['current_db'] = current_db
        context_extras['sql_queries'] = _threading_local.DB_POOL[current_db].queries
    return context_extras
