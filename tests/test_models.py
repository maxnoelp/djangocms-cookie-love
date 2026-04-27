"""Tests for cookie consent data models."""

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from djangocms_cookie_love.models import (
    ConsentVersion,
    Cookie,
    CookieConsentConfig,
    CookieGroup,
    UserConsent,
)
from djangocms_cookie_love.utils import hash_ip

# ---------------------------------------------------------------------------
# CookieConsentConfig
# ---------------------------------------------------------------------------


class TestCookieConsentConfig:
    def test_create_config(self, config):
        assert config.pk is not None
        assert config.title == "Test Cookie Banner"
        assert config.is_active is True

    def test_str(self, config):
        assert str(config) == "Test Cookie Banner"

    def test_singleton_enforcement(self, config):
        """When a new active config is saved the old one is deactivated."""
        config2 = CookieConsentConfig.objects.create(title="Second Config", is_active=True)
        config.refresh_from_db()
        assert config.is_active is False
        assert config2.is_active is True

    def test_get_active(self, config):
        assert CookieConsentConfig.get_active() == config

    def test_get_active_returns_none_when_inactive(self, config):
        config.is_active = False
        config.save()
        assert CookieConsentConfig.get_active() is None

    def test_create_snapshot(self, config, essential_group, analytics_group):
        snapshot = config.create_snapshot()
        assert snapshot["title"] == "Test Cookie Banner"
        assert len(snapshot["cookie_groups"]) == 2
        assert snapshot["cookie_groups"][0]["slug"] == "essential"

    def test_get_current_version_none(self, config):
        # CookieConsentConfig.save() auto-creates a 1.0 version; remove it
        # to exercise the no-versions code path.
        config.versions.all().delete()
        assert config.get_current_version() is None

    def test_get_current_version(self, config, version):
        assert config.get_current_version() == version


# ---------------------------------------------------------------------------
# CookieGroup
# ---------------------------------------------------------------------------


class TestCookieGroup:
    def test_create_group(self, essential_group):
        assert essential_group.pk is not None
        assert essential_group.name == "Essential"
        assert essential_group.is_required is True

    def test_str(self, essential_group):
        assert str(essential_group) == "Essential"

    def test_ordering(self, essential_group, analytics_group):
        groups = list(CookieGroup.objects.filter(config=essential_group.config).order_by("order"))
        assert groups[0] == essential_group
        assert groups[1] == analytics_group

    def test_cookies_json_field(self, essential_group):
        assert isinstance(essential_group.cookies, list)
        assert essential_group.cookies[0]["name"] == "sessionid"

    def test_optional_cannot_be_default_enabled(self, config):
        group = CookieGroup(
            config=config,
            name="Bad",
            slug="bad",
            description="Bad group",
            is_required=False,
            is_default_enabled=True,
        )
        with pytest.raises(ValidationError):
            group.clean()

    def test_required_can_be_default_enabled(self, config):
        group = CookieGroup(
            config=config,
            name="Good",
            slug="good",
            description="Good group",
            is_required=True,
            is_default_enabled=True,
        )
        group.clean()  # Should not raise


# ---------------------------------------------------------------------------
# ConsentVersion
# ---------------------------------------------------------------------------


class TestConsentVersion:
    def test_create_version(self, version):
        assert version.pk is not None
        assert version.version == "1.0"

    def test_str(self, version):
        assert "1.0" in str(version)

    def test_snapshot_content(self, version):
        assert "title" in version.snapshot
        assert "cookie_groups" in version.snapshot

    def test_get_current(self, config, version):
        assert ConsentVersion.get_current() == version

    def test_get_current_none(self, db):
        assert ConsentVersion.get_current() is None

    def test_requires_reconsent_flag(self, config, version):
        v2 = ConsentVersion.objects.create(
            config=config,
            version="2.0",
            change_description="Update",
            requires_reconsent=True,
            snapshot=config.create_snapshot(),
        )
        assert v2.requires_reconsent is True


# ---------------------------------------------------------------------------
# UserConsent
# ---------------------------------------------------------------------------


