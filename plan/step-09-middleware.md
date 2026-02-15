# Step 09 – Middleware

## Goal

Provide a Django middleware that checks cookie consent status on each request and makes consent information available to templates and views.

## Tasks

### 9.1 `CookieConsentMiddleware`

```python
# middleware.py
from django.conf import settings
from .models import CookieConsentConfig, UserConsent, ConsentVersion


class CookieConsentMiddleware:
    """
    Checks the user's cookie consent status on each request.

    Sets the following on `request`:
    - `request.cookie_consent` – UserConsent instance or None
    - `request.cookie_consent_required` – True if banner should be shown
    - `request.cookie_consent_groups` – list of accepted group slugs
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._process_consent(request)
        response = self.get_response(request)
        return response

    def _process_consent(self, request):
        cookie_name = getattr(settings, "COOKIE_LOVE_COOKIE_NAME", "cookie_love_consent")
        consent_id = request.COOKIES.get(cookie_name)

        request.cookie_consent = None
        request.cookie_consent_required = True
        request.cookie_consent_groups = []

        if not consent_id:
            return

        try:
            consent = UserConsent.objects.select_related("version").get(
                consent_id=consent_id
            )
        except (UserConsent.DoesNotExist, ValueError):
            return

        # Check if consent is still valid (version not outdated)
        config = CookieConsentConfig.get_active()
        if not config:
            return

        current_version = config.get_current_version()
        if current_version and current_version != consent.version:
            if current_version.requires_reconsent:
                return  # Consent outdated, show banner again

        request.cookie_consent = consent
        request.cookie_consent_required = False
        request.cookie_consent_groups = list(
            consent.accepted_groups.values_list("slug", flat=True)
        )
```

### 9.2 Context Processor

Make consent data available in all templates:

```python
# context_processors.py
def cookie_consent(request):
    return {
        "cookie_consent": getattr(request, "cookie_consent", None),
        "cookie_consent_required": getattr(request, "cookie_consent_required", True),
        "cookie_consent_groups": getattr(request, "cookie_consent_groups", []),
    }
```

### 9.3 Installation

```python
# settings.py

MIDDLEWARE = [
    ...
    "djangocms_cookie_love.middleware.CookieConsentMiddleware",
    ...
]

TEMPLATES = [
    {
        ...
        "OPTIONS": {
            "context_processors": [
                ...
                "djangocms_cookie_love.context_processors.cookie_consent",
            ],
        },
    },
]
```

### 9.4 Template Usage

```html
<!-- Conditional rendering based on consent -->
{% if "analytics" in cookie_consent_groups %}
<!-- Load analytics scripts -->
{% endif %}

<!-- Show banner if consent is needed -->
{% if cookie_consent_required %} {% cookie_love_banner %} {% endif %}
```

## Performance Considerations

- Middleware uses `select_related` to minimize DB queries
- Consent lookup is a single query by UUID (indexed)
- Config uses `get_active()` which can be cached
- Consider adding `@lru_cache` or Django cache for config lookup
- Middleware should be placed after `SessionMiddleware` and `AuthenticationMiddleware`

## Verification

- [ ] `request.cookie_consent` is set correctly
- [ ] `request.cookie_consent_required` is True when no consent exists
- [ ] `request.cookie_consent_required` is True when version requires re-consent
- [ ] `request.cookie_consent_groups` contains accepted group slugs
- [ ] Context processor makes data available in templates
- [ ] Invalid/expired consent IDs are handled gracefully
- [ ] Performance: single DB query for consent lookup
