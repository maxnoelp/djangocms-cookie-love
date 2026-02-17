"""URL configuration for cookie consent."""

from django.urls import path

from . import views

app_name = "cookie_love"

urlpatterns = [
    path("api/config/", views.config_view, name="api_config"),
    path("api/consent/", views.consent_view, name="api_consent"),
    path("api/consent/revoke/", views.revoke_view, name="api_revoke"),
]
