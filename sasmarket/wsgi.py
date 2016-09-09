"""
WSGI config for sasmarket project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""

import os
import time
import traceback
import signal
import sys
from django.core.wsgi import get_wsgi_application

try:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sasmarket.settings")
    application = get_wsgi_application()
    print "WSGI without exception"
except:
    print "Handling WSGI exception"
    print "Pyton maxunicode: {}".format(sys.maxunicode)
    if 'mod_wsgi' in sys.modules:
        traceback.print_exc()
        os.kill(os.getpid(), signal.SIGINT)
        time.sleep(2.5)
