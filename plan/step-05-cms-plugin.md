# Step 05 – Django CMS Plugin

## Goal

Register a Django CMS plugin that renders the cookie consent banner on any CMS page. Additionally, provide a template tag for non-CMS pages or base template integration.

## Tasks

### 5.1 CMS Plugin Model

```python
# cms_plugins.py
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from .models import CookieConsentConfig


@plugin_pool.register_plugin
class CookieConsentPlugin(CMSPluginBase):
    name = _("Cookie Consent Banner")
    module = _("Cookie Love")
    render_template = "djangocms_cookie_love/banner.html"
    cache = False  # Must not be cached (consent is per-user)
    allow_children = False

    # No additional model needed – uses singleton CookieConsentConfig

    def render(self, context, instance, placeholder):
        config = CookieConsentConfig.get_active()
        if config:
            context.update({
                "cookie_config": config,
                "cookie_groups": config.cookie_groups.all().order_by("order"),
                "current_version": config.get_current_version(),
            })
        return context
```

**Notes:**

- Plugin uses the singleton `CookieConsentConfig` (no separate plugin model needed)
- `cache = False` because consent state varies per user
- Plugin can be placed in any placeholder (typically in a base template placeholder)

### 5.2 Template Tag (Alternative Integration)

For projects that prefer base template integration over CMS plugins:

```python
# templatetags/cookie_love_tags.py
from django import template
from django.template.loader import render_to_string

from djangocms_cookie_love.models import CookieConsentConfig

register = template.Library()


@register.inclusion_tag("djangocms_cookie_love/banner.html", takes_context=True)
def cookie_love_banner(context):
    config = CookieConsentConfig.get_active()
    if config:
        context.update({
            "cookie_config": config,
            "cookie_groups": config.cookie_groups.all().order_by("order"),
            "current_version": config.get_current_version(),
        })
    return context


@register.simple_tag
def cookie_love_js():
    """Outputs the <script> tag for cookie-love.js"""
    return mark_safe(
        '<script src="{% static \'djangocms_cookie_love/js/cookie-love.js\' %}" defer></script>'
    )
```

**Usage in templates:**

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

### 5.3 URL Configuration

Include cookie-love URLs in the project:

```python
# urls.py (project level)
urlpatterns = [
    ...
    path("cookie-love/", include("djangocms_cookie_love.urls")),
    ...
]
```

## Verification

- [ ] Plugin appears in Django CMS plugin list under "Cookie Love" module
- [ ] Plugin renders banner correctly on CMS page
- [ ] Template tag works as alternative to CMS plugin
- [ ] Banner loads current config and cookie groups
- [ ] Plugin is not cached
- [ ] Works with Django CMS 4.x
