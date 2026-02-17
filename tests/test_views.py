"""Tests for API views."""

import json

import pytest
from django.test import Client

from djangocms_cookie_love.models import (
    ConsentVersion,
    UserConsent,
)


@pytest.fixture
def api_client():
    return Client(enforce_csrf_checks=False)


# ---------------------------------------------------------------------------
# GET /cookie-love/api/config/
# ---------------------------------------------------------------------------


class TestConfigAPI:
    def test_get_config(self, api_client, config, essential_group, version):
        resp = api_client.get("/cookie-love/api/config/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Test Cookie Banner"
        assert data["version"] == "1.0"

    def test_get_config_no_active(self, api_client, db):
        resp = api_client.get("/cookie-love/api/config/")
        assert resp.status_code == 404

    def test_config_includes_groups(self, api_client, config, essential_group, analytics_group, version):
        resp = api_client.get("/cookie-love/api/config/")
        data = resp.json()
        slugs = [g["slug"] for g in data["cookie_groups"]]
        assert "essential" in slugs
        assert "analytics" in slugs

    def test_config_includes_buttons(self, api_client, config, version):
        resp = api_client.get("/cookie-love/api/config/")
        data = resp.json()
        assert "accept_all" in data["buttons"]
        assert "reject_all" in data["buttons"]
        assert "settings" in data["buttons"]
        assert "save" in data["buttons"]

    def test_method_not_allowed(self, api_client, config):
        resp = api_client.post("/cookie-love/api/config/")
        assert resp.status_code == 405


# ---------------------------------------------------------------------------
# POST /cookie-love/api/consent/
# ---------------------------------------------------------------------------


class TestConsentAPI:
    def test_post_consent(self, api_client, config, version, essential_group):
        resp = api_client.post(
            "/cookie-love/api/consent/",
            data=json.dumps(
                {
                    "accepted_groups": ["essential"],
                    "consent_method": "banner_accept_all",
                }
            ),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "consent_id" in data
        assert "essential" in data["accepted_groups"]

    def test_post_consent_sets_cookie(self, api_client, config, version, essential_group):
        resp = api_client.post(
            "/cookie-love/api/consent/",
            data=json.dumps(
                {
                    "accepted_groups": ["essential"],
                    "consent_method": "banner_accept_all",
                }
            ),
            content_type="application/json",
        )
        assert "cookie_love_consent" in resp.cookies

    def test_post_consent_always_includes_required(self, api_client, config, version, essential_group, analytics_group):
        """Even if user doesn't select required groups they are added."""
        resp = api_client.post(
            "/cookie-love/api/consent/",
            data=json.dumps(
                {
                    "accepted_groups": ["analytics"],
                    "consent_method": "settings",
                }
            ),
            content_type="application/json",
        )
        data = resp.json()
        assert "essential" in data["accepted_groups"]

    def test_invalid_consent_method(self, api_client, config, version, essential_group):
        resp = api_client.post(
            "/cookie-love/api/consent/",
            data=json.dumps(
                {
                    "accepted_groups": ["essential"],
                    "consent_method": "invalid_method",
                }
            ),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_invalid_group_slugs(self, api_client, config, version, essential_group):
        resp = api_client.post(
            "/cookie-love/api/consent/",
            data=json.dumps(
                {
                    "accepted_groups": ["nonexistent"],
                    "consent_method": "settings",
                }
            ),
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_invalid_json(self, api_client, config, version):
        resp = api_client.post(
            "/cookie-love/api/consent/",
            data="not json",
            content_type="application/json",
        )
        assert resp.status_code == 400

    def test_no_active_config(self, api_client, db):
        resp = api_client.post(
            "/cookie-love/api/consent/",
            data=json.dumps(
                {
                    "accepted_groups": ["essential"],
                    "consent_method": "settings",
                }
            ),
            content_type="application/json",
        )
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# GET /cookie-love/api/consent/  (status check)
# ---------------------------------------------------------------------------


class TestConsentStatusAPI:
    def test_no_cookie(self, api_client, db):
        resp = api_client.get("/cookie-love/api/consent/")
        data = resp.json()
        assert data["has_consent"] is False
        assert data["reason"] == "no_consent"

    def test_valid_consent(self, api_client, consent):
        api_client.cookies["cookie_love_consent"] = str(consent.consent_id)
        resp = api_client.get("/cookie-love/api/consent/")
        data = resp.json()
        assert data["has_consent"] is True
        assert data["is_current_version"] is True

    def test_outdated_version(self, api_client, consent, config):
        ConsentVersion.objects.create(
            config=config,
            version="2.0",
            change_description="Update",
            requires_reconsent=True,
            snapshot=config.create_snapshot(),
        )
        api_client.cookies["cookie_love_consent"] = str(consent.consent_id)
        resp = api_client.get("/cookie-love/api/consent/")
        data = resp.json()
        assert data["has_consent"] is True
        assert data["is_current_version"] is False
        assert data["reason"] == "version_outdated"

    def test_invalid_consent_id(self, api_client, db):
        api_client.cookies["cookie_love_consent"] = "invalid"
        resp = api_client.get("/cookie-love/api/consent/")
        data = resp.json()
        assert data["has_consent"] is False


# ---------------------------------------------------------------------------
# POST /cookie-love/api/consent/revoke/
# ---------------------------------------------------------------------------


class TestRevokeAPI:
    def test_revoke_consent(self, api_client, config, version, essential_group, analytics_group):
        resp = api_client.post("/cookie-love/api/consent/revoke/")
        assert resp.status_code == 200
        data = resp.json()
        assert data["accepted_groups"] == ["essential"]
        assert "consent_id" in data

    def test_revoke_sets_cookie(self, api_client, config, version, essential_group):
        resp = api_client.post("/cookie-love/api/consent/revoke/")
        assert "cookie_love_consent" in resp.cookies

    def test_revoke_method_not_allowed(self, api_client, config):
        resp = api_client.get("/cookie-love/api/consent/revoke/")
        assert resp.status_code == 405

    def test_revoke_no_config(self, api_client, db):
        resp = api_client.post("/cookie-love/api/consent/revoke/")
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# Cookie-level consent tests
# ---------------------------------------------------------------------------


class TestCookieLevelConsentAPI:
    def test_config_includes_cookie_objects(
        self,
        api_client,
        config,
        essential_group,
        analytics_group,
        essential_cookies,
        analytics_cookies,
        version,
    ):
        resp = api_client.get("/cookie-love/api/config/")
        data = resp.json()
        analytics_data = next(g for g in data["cookie_groups"] if g["slug"] == "analytics")
        cookie_slugs = [c["slug"] for c in analytics_data["cookies"]]
        assert "ga" in cookie_slugs
        assert "gid" in cookie_slugs

    def test_config_cookie_has_fields(
        self,
        api_client,
        config,
        analytics_group,
        analytics_cookies,
        version,
    ):
        resp = api_client.get("/cookie-love/api/config/")
        data = resp.json()
        analytics_data = next(g for g in data["cookie_groups"] if g["slug"] == "analytics")
        ga = next(c for c in analytics_data["cookies"] if c["slug"] == "ga")
        assert ga["name"] == "_ga"
        assert ga["provider"] == "Google"
        assert ga["duration"] == "2 years"
        assert ga["is_required"] is False

    def test_post_consent_with_individual_cookies(
        self,
        api_client,
        config,
        version,
        essential_group,
        analytics_group,
        essential_cookies,
        analytics_cookies,
    ):
        """Post consent with individual cookie selection."""
        resp = api_client.post(
            "/cookie-love/api/consent/",
            data=json.dumps(
                {
                    "accepted_groups": ["essential"],
                    "accepted_cookies": ["analytics:ga"],
                    "consent_method": "settings",
                }
            ),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "essential" in data["accepted_groups"]
        assert "analytics:ga" in data["accepted_cookies"]
        # _gid was NOT selected
        assert "analytics:gid" not in data["accepted_cookies"]

    def test_post_consent_group_includes_all_cookies(
        self,
        api_client,
        config,
        version,
        essential_group,
        analytics_group,
        essential_cookies,
        analytics_cookies,
    ):
        """Accepting a group includes all its cookies."""
        resp = api_client.post(
            "/cookie-love/api/consent/",
            data=json.dumps(
                {
                    "accepted_groups": ["essential", "analytics"],
                    "accepted_cookies": [],
                    "consent_method": "banner_accept_all",
                }
            ),
            content_type="application/json",
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "analytics:ga" in data["accepted_cookies"]
        assert "analytics:gid" in data["accepted_cookies"]
        assert "essential:sessionid" in data["accepted_cookies"]

    def test_get_consent_includes_accepted_cookies(
        self,
        api_client,
        config,
        version,
        essential_group,
        analytics_group,
        essential_cookies,
        analytics_cookies,
        consent,
    ):
        """GET consent status includes accepted_cookies."""
        consent.accepted_cookies.set(essential_cookies + analytics_cookies)
        api_client.cookies["cookie_love_consent"] = str(consent.consent_id)
        resp = api_client.get("/cookie-love/api/consent/")
        data = resp.json()
        assert "accepted_cookies" in data
        assert "analytics:ga" in data["accepted_cookies"]

    def test_revoke_keeps_only_required_cookies(
        self,
        api_client,
        config,
        version,
        essential_group,
        analytics_group,
        essential_cookies,
        analytics_cookies,
    ):
        """Revoke removes optional cookies, keeps required ones."""
        resp = api_client.post("/cookie-love/api/consent/revoke/")
        data = resp.json()
        # Should have essential cookies
        consent = UserConsent.objects.get(consent_id=data["consent_id"])
        cookie_slugs = consent.get_accepted_cookie_slugs()
        assert "essential:sessionid" in cookie_slugs
        # Should NOT have analytics cookies
        assert "analytics:ga" not in cookie_slugs
