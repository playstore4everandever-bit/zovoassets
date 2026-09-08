from pathlib import Path
import os
import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    "SECRET_KEY",
    "django-insecure-zovoassets-dev-key-change-in-production"
)

DEBUG = os.environ.get("DEBUG", "False") == "False"

ALLOWED_HOSTS = [
    'zovoassets.com',
    'www.zovoassets.com',
    'zovoassets.onrender.com',
    '127.0.0.1',
    'localhost',
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "django.contrib.sites",
    "django.contrib.sitemaps",

    "core",
    "investments",
    "loans",
    "trading",
    "deposits",
    "accounts",
]

SITE_ID = 1
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "csp.middleware.CSPMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "zovoassets.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "zovoassets.wsgi.application"

DATABASES = {
    'default': dj_database_url.config(
        default='postgresql://zovoassets_user:WEUOkgIecWSV9K6l4vPDyuJOUNUMYmsi@dpg-dafiv48u01pc73ali2jg-a/zovoassets',
        conn_max_age=600
    )
}

# Railway Postgres
if os.environ.get("DATABASE_URL"):
    import dj_database_url

    DATABASES["default"] = dj_database_url.parse(
        os.environ.get("DATABASE_URL"),
        conn_max_age=600
    )

AUTH_USER_MODEL = "core.User"

LOGIN_URL = "/login/"
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"


STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

STATICFILES_STORAGE = (
    "whitenoise.storage.CompressedManifestStaticFilesStorage"
)

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -----------------------------
# CSRF / SECURITY FIX
# -----------------------------
CSRF_TRUSTED_ORIGINS = [
    "https://zovoassets.com",
    "https://www.zovoassets.com",
    "https://*.railway.app",
    "https://*.up.railway.app",
]


# Security Headers
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')



CSP_DEFAULT_SRC = ("'self'",)
CSP_SCRIPT_SRC = ("'self'", "cdn.jsdelivr.net", "fonts.googleapis.com")
CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "cdn.jsdelivr.net", "fonts.googleapis.com")
CSP_FONT_SRC = ("'self'", "fonts.gstatic.com")
CSP_IMG_SRC = ("'self'", "data:", "images.unsplash.com")
CSP_CONNECT_SRC = ("'self'", "api.coingecko.com", "api.twelvedata.com")