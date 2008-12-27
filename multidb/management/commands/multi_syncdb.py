from django.core.management.base import NoArgsCommand
from django.core.management import call_command
from django.conf import settings

class Command(NoArgsCommand):
    help = "Sync multiple databases."

    def handle_noargs(self, **options):
        for name, database in settings.DATABASES.iteritems():
            print "Running syncdb for %s" % (name,)
            for key, value in database.iteritems():
                setattr(settings, key, value)
            call_command('syncdb')
