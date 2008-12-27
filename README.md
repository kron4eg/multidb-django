==============
django-multidb
==============

App which make you able to work with multiple databases from django ORM.

!WARNING!
---------

Code is still alfa quality. And it switches database GLOBALLY (per thread), for all models!

Based on: <http://www.eflorenzano.com/blog/post/easy-multi-database-support-django/>

Usage
-----

Insert `multidb` in `INSTALLED_APPS`

    INSTALLED_APPS = (
        'multidb'
        'django.contrib.sessions',
        'django.contrib.sites',
        ...
    )

Configure your databases.

    DATABASES = dict(
        default = dict(
            DATABASE_ENGINE=DATABASE_ENGINE,
            DATABASE_NAME=DATABASE_NAME,
            DATABASE_USER=DATABASE_USER,
            DATABASE_PASSWORD=DATABASE_PASSWORD,
            DATABASE_HOST=DATABASE_HOST,
            DATABASE_PORT=DATABASE_PORT,
        ),
        second = dict(
            DATABASE_ENGINE=DATABASE_ENGINE,
            DATABASE_NAME='another_DB',
            DATABASE_USER='user',
            DATABASE_PASSWORD='pass',
            DATABASE_HOST='host',
            DATABASE_PORT='',
        ),
    )

Don't use database backend for sessions.

    from multidb.db import switch_db
    from models import SomeModel

    # Select using default database
    SomeModel.objects.all()

    # And second database
    switch_db('second')
    SomeModel.objects.all()

    from multidb.db import get_object_anywhere, get_object_from

    # This will return first founded object with pk=1345, or None if case of fail.
    get_object_anywhere(SomeModel, pk=1345)

    #this will search only in listed databases
    get_object_from(['db1', 'db2'], SomeModel, pk=1345)

TODO
----

* Implement per model switch, using manager
* Implement partitioning tables
* Implement connection pooling

