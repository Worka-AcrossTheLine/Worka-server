from .comm import *

INSTALLED_APPS += [
    'debug_toolbar',
]

MIDDLEWARE = ["debug_toolbar.middleware.DebugToolbarMiddleware"] + MIDDLEWARE

CORS_ORIGIN_ALLOW_ALL = True

INTERNAL_IPS = ["127.0.0.1"]