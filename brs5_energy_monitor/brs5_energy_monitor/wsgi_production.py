"""
WSGI config for brs5_energy_monitor project. This specific one was copied and then adjusted manually to fir for use with Apache2.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

# See: https://gist.github.com/GrahamDumpleton/b380652b768e81a7f60c

import os

os.environ["DJANGO_ALLOWED_HOSTS"] = "127.0.0.1,localhost,192.168.68.67,brs5-energy.duckdns.org"
os.environ["DJANGO_SETTINGS_MODULE"] = "brs5_energy_monitor.settings"

# Database
# To connect to Postgres when using WSL, where postgres is on the Windows host but we're running Django in WSL, find the IP address with this (run in WSL):
# ipconfig.exe | grep 'vEthernet (WSL)' -A4 | cut -d":" -f 2 | tail -n1 | sed -e 's/\s*//g'
# Use localhost when... local.
os.environ["BRS5_ENERGY_POSTGRES_DB_SERVER"] = "localhost"
os.environ["BRS5_ENERGY_POSTGRES_DB_PORT"] = "5432"
os.environ["BRS5_ENERGY_POSTGRES_DB_USER"] = "brs5_energy"
os.environ["BRS5_ENERGY_POSTGRES_DB_PASSWORD"] = "FiZk_ihcy7UzuyU-g*KbGcCNZ4Qz"
os.environ["BRS5_ENERGY_POSTGRES_DB_NAME"] = "brs5_energy"

from django.core.wsgi import get_wsgi_application


application = get_wsgi_application()
