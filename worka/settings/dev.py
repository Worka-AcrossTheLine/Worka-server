from .comm import *

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

CORS_ORIGIN_ALLOW_ALL = True

INTERNAL_IPS = type(str('c'), (), {'__contains__': lambda *a: True})()