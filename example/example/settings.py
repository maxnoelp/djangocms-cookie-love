"""
Django settings for the cookie-love example project.

A minimal Django CMS setup for manually testing the cookie consent banner.
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "example-only-not-for-production-change-me"

DEBUG = True

ALLOWED_HOSTS = ["*"]

X_FRAME_OPTIONS = "SAMEORIGIN"

# ---------------------------------------------------------------------------
# Installed apps
# ---------------------------------------------------------------------------

INSTALLED_APPS = [
    "djangocms_admin_style",
    # Django
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    # Django CMS
    "cms",
    "menus",
    "treebeard",
    "sekizai",
    # Cookie Love
    "djangocms_cookie_love",
    "djangocms_cookie_love.contrib.cms.apps.CookieLoveCmsConfig",
    # Example app
    "example",
]

SITE_ID = 1

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "cms.middleware.utils.ApphookReloadMiddleware",
    "cms.middleware.user.CurrentUserMiddleware",
    "cms.middleware.page.CurrentPageMiddleware",
    "cms.middleware.toolbar.ToolbarMiddleware",
    "cms.middleware.language.LanguageCookieMiddleware",
    "djangocms_cookie_love.middleware.CookieConsentMiddleware",
]

ROOT_URLCONF = "example.urls"

# ---------------------------------------------------------------------------
# Templates
# ---------------------------------------------------------------------------

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "sekizai.context_processors.sekizai",
                "cms.context_processors.cms_settings",
                "djangocms_cookie_love.context_processors.cookie_consent",
            ],
        },
    },
]

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# ---------------------------------------------------------------------------
# Static files
# ---------------------------------------------------------------------------

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ---------------------------------------------------------------------------
# Internationalization
# ---------------------------------------------------------------------------

LANGUAGE_CODE = "de"

LANGUAGES = [
    ("de", "Deutsch"),
    ("en", "English"),
]

USE_I18N = True
USE_L10N = True
USE_TZ = True
TIME_ZONE = "Europe/Berlin"

# ---------------------------------------------------------------------------
# Django CMS
# ---------------------------------------------------------------------------

CMS_CONFIRM_VERSION4 = True

CMS_TEMPLATES = [
    ("base.html", "Standard"),
    ("fullwidth.html", "Volle Breite"),
    ("home.html", "Dokumentation"),
    ("datenschutz.html", "Datenschutz"),
    ("impressum.html", "Impressum"),
]

# ---------------------------------------------------------------------------
# Cookie Love
# ---------------------------------------------------------------------------

COOKIE_LOVE_IP_SALT = "example-salt-change-in-production"
COOKIE_LOVE_COOKIE_SECURE = False  # True in production with HTTPS
