from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CookieLoveCmsConfig(AppConfig):
    name = "djangocms_cookie_love.contrib.cms"
    label = "djangocms_cookie_love_cms"
    verbose_name = _("Cookie Love – django CMS integration")
