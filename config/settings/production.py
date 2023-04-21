from .base import *  # noqa
from .base import env

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
SECRET_KEY = env("DJANGO_SECRET_KEY")
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["example.com"])

# DATABASES
# ------------------------------------------------------------------------------
DATABASES["default"] = env.db("DATABASE_URL")  # noqa F405
DATABASES["default"]["ATOMIC_REQUESTS"] = True  # noqa F405
DATABASES["default"]["CONN_MAX_AGE"] = env.int("CONN_MAX_AGE", default=60)  # noqa F405

# CACHES
# ------------------------------------------------------------------------------
CACHES = {
    'default': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_DEFAULT_LOCATION"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
            "PASSWORD": os.getenv("REDIS_DEFAULT_PASSWORD"),
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer"
        },
    },
    '1': {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": os.getenv("REDIS_1_LOCATION"),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            "IGNORE_EXCEPTIONS": True,
            "PASSWORD": os.getenv("REDIS_1_PASSWORD"),
            # "SERIALIZER": "django_redis.serializers.json.JSONSerializer"
        },
    }
}

# SECURITY
# # ------------------------------------------------------------------------------
# # https://docs.djangoproject.com/en/dev/ref/settings/#secure-proxy-ssl-header
# SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
# # https://docs.djangoproject.com/en/dev/ref/settings/#secure-ssl-redirect
# SECURE_SSL_REDIRECT = env.bool("DJANGO_SECURE_SSL_REDIRECT", default=False)
# # https://docs.djangoproject.com/en/dev/ref/settings/#session-cookie-secure
SESSION_COOKIE_SECURE = True
# # https://docs.djangoproject.com/en/dev/ref/settings/#csrf-cookie-secure
# CSRF_COOKIE_SECURE = False
# # https://docs.djangoproject.com/en/dev/topics/security/#ssl-https
# # https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-seconds
# # TODO: set this to 60 seconds first and then to 518400 once you prove the former works
# SECURE_HSTS_SECONDS = 60
# # https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-include-subdomains
# SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool(
#     "DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True
# )
# # https://docs.djangoproject.com/en/dev/ref/settings/#secure-hsts-preload
# SECURE_HSTS_PRELOAD = env.bool("DJANGO_SECURE_HSTS_PRELOAD", default=True)
# # https://docs.djangoproject.com/en/dev/ref/middleware/#x-content-type-options-nosniff
# SECURE_CONTENT_TYPE_NOSNIFF = env.bool(
#     "DJANGO_SECURE_CONTENT_TYPE_NOSNIFF", default=True
# )

# STATIC
# ------------------------
# STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
# MEDIA
# ------------------------------------------------------------------------------

# EMAIL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#default-from-email
# DEFAULT_FROM_EMAIL = env(
#     "DJANGO_DEFAULT_FROM_EMAIL",
#     default="Dkhtn_Django <noreply@example.com>",
# )
# # https://docs.djangoproject.com/en/dev/ref/settings/#server-email
# SERVER_EMAIL = env("DJANGO_SERVER_EMAIL", default=DEFAULT_FROM_EMAIL)
# # https://docs.djangoproject.com/en/dev/ref/settings/#email-subject-prefix
# EMAIL_SUBJECT_PREFIX = env(
#     "DJANGO_EMAIL_SUBJECT_PREFIX",
#     default="[Dkhtn_Django]",
# )

# ADMIN
# ------------------------------------------------------------------------------
# Django Admin URL regex.
ADMIN_URL = env("DJANGO_ADMIN_URL")

# Anymail
# ------------------------------------------------------------------------------
# https://anymail.readthedocs.io/en/stable/installation/#installing-anymail
# INSTALLED_APPS += ["anymail"]  # noqa F405
# https://docs.djangoproject.com/en/dev/ref/settings/#email-backend
# https://anymail.readthedocs.io/en/stable/installation/#anymail-settings-reference
# https://anymail.readthedocs.io/en/stable/esps/mailgun/
# EMAIL_BACKEND = "anymail.backends.mailgun.EmailBackend"
# ANYMAIL = {
#     "MAILGUN_API_KEY": env("MAILGUN_API_KEY"),
#     "MAILGUN_SENDER_DOMAIN": env("MAILGUN_DOMAIN"),
#     "MAILGUN_API_URL": env("MAILGUN_API_URL", default="https://api.mailgun.net/v3"),
# }


# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}

# Your stuff...
# ------------------------------------------------------------------------------
rabbitmq_host = os.getenv("RABBITMQ_HOST")

RSA_PRIVATE_KEY = '''-----BEGIN RSA PRIVATE KEY-----
MIICXgIBAAKBgQCzajFWnkVU8zhcElaooCEEMZMSbHZpKP0rqzqlz1Z62LHZh6eT
yjFtKOw+qRSYE4nUlt7k0glBk3M4VqBsLdjxAm5cchzN7EngUZj/ddKZs0Wmsm7O
5KVePIRcHS3B3zfJT+g9v6OEDJafSn23JbK8yTGVooCEG6gQIkg16Hz5HwIDAQAB
AoGASXrvlBMkQCOQ7JySI2PZwdbv7ja/1Ff2QGFTlr8xIwUG6hmV94By98sv3oXv
Kk2uQIQ966deJR5XrTZFY6jvVS2VORq0/peNodfx++CB3XUTpT9TN/2caLLlvNvN
kWnqzuNEfYZA/XKqy5zEwlVHB+LZMIcVJyD0Td5wmK0OOLkCQQDCnfpH8reN8ZTC
ZYthx0OMasMmfRokXWIv55dwRZ4jytstzAL3txFXbcXU1NWmyR2QEqNhoQvriz5V
8MU9GjS7AkEA7AC7lyGO0HOAlUwU0jVXNgTXhRxa/ACLbQFV5me7bu50DPYyCZD8
IR0nVEFbtfhO8iaI4P52/qVtztYDXJ/47QJBAJtQlEMDEzX2jC+v9lJsQh43vdJj
mI9Y71knzBXPmWsbI1wjKmMi+HX7pxw5VuCqNCuclEL/0ZGDKJZRdjdTSK0CQQCd
Ose/ol3RRoIt9SgR+/OES6mCRyfeqEY7cx5ViFp5R2gNkqA3e15eeVvQaFK/YxTF
gyLCMwX4FSKZID/RH8rpAkEAkbndGyu8JGtRBwuJPQqWtF4fdPHc+rFXIVHqqkIc
Irwt1ieL8Gm+Zd/IcKQQdz2UxkLwk6Yxgc78mfeb4ZZhow==
-----END RSA PRIVATE KEY-----'''