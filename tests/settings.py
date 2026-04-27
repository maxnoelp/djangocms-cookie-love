"""Django test settings for djangocms-cookie-love."""

SECRET_KEY = "test-secret-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.admin",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.messages",
    "cms",
    "menus",
    "treebeard",
    "djangocms_cookie_love",
    "djangocms_cookie_love.contrib.cms.apps.CookieLoveCmsConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "djangocms_cookie_love.middleware.CookieConsentMiddleware",
]

ROOT_URLCONF = "tests.urls"

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
                "djangocms_cookie_love.context_processors.cookie_consent",
            ],
        },
    },
]

STATIC_URL = "/static/"
SITE_ID = 1
CMS_CONFIRM_VERSION4 = True

# Cookie Love settings
COOKIE_LOVE_IP_SALT = "test-salt"
COOKIE_LOVE_COOKIE_NAME = "cookie_love_consent"
COOKIE_LOVE_COOKIE_DURATION = 365
COOKIE_LOVE_COOKIE_SECURE = False  # For testing
