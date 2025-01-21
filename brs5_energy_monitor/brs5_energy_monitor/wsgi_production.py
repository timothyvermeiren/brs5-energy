"""
WSGI config for brs5_energy_monitor project. This specific one was copied and then adjusted manually to fir for use with Apache2.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

# See: https://gist.github.com/GrahamDumpleton/b380652b768e81a7f60c

import os

os.environ["DJANGO_ALLOWED_HOSTS"] = "127.0.0.1,localhost,192.168.68.67,brs5-energy.duckdns.org,brs5-energy.08082020.be,brs5-energy.morregen.be"
os.environ["DJANGO_SETTINGS_MODULE"] = "brs5_energy_monitor.settings"

# Database
os.environ["BRS5_ENERGY_POSTGRES_DB_SERVER"] = "192.168.68.85"
os.environ["BRS5_ENERGY_POSTGRES_DB_PORT"] = "5432"
os.environ["BRS5_ENERGY_POSTGRES_DB_USER"] = "brs5_energy"
os.environ["BRS5_ENERGY_POSTGRES_DB_PASSWORD"] = "FiZk_ihcy7UzuyU-g*KbGcCNZ4Qz"
os.environ["BRS5_ENERGY_POSTGRES_DB_NAME"] = "brs5_energy"

from django.core.wsgi import get_wsgi_application
from django.core.management import call_command

application = get_wsgi_application()
# Our database isn't local, so we "need to migrate each time"
# See: https://stackoverflow.com/questions/58168161/django-applying-database-migration-on-server-start-with-wsgi
call_command("migrate")