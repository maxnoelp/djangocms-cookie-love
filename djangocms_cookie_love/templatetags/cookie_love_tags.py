"""Template tags for cookie consent banner integration."""

from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from djangocms_cookie_love.models import CookieConsentConfig

register = template.Library()


@register.inclusion_tag("djangocms_cookie_love/banner.html", takes_context=True)
def cookie_love_banner(context):
    """
    Render the cookie consent banner.

    Usage::

        {% load cookie_love_tags %}
        {% cookie_love_banner %}
    """
    config = CookieConsentConfig.get_active()
    if config:
        context.update(
            {
                "cookie_config": config,
                "cookie_groups": config.cookie_groups.all().order_by("order"),
                "current_version": config.get_current_version(),
            }
        )
    return context


@register.simple_tag
def cookie_love_css():
    """
    Output the <link> tag for cookie-love.css.

    Usage::

        {% load cookie_love_tags %}
        {% cookie_love_css %}
    """
    url = static("djangocms_cookie_love/css/cookie-love.css")
    return mark_safe(f'<link rel="stylesheet" href="{url}">')


@register.simple_tag
def cookie_love_js():
    """
    Output the <script> tag for cookie-love.js.

    Usage::

        {% load cookie_love_tags %}
        {% cookie_love_js %}
    """
    url = static("djangocms_cookie_love/js/cookie-love.js")
    return mark_safe(f'<script src="{url}" defer></script>')
