from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DjangoCmsCookieLoveConfig(AppConfig):
    name = "djangocms_cookie_love"
    default_auto_field = "django.db.models.BigAutoField"
    verbose_name = _("Cookie Love – Cookie Consent")
