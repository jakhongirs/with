from .base import *  # noqa

###################################################################
# General
###################################################################

DEBUG = False

###################################################################
# Django security
###################################################################

USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

CSRF_COOKIE_SECURE = False
CSRF_TRUSTED_ORIGINS = ["http://45.159.220.240:8080"]
CSRF_COOKIE_DOMAIN = "45.159.220.240"
CSRF_USE_SESSIONS = True
SESSION_COOKIE_SECURE = False

###################################################################
# CORS
###################################################################

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = ["*"]

REDIS_HOST = env.str("REDIS_HOST", "redis")
REDIS_PORT = env.int("REDIS_PORT", 6379)
REDIS_DB = env.int("REDIS_DB", 0)

ALLOWED_HOSTS = ["45.159.220.240", "localhost", "127.0.0.1"]
