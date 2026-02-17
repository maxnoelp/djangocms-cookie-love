"""Django CMS plugin definitions."""

from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from django.utils.translation import gettext_lazy as _

from .models import CookieConsentConfig


@plugin_pool.register_plugin
class CookieConsentPlugin(CMSPluginBase):
    """Renders the cookie consent banner on any CMS page."""

    name = _("Cookie Consent Banner")
    module = _("Cookie Love")
    render_template = "djangocms_cookie_love/banner.html"
    cache = False  # Must not be cached – consent is per-user
    allow_children = False

    # No additional model needed – uses singleton CookieConsentConfig

    def render(self, context, instance, placeholder):
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
