# djangocms-cookie-love – Project Overview

## Vision

A Django CMS package for GDPR-compliant cookie consent banners that is easy to use, fully versionable, and customizable through an admin edit interface. Ships with a Bootstrap 5-based default design.

## Key Features

- **GDPR-compliant** opt-in cookie consent with granular category control
- **Versioning** – track changes to cookie policies and force re-consent when needed
- **Admin edit page** – configure banner text, cookie groups, and design through Django Admin
- **Bootstrap 5 default design** – responsive, accessible, easily overridable
- **Django CMS Plugin + Template Tag** – flexible integration options
- **Consent logging** – documented proof of user consent with hashed IPs
- **Vanilla JS** – no jQuery dependency, lightweight
- **Revocable consent** – users can change their preferences at any time
- **Internationalization (i18n)** – ships with German and English translations

## Project Structure

```
djangocms-cookie-love/
├── plan/                              # Planning documents
│   ├── overview.md                    # This file
│   ├── step-01-project-scaffolding.md
│   ├── step-02-django-app-skeleton.md
│   ├── step-03-data-models.md
│   ├── step-04-gdpr-compliance.md
│   ├── step-05-cms-plugin.md
│   ├── step-06-admin-edit-page.md
│   ├── step-07-views-api.md
│   ├── step-08-frontend.md
│   ├── step-09-middleware.md
│   ├── step-10-tests.md
│   └── step-11-internationalization.md
├── djangocms_cookie_love/             # Main Python package
│   ├── __init__.py
│   ├── apps.py                        # Django AppConfig
│   ├── models.py                      # Data models
│   ├── admin.py                       # Admin interface
│   ├── cms_plugins.py                 # Django CMS plugin registration
│   ├── views.py                       # API endpoints
│   ├── urls.py                        # URL routing
│   ├── forms.py                       # Forms for edit page
│   ├── middleware.py                  # Consent-checking middleware
│   ├── utils.py                       # Helper functions
│   ├── constants.py                   # Cookie categories, defaults
│   ├── templatetags/
│   │   └── cookie_love_tags.py        # Template tags
│   ├── locale/                        # Translations
│   │   ├── en/LC_MESSAGES/            # English
│   │   └── de/LC_MESSAGES/            # German
│   ├── migrations/
│   │   └── 0001_initial.py
│   ├── templates/
│   │   └── djangocms_cookie_love/
│   │       ├── banner.html
│   │       ├── settings_modal.html
│   │       ├── edit_form.html
│   │       └── includes/
│   │           ├── cookie_group.html
│   │           └── toggle_switch.html
│   └── static/
│       └── djangocms_cookie_love/
│           ├── css/
│           │   └── cookie-love.css
│           └── js/
│               └── cookie-love.js
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_models.py
│   ├── test_views.py
│   ├── test_plugins.py
│   └── test_middleware.py
├── pyproject.toml
├── setup.cfg
├── MANIFEST.in
├── README.md
├── LICENSE
├── CHANGELOG.md
└── .gitignore
```

## Tech Stack

| Component      | Technology                     |
| -------------- | ------------------------------ |
| Backend        | Python ≥3.10, Django ≥4.2      |
| CMS            | django-cms ≥4.0                |
| Frontend       | Bootstrap 5, Vanilla JS        |
| Build System   | PEP 621 (pyproject.toml)       |
| Testing        | pytest + pytest-django         |
| i18n           | Django i18n (gettext), de + en |
| Package Format | pip-installable Python package |

## Architecture Decisions

| Decision                     | Rationale                                     |
| ---------------------------- | --------------------------------------------- |
| PEP 621 (`pyproject.toml`)   | Modern Python packaging standard              |
| Vanilla JS (no jQuery)       | No additional dependency, lightweight         |
| Bootstrap 5 default design   | Widely used in Django CMS projects            |
| Singleton pattern for config | Only one active consent config per site       |
| JSONField for cookie details | Pragmatic, less model complexity              |
| IP hashing                   | GDPR-compliant consent documentation          |
| Template Tag + CMS Plugin    | Two integration paths for maximum flexibility |

## Steps

1. **Project Scaffolding** – pyproject.toml, .gitignore, README, LICENSE
2. **Django App Skeleton** – apps.py, **init**.py
3. **Data Models** – CookieConsentConfig, CookieGroup, ConsentVersion, UserConsent
4. **GDPR Compliance** – Opt-in, granular control, revocation, documentation
5. **CMS Plugin** – Django CMS plugin + template tag
6. **Admin / Edit Page** – Django Admin with inlines + optional frontend edit view
7. **Views & API** – REST endpoints for consent CRUD
8. **Frontend** – Bootstrap templates, CSS, Vanilla JS
9. **Middleware** – CookieConsentMiddleware
10. **Tests** – Full test suite
11. **Internationalization** – German and English translations (i18n)
