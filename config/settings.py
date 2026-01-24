import logging
import os
from datetime import timedelta
from pathlib import Path
from urllib.parse import parse_qsl, urlparse

from decouple import Csv, config

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", cast=str)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config("DEBUG", cast=bool, default=False)
logger.info("DEBUG: " + str(DEBUG))

ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())
logger.info("ALLOWED_HOSTS: " + str(ALLOWED_HOSTS))

# APPLICATION SECURITY
SECURE_HSTS_SECONDS = 3600  # 1 hour
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", cast=bool, default=False)
SESSION_COOKIE_SECURE = config("SESSION_COOKIE_SECURE", cast=bool, default=True)
CSRF_COOKIE_SECURE = config("CSRF_COOKIE_SECURE", cast=bool, default=True)
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS", cast=lambda v: [s.strip() for s in v.split(",")], default=[]
)


REST_FRAMEWORK = {
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",  # Or your chosen scheme
    "ALLOWED_VERSIONS": ["v1", "v2"],  # List of allowed versions
    "DEFAULT_VERSION": "v1",  # The default version to use if not specified
    "VERSION_PARAM": "version",
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# JSON WEB TOKENS CONFIGURAITONS
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(config("ACCESS_TOKEN_LIFETIME", cast=int)),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=config("REFRESH_TOKEN_LIFETIME", cast=int)),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
}

SPECTACULAR_SETTINGS = {
    "TITLE": "ELD Project API",
    "DESCRIPTION": "Electronice Logging Digital Backend Project",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    # OTHER SETTINGS
}

CORS_ALLOWED_ORIGINS = CSRF_TRUSTED_ORIGINS

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
]

THIRD_PARTY_APPS = [
    "guardian",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "corsheaders",
]

# Custom apps
CUSTOM_APPS = [
    # Add your custom apps here
    "eld",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + CUSTOM_APPS


AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
]

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "guardian.backends.ObjectPermissionBackend",
]
# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases
DATABASES = {}
USE_SQLITE = config("USE_SQLITE", cast=bool)
USE_MYSQL = config("USE_MYSQL", cast=bool)
USE_POSTGRES = config("USE_POSTGRES", cast=bool)

if USE_SQLITE:
    logger.info(f"USE_SQLITE: {USE_SQLITE}")
    DATABASES.update(
        {
            "default": {
                "ENGINE": "django.db.backends.sqlite3",
                "NAME": BASE_DIR / "db.sqlite3",
            }
        }
    )
elif USE_MYSQL:
    logger.info(f"USE_MYSQL: {USE_MYSQL}")
    DATABASES.update(
        {
            "default": {
                "ENGINE": "django.db.backends.mysql",
                "NAME": config("MYSQL_NAME"),
                "USER": config("MYSQL_USERNAME"),
                "HOST": config("MYSQL_HOST"),
                "PORT": config("MYSQL_PORT"),
                "PASSWORD": config("MYSQL_PASSWORD"),
            }
        }
    )
elif USE_POSTGRES:
    tmpPostgres = urlparse(config("DATABASE_URL", cast=str))  # pyright: ignore[reportArgumentType] # noqa: N816
    logger.info(f"USE_POSTGRES: {USE_POSTGRES}")
    DATABASES.update(
        {
            "default": {
                "ENGINE": "django.db.backends.postgresql",
                "NAME": tmpPostgres.path.replace("/", ""),
                "USER": tmpPostgres.username,
                "PASSWORD": tmpPostgres.password,
                "HOST": tmpPostgres.hostname,
                "PORT": 5432,
                "OPTIONS": dict(parse_qsl(tmpPostgres.query)),
            }
        }
    )
else:
    logger.error("No Database configured")


# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles_build", "static")

MEDIA_URL = "/media/"
MEDIA_ROOT = config("MEDIA_ROOT", default=os.path.join(BASE_DIR, "media"))

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {message}",
            "style": "{",
        },
        "simple": {"format": "{levelname} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"level": "INFO", "class": "logging.StreamHandler", "formatter": "simple"},
    },
    "loggers": {
        "django": {
            "handlers": [
                "console",
            ],
            "level": "INFO",
            "propagate": True,
        },
        # customize logs for apps
        "eld.views": {
            "handlers": [
                "console",
            ],
            "level": "INFO",
            "propagrate": True,
        },
    },
}
