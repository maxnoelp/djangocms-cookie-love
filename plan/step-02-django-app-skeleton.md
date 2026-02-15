# Step 02 – Django App Skeleton

## Goal

Create the basic Django app structure with proper AppConfig and package initialization.

## Tasks

### 2.1 Create `djangocms_cookie_love/__init__.py`

```python
__version__ = "0.1.0"
default_app_config = "djangocms_cookie_love.apps.DjangoCmsCookieLoveConfig"
```

### 2.2 Create `djangocms_cookie_love/apps.py`

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoCmsCookieLoveConfig(AppConfig):
    name = "djangocms_cookie_love"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("Cookie Love – Cookie Consent")
```

### 2.3 Create Empty Module Files

Stub files with docstrings:

- `models.py` – "Cookie consent data models"
- `admin.py` – "Admin configuration for cookie consent"
- `views.py` – "API views for cookie consent"
- `urls.py` – "URL configuration"
- `forms.py` – "Forms for cookie consent editing"
- `cms_plugins.py` – "Django CMS plugin definitions"
- `middleware.py` – "Cookie consent middleware"
- `utils.py` – "Utility functions"
- `constants.py` – "Constants and default values"

### 2.4 Create `djangocms_cookie_love/templatetags/__init__.py`

Empty init for templatetags package.

### 2.5 Create `djangocms_cookie_love/templatetags/cookie_love_tags.py`

Stub template tag library:

```python
from django import template

register = template.Library()
```

### 2.6 Create Directory Structure

```
djangocms_cookie_love/
├── locale/
│   ├── en/
│   │   └── LC_MESSAGES/
│   └── de/
│       └── LC_MESSAGES/
├── migrations/
│   └── __init__.py
├── templates/
│   └── djangocms_cookie_love/
│       └── includes/
├── static/
│   └── djangocms_cookie_love/
│       ├── css/
│       └── js/
└── templatetags/
    └── __init__.py
```

## Verification

- [ ] `python -c "import djangocms_cookie_love"` works
- [ ] `python -c "from djangocms_cookie_love.apps import DjangoCmsCookieLoveConfig"` works
- [ ] All stub modules are importable
- [ ] App can be added to `INSTALLED_APPS` without errors
