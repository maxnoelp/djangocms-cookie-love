"""Tests for admin functionality."""

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.test import RequestFactory

from djangocms_cookie_love.admin import (
    ConsentVersionAdmin,
    CookieConsentConfigAdmin,
    CookieGroupAdmin,
    UserConsentAdmin,
)
from djangocms_cookie_love.models import (
    ConsentVersion,
    CookieConsentConfig,
    CookieGroup,
    UserConsent,
)


@pytest.fixture
def site():
    return AdminSite()


@pytest.fixture
def rf():
    return RequestFactory()


@pytest.fixture
def superuser(db):
    return User.objects.create_superuser("admin", "admin@test.com", "password")


@pytest.mark.django_db
class TestCookieConsentConfigAdmin:
    """Test singleton enforcement in config admin."""

    def test_has_add_permission_when_none_exists(self, site, rf, superuser):
        """Can add config when none exists."""
        admin = CookieConsentConfigAdmin(CookieConsentConfig, site)
        request = rf.get("/admin/")
        request.user = superuser
        assert admin.has_add_permission(request) is True

    def test_has_add_permission_when_exists(self, site, rf, config, superuser):
        """Cannot add config when one already exists."""
        admin = CookieConsentConfigAdmin(CookieConsentConfig, site)
        request = rf.get("/admin/")
        request.user = superuser
        assert admin.has_add_permission(request) is False


@pytest.mark.django_db
class TestConsentVersionAdmin:
    """Test version admin auto-snapshot."""

    def test_save_model_creates_snapshot(self, site, rf, config, superuser):
        """Saving a new version auto-generates a snapshot.

        Note: ``config`` already has a 1.0 auto-created by ``CookieConsentConfig.save()``,
        so this test creates a *second* version to exercise the admin's snapshot path.
        """
        admin = ConsentVersionAdmin(ConsentVersion, site)
        version = ConsentVersion(
            config=config,
            version="2.0",
            change_description="Policy update",
        )
        request = rf.post("/admin/")
        request.user = superuser
        admin.save_model(request, version, None, change=False)
        assert version.snapshot is not None
        assert version.pk is not None


@pytest.mark.django_db
class TestUserConsentAdmin:
    """Test read-only consent admin."""

    def test_no_add_permission(self, site, rf):
        """Cannot add consent via admin."""
        admin = UserConsentAdmin(UserConsent, site)
        request = rf.get("/admin/")
        assert admin.has_add_permission(request) is False

    def test_no_change_permission(self, site, rf):
        """Cannot change consent via admin."""
        admin = UserConsentAdmin(UserConsent, site)
        request = rf.get("/admin/")
        assert admin.has_change_permission(request) is False

    def test_no_delete_permission(self, site, rf):
        """Cannot delete consent via admin."""
        admin = UserConsentAdmin(UserConsent, site)
        request = rf.get("/admin/")
        assert admin.has_delete_permission(request) is False

    def test_export_consent_csv(self, site, rf, consent):
        """CSV export produces valid CSV output."""
        admin = UserConsentAdmin(UserConsent, site)
        request = rf.get("/admin/")
        queryset = UserConsent.objects.all()
        response = admin.export_consent_csv(request, queryset)
        assert response["Content-Type"] == "text/csv"
        content = response.content.decode("utf-8")
        assert "Consent ID" in content
        assert str(consent.consent_id) in content


@pytest.mark.django_db
class TestCookieGroupAdmin:
    """Test CookieGroup admin with CookieInline."""

    def test_cookie_group_admin_registered(self, site):
        """CookieGroupAdmin is properly configured."""
        admin = CookieGroupAdmin(CookieGroup, site)
        assert len(admin.inlines) == 1

    def test_cookie_count_display(self, site, analytics_group, analytics_cookies):
        """cookie_count shows correct count."""
        admin = CookieGroupAdmin(CookieGroup, site)
        assert admin.cookie_count(analytics_group) == 2
