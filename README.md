# djangocms-cookie-love

A GDPR-compliant cookie consent management plugin for Django CMS with granular control, versioning, and a modern Bootstrap 5 design.

![Version](https://img.shields.io/badge/version-0.1.0-blue)
![Python](https://img.shields.io/badge/python-≥3.10-blue)
![Django](https://img.shields.io/badge/django-≥4.2-green)
![Django CMS](https://img.shields.io/badge/django--cms-≥4.0-green)
![Tests](https://img.shields.io/badge/tests-116%20passing-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-93%25-brightgreen)
![License](https://img.shields.io/badge/license-MIT-lightgrey)

## Features

- **GDPR/TTDSG-compliant** – Opt-in by default, no pre-selected optional cookies
- **Granular consent** – Per cookie group _and_ per individual cookie control
- **Versioning** – Track policy changes, force re-consent when the version changes
- **Consent audit trail** – Full documentation of every consent decision (timestamp, IP hash, version, method)
- **Admin interface** – Configure banner, cookie groups, and individual cookies through Django Admin
- **CMS Plugin + Template Tags** – Flexible integration: drag & drop plugin or `{% cookie_love_banner %}`
- **Script blocking** – Conditionally load `<script>` tags based on consent via `data-cookie-group`
- **Cookie-level script blocking** – Block scripts per individual cookie via `data-cookie-slug`
- **Bootstrap 5 design** – Responsive, mobile-first, easily themeable with CSS custom properties
- **Accessible** – ARIA attributes, keyboard navigation, focus trap in settings modal
- **Vanilla JS** – No jQuery or other dependencies, ~700 lines
- **i18n** – Ships with English and German translations
- **Pre-commit hooks** – Ruff linting and formatting enforced on every commit

## Architecture

```
┌─────────────────────────────────────────────────────┐
│  Browser                                            │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  Banner   │  │ Settings     │  │ cookie-love  │  │
│  │  (HTML)   │→ │ Modal (HTML) │→ │ .js          │  │
│  └──────────┘  └──────────────┘  └──────┬───────┘  │
│                                         │ XHR      │
├─────────────────────────────────────────┼───────────┤
│  Server                                 ▼           │
│  ┌──────────────────────────────────────────────┐   │
│  │  API Views                                   │   │
│  │  GET  /cookie-love/api/config/               │   │
│  │  GET  /cookie-love/api/consent/              │   │
│  │  POST /cookie-love/api/consent/              │   │
│  │  POST /cookie-love/api/consent/revoke/       │   │
│  └──────────────────┬───────────────────────────┘   │
│                     ▼                               │
│  ┌──────────────────────────────────────────────┐   │
│  │  Models                                      │   │
│  │  CookieConsentConfig (singleton)             │   │
│  │  CookieGroup → Cookie (individual items)     │   │
│  │  ConsentVersion (policy snapshots)           │   │
│  │  UserConsent (audit trail)                   │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘
```

## Data Models

| Model                 | Purpose                                                              |
| --------------------- | -------------------------------------------------------------------- |
| `CookieConsentConfig` | Singleton – banner text, button labels, links, position              |
| `CookieGroup`         | Category of cookies (e.g. Essential, Analytics, Marketing)           |
| `Cookie`              | Individual cookie within a group (name, provider, duration, purpose) |
| `ConsentVersion`      | Snapshot of the current policy; triggers re-consent on change        |
| `UserConsent`         | Audit record: accepted groups/cookies, timestamp, IP hash, method    |

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

Add the middleware (after `SessionMiddleware`):

```python
MIDDLEWARE = [
    ...
    "djangocms_cookie_love.middleware.CookieConsentMiddleware",
    ...
]
```

Add the context processor:

```python
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

This creates default cookie groups (Essential, Analytics, Marketing, Preferences).

## Quick Start

### Option 1: Template Tags (recommended)

```html
{% load cookie_love_tags %}
<!DOCTYPE html>
<html>
  <head>
    {% cookie_love_css %}
  </head>
  <body>
    ... {% cookie_love_banner %} {% cookie_love_js %}
  </body>
</html>
```

### Option 2: Django CMS Plugin

Add the **Cookie Consent Banner** plugin to any CMS placeholder. The banner renders automatically with all configuration from the admin.

> **Note:** Use either the template tag _or_ the plugin, not both – otherwise the banner appears twice.

## Configuration

```python
# settings.py

# Required
COOKIE_LOVE_IP_SALT = "your-secret-salt-here"        # Salt for IP address hashing

# Optional (shown with defaults)
COOKIE_LOVE_COOKIE_NAME = "cookie_love_consent"       # Browser cookie name
COOKIE_LOVE_COOKIE_DURATION = 365                      # Days until consent expires
COOKIE_LOVE_COOKIE_SECURE = True                       # Set to False for local dev (HTTP)
COOKIE_LOVE_COOKIE_SAMESITE = "Lax"                    # SameSite policy
COOKIE_LOVE_COOKIE_HTTPONLY = True                      # HttpOnly flag
```

## Script Blocking

### By cookie group

Scripts with `data-cookie-group` are only executed after the user consents to that group:

```html
<script type="text/plain" data-cookie-group="analytics">
  // Runs only after user consents to "analytics"
</script>

<script
  type="text/plain"
  data-cookie-group="analytics"
  data-src="https://www.googletagmanager.com/gtag/js?id=G-XXX"
>
  // External script – loaded only after consent
</script>
```

### By individual cookie

For finer control, block scripts per individual cookie:

```html
<script type="text/plain" data-cookie-group="analytics" data-cookie-slug="ga">
  // Runs only if the user consented to the "ga" cookie in the "analytics" group
</script>
```

## JavaScript API

```javascript
// Open/close settings modal
CookieLove.openSettings();
CookieLove.closeSettings();

// Programmatic consent
CookieLove.acceptAll();
CookieLove.rejectAll();
CookieLove.saveSettings();

// Query consent state
CookieLove.getConsent(); // { acceptedGroups, acceptedCookies }
CookieLove.hasConsent("analytics"); // true/false
CookieLove.hasCookieConsent("analytics", "ga"); // true/false

// React to consent changes
CookieLove.onConsent(function (groups, cookies) {
  console.log("Accepted groups:", groups);
  console.log("Accepted cookies:", cookies);
});

// Revoke consent
CookieLove.revokeConsent();
```

### Events

```javascript
document.addEventListener("cookie-love:consent", function (e) {
  console.log(e.detail.acceptedGroups);
  console.log(e.detail.acceptedCookies);
});

document.addEventListener("cookie-love:revoke", function (e) {
  console.log("Consent revoked");
});
```

## Theming

Override CSS custom properties to match your brand:

```css
:root {
  --cl-primary: #6b21a8;
  --cl-primary-hover: #581c87;
  --cl-primary-subtle: #f3e8ff;
  --cl-bg: #ffffff;
  --cl-text: #1e1b2e;
  --cl-border: #e5e7eb;
  --cl-radius: 1rem;
}
```

## Admin Interface

1. **Cookie Consent Config** – Configure banner title, description, button labels, links, position
2. **Cookie Groups** – Add/edit cookie categories with inline cookie management
3. **Consent Versions** – Publish new versions to trigger re-consent
4. **User Consents** – Read-only audit log with CSV export

## Middleware

The `CookieConsentMiddleware` sets these attributes on every request:

| Attribute                         | Type                    | Description                           |
| --------------------------------- | ----------------------- | ------------------------------------- |
| `request.cookie_consent`          | `UserConsent` or `None` | The user's consent record             |
| `request.cookie_consent_required` | `bool`                  | Whether the banner should be shown    |
| `request.cookie_consent_groups`   | `list[str]`             | Accepted group slugs                  |
| `request.cookie_consent_cookies`  | `list[str]`             | Accepted cookie refs (`group:cookie`) |

Use in templates:

```html
{% if request.cookie_consent_required %}
<!-- Banner will show automatically via JS -->
{% endif %} {% if "analytics" in request.cookie_consent_groups %}
<!-- Server-side conditional rendering -->
{% endif %}
```

## Development

```bash
git clone https://github.com/noelpmax/djangocms-cookie-love.git
cd djangocms-cookie-love
python -m venv .venv
source .venv/bin/activate          # Linux/macOS
# .venv\Scripts\activate           # Windows
pip install -e ".[dev]"
pre-commit install
pytest
```

### Example Project

```bash
cd example
./setup.sh
python manage.py runserver
```

Visit `http://localhost:8000` to see the banner in action.

### Code Quality

Pre-commit hooks enforce on every commit:

- **ruff check** – Linting (pycodestyle, pyflakes, isort, bugbear, pyupgrade, flake8-django)
- **ruff format** – Code formatting
- **trailing-whitespace** / **end-of-file-fixer** – File hygiene

## GDPR Compliance

This package implements the following GDPR/TTDSG requirements:

| Requirement                       | Implementation                                               |
| --------------------------------- | ------------------------------------------------------------ |
| Opt-in by default                 | No optional cookies pre-selected                             |
| Granular control                  | Per group and per individual cookie                          |
| Informed consent                  | Cookie name, provider, duration, purpose displayed           |
| Revocable consent                 | `CookieLove.openSettings()` / `CookieLove.revokeConsent()`   |
| Documented consent                | `UserConsent` model with timestamp, IP hash, version, method |
| IP anonymization                  | SHA-256 hash with configurable salt                          |
| Version tracking                  | `ConsentVersion` with automatic re-consent                   |
| Essential cookies without consent | `is_required` groups are always active                       |

## Further Reading

- [**TESTING.md**](TESTING.md) – Test coverage report (116 tests, 93% coverage)
- [**idea/**](idea/) – Planned features and ideas
  - [Plain Django support](idea/plain-django-support.md) – Making Django CMS optional
- [**CHANGELOG.md**](CHANGELOG.md) – Version history

## License

MIT License – see [LICENSE](LICENSE) for details.
