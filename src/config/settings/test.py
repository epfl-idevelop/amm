"""(c) All rights reserved. ECOLE POLYTECHNIQUE FEDERALE DE LAUSANNE, Switzerland, VPSI, 2017"""

from .base import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ENVIRONMENT_ID = "1a7"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'HOST': '127.0.0.1',
        'NAME': 'test',
        'USER': 'test',
        'PASSWORD': 'test',
    }
}

DOMAIN = ".db.test-rsaas.epfl.ch"
