"""Tests for CookieConsentMiddleware."""

import pytest
from django.test import RequestFactory

from djangocms_cookie_love.middleware import CookieConsentMiddleware
from djangocms_cookie_love.models import (
    ConsentVersion,
)


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def middleware():
    return CookieConsentMiddleware(lambda request: request)


class TestCookieConsentMiddleware:
    def test_no_consent_cookie(self, rf, middleware, config):
        request = rf.get("/")
        middleware(request)
        assert request.cookie_consent is None
        assert request.cookie_consent_required is True
        assert request.cookie_consent_groups == []
        assert request.cookie_consent_cookies == []

    def test_valid_consent(self, rf, middleware, consent):
        request = rf.get("/")
        request.COOKIES["cookie_love_consent"] = str(consent.consent_id)
        middleware(request)
        assert request.cookie_consent == consent
        assert request.cookie_consent_required is False
        assert set(request.cookie_consent_groups) == {"essential", "analytics"}

    def test_invalid_consent_id(self, rf, middleware, config):
        request = rf.get("/")
        request.COOKIES["cookie_love_consent"] = "invalid-uuid"
        middleware(request)
        assert request.cookie_consent is None
        assert request.cookie_consent_required is True

    def test_nonexistent_consent_id(self, rf, middleware, config):
        request = rf.get("/")
        request.COOKIES["cookie_love_consent"] = "00000000-0000-0000-0000-000000000000"
        middleware(request)
        assert request.cookie_consent is None
        assert request.cookie_consent_required is True

    def test_outdated_version_requires_reconsent(self, rf, middleware, consent, config):
        ConsentVersion.objects.create(
            config=config,
            version="2.0",
            change_description="Major update",
            requires_reconsent=True,
            snapshot=config.create_snapshot(),
        )
        request = rf.get("/")
        request.COOKIES["cookie_love_consent"] = str(consent.consent_id)
        middleware(request)
        assert request.cookie_consent is None
        assert request.cookie_consent_required is True

    def test_outdated_version_no_reconsent(self, rf, middleware, consent, config):
        ConsentVersion.objects.create(
            config=config,
            version="2.0",
            change_description="Minor update",
            requires_reconsent=False,
            snapshot=config.create_snapshot(),
        )
        request = rf.get("/")
        request.COOKIES["cookie_love_consent"] = str(consent.consent_id)
        middleware(request)
        assert request.cookie_consent == consent
        assert request.cookie_consent_required is False

    def test_consent_groups_populated(self, rf, middleware, consent):
        request = rf.get("/")
        request.COOKIES["cookie_love_consent"] = str(consent.consent_id)
        middleware(request)
        assert "essential" in request.cookie_consent_groups
        assert "analytics" in request.cookie_consent_groups

    def test_consent_cookies_populated(self, rf, middleware, consent, essential_cookies, analytics_cookies):
        consent.accepted_cookies.set(essential_cookies + analytics_cookies)
        request = rf.get("/")
        request.COOKIES["cookie_love_consent"] = str(consent.consent_id)
        middleware(request)
        assert "analytics:ga" in request.cookie_consent_cookies
        assert "essential:sessionid" in request.cookie_consent_cookies
