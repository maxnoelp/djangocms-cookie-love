# djangocms-cookie-love

A GDPR-compliant cookie consent banner plugin for Django CMS with versioning, admin editing, and Bootstrap 5 default design.

## Features

- **GDPR/DSGVO-compliant** – Opt-in by default, granular cookie group control, revocable consent
- **Versioning** – Track changes to cookie policies, force re-consent when needed
- **Admin interface** – Configure banner text, cookie groups, and design through Django Admin
- **Bootstrap 5 design** – Responsive, accessible, easily overridable
- **Django CMS Plugin + Template Tag** – Flexible integration options
- **Consent audit trail** – Documented proof of user consent with hashed IPs
- **Lightweight** – Vanilla JS, no jQuery dependency
- **Internationalization** – Ships with German and English translations

## Requirements

- Python ≥ 3.10
- Django ≥ 4.2
- django-cms ≥ 4.0

## Installation

```bash
pip install djangocms-cookie-love
```

Add to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "djangocms_cookie_love",
    ...
]
```

Add the middleware:

```python
MIDDLEWARE = [
    ...
    "djangocms_cookie_love.middleware.CookieConsentMiddleware",
    ...
]
```

Include the URLs:

```python
urlpatterns = [
    ...
    path("cookie-love/", include("djangocms_cookie_love.urls")),
    ...
]
```

Run migrations:

```bash
python manage.py migrate
```

## Quick Start

### Option 1: Django CMS Plugin

Add the **Cookie Consent Banner** plugin to any CMS placeholder in your template.

### Option 2: Template Tag

```html
{% load cookie_love_tags %}

<!DOCTYPE html>
<html>
  <head>
    ...
  </head>
  <body>
    ... {% cookie_love_banner %}
  </body>
</html>
```

## Configuration

```python
# settings.py

COOKIE_LOVE_IP_SALT = "your-secret-salt-here"      # Salt for IP hashing
COOKIE_LOVE_COOKIE_NAME = "cookie_love_consent"     # Consent cookie name
COOKIE_LOVE_COOKIE_DURATION = 365                    # Days until consent expires
COOKIE_LOVE_COOKIE_SECURE = True                     # Secure flag
COOKIE_LOVE_COOKIE_SAMESITE = "Lax"                  # SameSite policy
```

## Script Blocking

Use `data-cookie-group` to conditionally load scripts:

```html
<script type="text/plain" data-cookie-group="analytics">
  // This script only runs after user consents to "analytics"
</script>
```

## Development

```bash
git clone https://github.com/yourname/djangocms-cookie-love.git
cd djangocms-cookie-love
pip install -e ".[dev]"
pytest
```

## License

MIT License – see [LICENSE](LICENSE) for details.
