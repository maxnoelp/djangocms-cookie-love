"""Tests for context processors."""

import pytest
from django.test import RequestFactory

from djangocms_cookie_love.context_processors import cookie_consent


@pytest.fixture
def rf():
    return RequestFactory()


class TestCookieConsentContextProcessor:
    """Test the cookie_consent context processor."""

    def test_with_no_attributes(self, rf):
        """Returns defaults when middleware hasn't set attributes."""
        request = rf.get("/")
        ctx = cookie_consent(request)
        assert ctx["cookie_consent"] is None
        assert ctx["cookie_consent_required"] is True
        assert ctx["cookie_consent_groups"] == []
        assert ctx["cookie_consent_cookies"] == []

    def test_with_middleware_attributes(self, rf):
        """Returns values set by middleware on request."""
        request = rf.get("/")
        request.cookie_consent = "mock_consent"
        request.cookie_consent_required = False
        request.cookie_consent_groups = ["essential", "analytics"]
        request.cookie_consent_cookies = ["essential:sessionid", "analytics:ga"]
        ctx = cookie_consent(request)
        assert ctx["cookie_consent"] == "mock_consent"
        assert ctx["cookie_consent_required"] is False
        assert ctx["cookie_consent_groups"] == ["essential", "analytics"]
        assert ctx["cookie_consent_cookies"] == ["essential:sessionid", "analytics:ga"]
