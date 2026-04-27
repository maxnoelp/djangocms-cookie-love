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
COOKIE_LOVE_CONSENT_RETENTION_DAYS = 1095              # Days to keep consent records (default: 3 years)
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

The banner and settings modal are styled with CSS custom properties. There are three levels of customisation, from a quick colour swap to a fully custom layout.

### Level 1 – CSS Custom Properties (recommended)

Add overrides anywhere in your CSS — no template changes needed:

```css
:root {
  --cl-primary: #e11d48;          /* Brand colour (buttons, titles, links) */
  --cl-primary-hover: #be123c;    /* Hover state of the primary colour */
  --cl-primary-light: #fff1f2;    /* Light tint (modal header background) */
  --cl-primary-subtle: #ffe4e6;   /* Subtle tint (badge background) */
  --cl-bg: #ffffff;               /* Banner / modal background */
  --cl-text: #1e1b2e;             /* Primary text colour */
  --cl-text-muted: #6b7280;       /* Secondary / description text */
  --cl-border: #e5e7eb;           /* Divider and border colour */
  --cl-shadow: 0 -4px 32px rgba(225, 29, 72, 0.08);  /* Banner shadow */
  --cl-border-radius: 1rem;       /* Corner radius of banner and modal */
  --cl-border-radius-sm: 0.625rem;/* Corner radius of buttons */
  --cl-max-width: 720px;          /* Maximum width of banner / modal */
  --cl-font: system-ui, sans-serif; /* Font stack */
  --cl-z-index: 9999;             /* Banner z-index */
  --cl-modal-z-index: 10000;      /* Settings modal z-index */
}
```

**Example: dark mode**

```css
:root {
  --cl-bg: #1e1e2e;
  --cl-text: #cdd6f4;
  --cl-text-muted: #a6adc8;
  --cl-border: #313244;
  --cl-primary: #cba6f7;
  --cl-primary-hover: #b4befe;
  --cl-primary-light: #1e1e2e;
  --cl-primary-subtle: #313244;
}
```

**Example: square, full-width corporate style**

```css
:root {
  --cl-border-radius: 0;
  --cl-border-radius-sm: 0;
  --cl-max-width: 100%;
  --cl-primary: #003366;
  --cl-primary-hover: #002244;
  --cl-primary-light: #e6edf5;
  --cl-primary-subtle: #ccdaeb;
}
```

### Level 2 – Banner position

Set the position directly in the Django admin (`bottom`, `top`, or `center`) — no code changes needed.

### Level 3 – Template override

Copy the templates you want to customise into your own `templates/` directory and edit them freely:

```
your_project/
└── templates/
    └── djangocms_cookie_love/
        ├── banner.html           # Main banner
        ├── settings_modal.html   # Settings modal wrapper
        └── includes/
            ├── cookie_group.html # Individual group row with toggle
            └── cookie_item.html  # Individual cookie row with checkbox
```

Django's template loader will pick up your versions automatically — no settings change required.

## Admin Interface

1. **Cookie Consent Config** – Configure banner title, description, button labels, links, position. An initial consent version (`1.0`) is created automatically when you save a new config.
2. **Cookie Groups** – Add/edit cookie categories with inline cookie management
3. **Consent Versions** – Publish new versions to trigger re-consent. Create a new version with `requires_reconsent=True` whenever you make a significant policy change — all users will be shown the banner again.
4. **User Consents** – Read-only audit log with CSV export
5. **Discovered Cookies** – Cookies observed at runtime that aren't in the catalog yet (see [Cookie discovery](#cookie-discovery))

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

## Cookie discovery

Two complementary mechanisms surface cookies that aren't yet documented in the
catalog so editors can review and either add or dismiss them. Both write to the
`DiscoveredCookie` model — only cookie *names* and *domains* are stored, never
values.

### 1. Server-side middleware (optional)

`CookieDiscoveryMiddleware` inspects every outgoing response and records any
`Set-Cookie` whose name isn't in the catalog. Catches cookies set by Django,
including `HttpOnly` ones; misses cookies set by client-side JS or third
parties.

```python
MIDDLEWARE = [
    ...
    "djangocms_cookie_love.middleware.CookieConsentMiddleware",
    "djangocms_cookie_love.middleware.CookieDiscoveryMiddleware",  # optional
]
```

Adds one cached lookup and at most one DB write per response that sets an
unknown cookie. Recommended in staging; sample or disable in production.

### 2. Playwright crawler (optional contrib app)

For third-party and JS-set cookies you need a real browser. Install the optional
extra:

```bash
pip install "djangocms-cookie-love[playwright]"
playwright install chromium
```

Add the contrib app:

```python
INSTALLED_APPS = [
    ...
    "djangocms_cookie_love.contrib.playwright",   # adds the crawler command
]
```

Configure the URLs and (optional) login users:

```python
COOKIE_LOVE_DISCOVERY_URLS = [
    "/",
    "/contact/",
    "/privacy/",
    "/imprint/",
]
COOKIE_LOVE_DISCOVERY_USERS = [
    {"label": "regular", "username": "alice", "password": "..."},
]
COOKIE_LOVE_DISCOVERY_LOGIN_URL = "/admin/login/"  # default
```

Run the crawl:

```bash
python manage.py discover_cookies --base-url=https://staging.example.com
python manage.py discover_cookies --include-cms-pages    # one page per CMS template
python manage.py discover_cookies --anon-only            # skip authenticated sweeps
```

The crawler walks `(anon + each configured user) × (no-consent, rejected,
accepted) × URLs` in fresh browser contexts and tags each finding with the
sweep it came from in the `seen_in` field — so a cookie that appears in the
*no-consent* sweep is a compliance bug, while the same cookie in *accepted* is
expected.

> Don't crawl as staff/superuser — toolbar and admin assets inject cookies a
> public visitor never sees.

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
| Immutable audit trail             | Admin blocks add/change/delete on `UserConsent`              |
| Storage limitation (Art. 5(1)(e)) | `purge_old_consents` management command (default: 3 years)   |
| User-Agent storage                | Stored pseudonymously for audit purposes; mention in your privacy policy |

### Data Retention

Run the `purge_old_consents` command periodically (e.g. via cron or Celery beat) to delete
consent records older than the configured retention period:

```bash
# Delete records older than 3 years (default)
python manage.py purge_old_consents

# Preview without deleting
python manage.py purge_old_consents --dry-run

# Custom retention period
python manage.py purge_old_consents --days=730
```

> **Privacy Policy Note:** The `UserConsent` model stores the browser's User-Agent string alongside
> the hashed IP address for audit trail purposes. No user account or raw IP is ever stored.
> Mention this in your privacy policy.

## Further Reading

- [**TESTING.md**](TESTING.md) – Test coverage report (116 tests, 93% coverage)
- [**idea/**](idea/) – Planned features and ideas
  - [Plain Django support](idea/plain-django-support.md) – Making Django CMS optional
- [**CHANGELOG.md**](CHANGELOG.md) – Version history

## License

MIT License – see [LICENSE](LICENSE) for details.
