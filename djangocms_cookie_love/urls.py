"""URL configuration for cookie consent."""

from django.urls import path

from . import views

app_name = "cookie_love"

urlpatterns = [
    path("config/", views.config_view, name="api_config"),
    path("consent/", views.consent_view, name="api_consent"),
    path("consent/revoke/", views.revoke_view, name="api_revoke"),
]
