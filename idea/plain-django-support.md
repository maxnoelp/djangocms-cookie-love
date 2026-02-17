# Idea: Support Plain Django (without Django CMS)

## Current State

The package is named `djangocms-cookie-love` and lists `django-cms>=4.0` as a
dependency. However, **only one file** (`cms_plugins.py`) actually imports from
Django CMS. Everything else — models, admin, views, middleware, templates, JS,
CSS, template tags — is pure Django.

## Goal

Make Django CMS optional so the package works in any Django project. Users
without CMS still get the full cookie consent functionality via template tags.

## What Needs to Change

### 1. Make `cms_plugins.py` safe without CMS

```python
try:
    from cms.plugin_base import CMSPluginBase
    from cms.plugin_pool import plugin_pool
    HAS_CMS = True
except ImportError:
    HAS_CMS = False

if HAS_CMS:
    class CookieConsentPlugin(CMSPluginBase):
        ...
    plugin_pool.register_plugin(CookieConsentPlugin)
```

### 2. Make `django-cms` an optional dependency in `pyproject.toml`

```toml
dependencies = [
    "django>=4.2",
]

[project.optional-dependencies]
cms = [
    "django-cms>=4.0",
]
dev = [
    "pytest",
    "pytest-django",
    "pytest-cov",
    "ruff",
    "pre-commit",
    "django-cms>=4.0",
]
```

- `pip install djangocms-cookie-love` → works in plain Django
- `pip install djangocms-cookie-love[cms]` → includes Django CMS support

### 3. Usage in plain Django (without CMS)

In `base.html`:

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

This already works today — the template tags don't depend on CMS.

### 4. Consider renaming the package (future)

`djangocms-cookie-love` implies CMS-only. A future rename to `django-cookie-love`
could make the broader audience clearer. This would be a breaking change and
should only happen at a major version bump.

## Impact

- No breaking changes for existing CMS users
- Opens the package to the much larger plain Django audience
- Minimal code changes (1 file + `pyproject.toml`)
