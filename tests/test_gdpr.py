"""GDPR compliance tests."""

import pytest
from django.core.exceptions import ValidationError

from djangocms_cookie_love.models import (
    ConsentVersion,
    Cookie,
    CookieGroup,
)
from djangocms_cookie_love.utils import hash_ip


class TestGDPRCompliance:
    def test_no_optional_cookies_preselected(self, analytics_group):
        """GDPR: Optional cookie groups must NOT be pre-selected."""
        assert analytics_group.is_default_enabled is False

    def test_required_group_can_be_default_enabled(self, essential_group):
        """Required groups (essential) may be enabled by default."""
        assert essential_group.is_required is True
        assert essential_group.is_default_enabled is True

    def test_optional_group_cannot_be_default_enabled(self, config):
        """GDPR: Optional group with is_default_enabled=True is invalid."""
        group = CookieGroup(
            config=config,
            name="Marketing",
            slug="marketing",
            description="Marketing cookies",
            is_required=False,
            is_default_enabled=True,
        )
        with pytest.raises(ValidationError):
            group.clean()

    def test_ip_is_hashed(self, consent):
        """GDPR: IP addresses must be stored as hashes, not plain text."""
        assert len(consent.ip_hash) == 64  # SHA-256 hex
        assert "." not in consent.ip_hash  # Not a plain IP
        assert consent.ip_hash == hash_ip("127.0.0.1")

    def test_version_change_forces_reconsent(self, consent, config):
        """GDPR: Users must re-consent when cookie usage changes."""
        assert consent.is_valid() is True
        ConsentVersion.objects.create(
            config=config,
            version="2.0",
            change_description="Added tracking cookies",
            requires_reconsent=True,
            snapshot=config.create_snapshot(),
        )
        assert consent.is_valid() is False

    def test_version_minor_update_no_reconsent(self, consent, config):
        """Minor updates without requires_reconsent don't invalidate consent."""
        ConsentVersion.objects.create(
            config=config,
            version="1.1",
            change_description="Text fix",
            requires_reconsent=False,
            snapshot=config.create_snapshot(),
        )
        assert consent.is_valid() is True

    def test_privacy_links_present(self, config):
        """GDPR: Config supports privacy policy and imprint URLs."""
        assert config.get_privacy_policy_link() != ""
        assert config.get_imprint_link() != ""

    def test_granular_control(self, essential_group, analytics_group):
        """GDPR: Users can control consent per cookie group."""
        assert essential_group.slug != analytics_group.slug
        assert essential_group.is_required is True
        assert analytics_group.is_required is False

    def test_consent_audit_trail(self, consent):
        """GDPR: Consent must be documented (audit trail)."""
        assert consent.consent_id is not None
        assert consent.consent_given_at is not None
        assert consent.consent_method == "banner_accept_all"
        assert consent.ip_hash != ""
        assert consent.user_agent != ""
        assert consent.accepted_groups.count() >= 1

    def test_consent_snapshot_captures_state(self, version):
        """GDPR: Version snapshot captures the exact state at time of consent."""
        assert "title" in version.snapshot
        assert "cookie_groups" in version.snapshot
        assert len(version.snapshot["cookie_groups"]) > 0

    def test_reject_option_available(self, config):
        """GDPR: Reject button must be available."""
        assert config.reject_all_label != ""

    def test_cookie_details_available(self, essential_group):
        """GDPR: Cookie details (name, purpose, duration) must be visible."""
        assert len(essential_group.cookies) > 0
        cookie = essential_group.cookies[0]
        assert "name" in cookie
        assert "purpose" in cookie
        assert "duration" in cookie

    def test_required_cookie_cannot_be_optional_in_required_group(self, essential_group):
        """GDPR: Cookies in required groups must be required."""
        cookie = Cookie(
            group=essential_group,
            name="test",
            slug="test",
            is_required=False,
        )
        with pytest.raises(ValidationError):
            cookie.clean()

    def test_optional_cookie_not_preselected(self, analytics_cookies):
        """GDPR: Optional cookies must not be pre-selected."""
        for cookie in analytics_cookies:
            assert cookie.is_required is False

    def test_individual_cookie_consent_tracked(self, consent, analytics_cookies):
        """GDPR: Individual cookie consent decisions are recorded."""
        consent.accepted_cookies.set([analytics_cookies[0]])
        slugs = consent.get_accepted_cookie_slugs()
        assert "analytics:ga" in slugs
        assert "analytics:gid" not in slugs
