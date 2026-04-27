"""Shared test fixtures."""

import pytest

from djangocms_cookie_love.models import (
    ConsentVersion,
    Cookie,
    CookieConsentConfig,
    CookieGroup,
    UserConsent,
)
from djangocms_cookie_love.utils import hash_ip


@pytest.fixture
def config(db):
    """Active cookie consent configuration."""
    return CookieConsentConfig.objects.create(
        title="Test Cookie Banner",
        description="We use cookies for testing.",
        privacy_policy_url="https://example.com/privacy",
        imprint_url="https://example.com/imprint",
        is_active=True,
    )


@pytest.fixture
def essential_group(config):
    """Required cookie group."""
    return CookieGroup.objects.create(
        config=config,
        name="Essential",
        slug="essential",
        description="Essential cookies",
        is_required=True,
        is_default_enabled=True,
        order=0,
        cookies=[
            {
                "name": "sessionid",
                "provider": "This website",
                "duration": "Session",
                "purpose": "Session management",
            }
        ],
    )


@pytest.fixture
def analytics_group(config):
    """Optional analytics cookie group."""
    return CookieGroup.objects.create(
        config=config,
        name="Analytics",
        slug="analytics",
        description="Analytics cookies",
        is_required=False,
        is_default_enabled=False,
        order=1,
        cookies=[
            {
                "name": "_ga",
                "provider": "Google",
                "duration": "2 years",
                "purpose": "Distinguish users",
            }
        ],
    )


@pytest.fixture
def essential_cookies(essential_group):
    """Cookie objects for the essential group."""
    return [
        Cookie.objects.create(
            group=essential_group,
            name="sessionid",
            slug="sessionid",
            provider="This website",
            duration="Session",
            purpose="Session management",
            is_required=True,
            order=0,
        ),
    ]


@pytest.fixture
def analytics_cookies(analytics_group):
    """Cookie objects for the analytics group."""
    return [
        Cookie.objects.create(
            group=analytics_group,
            name="_ga",
            slug="ga",
            provider="Google",
            duration="2 years",
            purpose="Distinguish users",
            is_required=False,
            order=0,
        ),
        Cookie.objects.create(
            group=analytics_group,
            name="_gid",
            slug="gid",
            provider="Google",
            duration="24 hours",
            purpose="Distinguish users",
            is_required=False,
            order=1,
        ),
    ]


@pytest.fixture
def version(config, essential_group, analytics_group):
    """Published consent version with snapshot.

    ``CookieConsentConfig.save()`` auto-creates a 1.0 version on first save,
    so we fetch it here and refresh the snapshot now that the groups exist.
    """
    v = ConsentVersion.objects.get(config=config, version="1.0")
    v.snapshot = config.create_snapshot()
    v.save(update_fields=["snapshot"])
    return v


@pytest.fixture
def consent(version, essential_group, analytics_group):
    """User consent with all groups accepted."""
    c = UserConsent.objects.create(
        version=version,
        ip_hash=hash_ip("127.0.0.1"),
        user_agent="TestAgent/1.0",
        consent_method="banner_accept_all",
    )
    c.accepted_groups.set([essential_group, analytics_group])
    return c
