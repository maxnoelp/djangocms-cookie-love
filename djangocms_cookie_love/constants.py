"""Constants and default values for cookie consent."""

from django.conf import settings

# Cookie settings with defaults
COOKIE_NAME = getattr(settings, "COOKIE_LOVE_COOKIE_NAME", "cookie_love_consent")
COOKIE_DURATION = getattr(settings, "COOKIE_LOVE_COOKIE_DURATION", 365)  # days
COOKIE_SECURE = getattr(settings, "COOKIE_LOVE_COOKIE_SECURE", True)
COOKIE_SAMESITE = getattr(settings, "COOKIE_LOVE_COOKIE_SAMESITE", "Lax")
COOKIE_HTTPONLY = getattr(settings, "COOKIE_LOVE_COOKIE_HTTPONLY", True)

# Default cookie groups created on first setup
DEFAULT_COOKIE_GROUPS = [
    {
        "name": "Essential",
        "slug": "essential",
        "description": ("Required for the website to function properly. These cookies cannot be deactivated."),
        "is_required": True,
        "is_default_enabled": True,
        "order": 0,
        "cookies": [
            {
                "name": "sessionid",
                "provider": "This website",
                "duration": "Session",
                "purpose": "Session management",
            },
            {
                "name": "csrftoken",
                "provider": "This website",
                "duration": "1 year",
                "purpose": "CSRF protection",
            },
            {
                "name": COOKIE_NAME,
                "provider": "This website",
                "duration": f"{COOKIE_DURATION} days",
                "purpose": "Stores your cookie consent preferences",
            },
        ],
    },
    {
        "name": "Analytics",
        "slug": "analytics",
        "description": "Help us understand how visitors use our website so we can improve it.",
        "is_required": False,
        "is_default_enabled": False,
        "order": 1,
        "cookies": [],
    },
    {
        "name": "Marketing",
        "slug": "marketing",
        "description": "Used to deliver personalized advertisements and track their effectiveness.",
        "is_required": False,
        "is_default_enabled": False,
        "order": 2,
        "cookies": [],
    },
    {
        "name": "Preferences",
        "slug": "preferences",
        "description": "Allow the website to remember your preferences such as language or region.",
        "is_required": False,
        "is_default_enabled": False,
        "order": 3,
        "cookies": [],
    },
]
