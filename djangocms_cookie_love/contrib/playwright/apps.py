from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CookieLovePlaywrightConfig(AppConfig):
    name = "djangocms_cookie_love.contrib.playwright"
    label = "djangocms_cookie_love_playwright"
    verbose_name = _("Cookie Love – Playwright crawler")
