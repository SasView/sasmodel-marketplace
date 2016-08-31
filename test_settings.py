from sasmarket.settings import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'marketplace_default',
    },
    'other': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'marketplace_other',
    }
}