class TestUserConsent:
    def test_create_consent(self, consent):
        assert consent.pk is not None
        assert consent.consent_id is not None

    def test_str(self, consent):
        assert str(consent.consent_id)[:8] in str(consent)

    def test_consent_id_is_uuid(self, consent):
        import uuid

        assert isinstance(consent.consent_id, uuid.UUID)

    def test_accepted_groups(self, consent):
        slugs = set(consent.accepted_groups.values_list("slug", flat=True))
        assert slugs == {"essential", "analytics"}

    def test_ip_hash_stored(self, consent):
        assert len(consent.ip_hash) == 64
        assert consent.ip_hash == hash_ip("127.0.0.1")

    def test_is_valid_current_version(self, consent):
        assert consent.is_valid() is True

    def test_is_valid_outdated_version(self, consent, config):
        ConsentVersion.objects.create(
            config=config,
            version="2.0",
            change_description="New v2",
            requires_reconsent=True,
            snapshot=config.create_snapshot(),
        )
        assert consent.is_valid() is False

    def test_is_valid_no_reconsent_needed(self, consent, config):
        ConsentVersion.objects.create(
            config=config,
            version="2.0",
            change_description="Minor update",
            requires_reconsent=False,
            snapshot=config.create_snapshot(),
        )
        assert consent.is_valid() is True

    def test_get_by_consent_id(self, consent):
        found = UserConsent.get_by_consent_id(str(consent.consent_id))
        assert found == consent

    def test_get_by_consent_id_invalid(self):
        assert UserConsent.get_by_consent_id("invalid-uuid") is None

    def test_get_by_consent_id_nonexistent(self, db):
        assert UserConsent.get_by_consent_id("00000000-0000-0000-0000-000000000000") is None


# ---------------------------------------------------------------------------
# Cookie
# ---------------------------------------------------------------------------


class TestCookie:
    def test_create_cookie(self, analytics_cookies):
        cookie = analytics_cookies[0]
        assert cookie.pk is not None
        assert cookie.name == "_ga"
        assert cookie.slug == "ga"

    def test_str(self, analytics_cookies):
        cookie = analytics_cookies[0]
        assert "_ga" in str(cookie)
        assert "Analytics" in str(cookie)

    def test_unique_together(self, analytics_group, analytics_cookies):
        """slug must be unique within the group."""
        with pytest.raises(IntegrityError):
            Cookie.objects.create(
                group=analytics_group,
                name="duplicate",
                slug="ga",
                order=99,
            )

    def test_required_cookie_in_required_group(self, essential_cookies):
        cookie = essential_cookies[0]
        assert cookie.is_required is True

    def test_optional_cookie_in_required_group_fails(self, essential_group):
        cookie = Cookie(
            group=essential_group,
            name="test",
            slug="test",
            is_required=False,
        )
        with pytest.raises(ValidationError):
            cookie.clean()

    def test_optional_cookie_in_optional_group(self, analytics_group):
        cookie = Cookie(
            group=analytics_group,
            name="test",
            slug="test",
            is_required=False,
        )
        cookie.clean()  # Should not raise

    def test_ordering(self, analytics_cookies):
        cookies = list(Cookie.objects.filter(group=analytics_cookies[0].group).order_by("order", "name"))
        assert cookies[0].slug == "ga"
        assert cookies[1].slug == "gid"

    def test_cookie_group_relation(self, analytics_cookies, analytics_group):
        assert analytics_group.cookie_items.count() == 2

    def test_cookie_fields(self, analytics_cookies):
        cookie = analytics_cookies[0]
        assert cookie.provider == "Google"
        assert cookie.duration == "2 years"
        assert cookie.purpose == "Distinguish users"


# ---------------------------------------------------------------------------
# UserConsent – Cookie level
# ---------------------------------------------------------------------------


class TestUserConsentCookies:
    def test_accepted_cookies_m2m(self, consent, analytics_cookies, essential_cookies):
        """Can set accepted cookies on consent."""
        all_cookies = analytics_cookies + essential_cookies
        consent.accepted_cookies.set(all_cookies)
        assert consent.accepted_cookies.count() == 3

    def test_get_accepted_cookie_slugs(self, consent, analytics_cookies, essential_cookies):
        all_cookies = analytics_cookies + essential_cookies
        consent.accepted_cookies.set(all_cookies)
        slugs = consent.get_accepted_cookie_slugs()
        assert "analytics:ga" in slugs
        assert "analytics:gid" in slugs
        assert "essential:sessionid" in slugs

    def test_is_cookie_accepted_with_group_prefix(self, consent, analytics_cookies):
        consent.accepted_cookies.set(analytics_cookies)
        assert consent.is_cookie_accepted("analytics:ga") is True
        assert consent.is_cookie_accepted("analytics:gid") is True
        assert consent.is_cookie_accepted("essential:sessionid") is False

    def test_is_cookie_accepted_without_prefix(self, consent, analytics_cookies):
        consent.accepted_cookies.set(analytics_cookies)
        assert consent.is_cookie_accepted("ga") is True
        assert consent.is_cookie_accepted("nonexistent") is False

    def test_snapshot_includes_cookie_items(
        self, config, essential_group, analytics_group, essential_cookies, analytics_cookies
    ):
        snapshot = config.create_snapshot()
        analytics_data = next(g for g in snapshot["cookie_groups"] if g["slug"] == "analytics")
        cookie_slugs = [c["slug"] for c in analytics_data["cookies"]]
        assert "ga" in cookie_slugs
        assert "gid" in cookie_slugs
