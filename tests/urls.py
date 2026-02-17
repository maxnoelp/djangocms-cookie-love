"""URL configuration for tests."""

from django.urls import include, path

urlpatterns = [
    path("cookie-love/", include("djangocms_cookie_love.urls")),
]
