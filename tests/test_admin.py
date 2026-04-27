"""Tests for admin functionality."""

import pytest
from django.contrib.admin.sites import AdminSite
from django.contrib.auth.models import User
from django.contrib.messages.storage.fallback import FallbackStorage
from django.test import RequestFactory

from djangocms_cookie_love.admin import (
    ConsentVersionAdmin,
    CookieConsentConfigAdmin,
    CookieGroupAdmin,
    DiscoveredCookieAdmin,
    UserConsentAdmin,
    _make_assign_to_group_action,
    _unique_cookie_slug,
)
from djangocms_cookie_love.models import (
    ConsentVersion,
    Cookie,
    CookieConsentConfig,
    CookieGroup,
    DiscoveredCookie,
    UserConsent,
)


def _attach_messages(request):
    """RequestFactory requests don't have a session/messages backend."""
    setattr(request, "session", {})
    setattr(request, "_messages", FallbackStorage(request))
    return request


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


@pytest.mark.django_db
class TestUniqueCookieSlug:
    """Test slug-collision handling helper used by the assign-to-group action."""

    def test_simple_slug(self, analytics_group):
        assert _unique_cookie_slug(analytics_group, "_fbp") == "fbp"

    def test_falls_back_when_slugify_yields_empty(self, analytics_group):
        # slugify("___") -> "" so the helper must use the "cookie" fallback.
        assert _unique_cookie_slug(analytics_group, "___") == "cookie"

    def test_appends_suffix_on_collision(self, analytics_group, analytics_cookies):
        # analytics_cookies fixture already creates slug="ga" in this group.
        assert _unique_cookie_slug(analytics_group, "_ga") == "ga-2"

    def test_collision_only_within_group(self, essential_group, analytics_group, analytics_cookies):
        # "ga" exists in analytics_group but not in essential_group.
        assert _unique_cookie_slug(essential_group, "_ga") == "ga"

    def test_truncates_long_names(self, analytics_group):
        slug = _unique_cookie_slug(analytics_group, "x" * 250)
        assert len(slug) <= 100


@pytest.mark.django_db
class TestDiscoveredCookieAssignAction:
    """Test the dynamic per-group 'Assign to cookie group' admin actions."""

    def _make_discovered(self, name, *, domain="example.com", source="crawler"):
        return DiscoveredCookie.objects.create(name=name, domain=domain, source=source)

    def test_get_actions_includes_one_per_group(self, site, rf, superuser, essential_group, analytics_group):
        admin = DiscoveredCookieAdmin(DiscoveredCookie, site)
        request = rf.get("/admin/")
        request.user = superuser
        actions = admin.get_actions(request)
        assert f"assign_to_group_{essential_group.pk}" in actions
        assert f"assign_to_group_{analytics_group.pk}" in actions

    def test_get_actions_label_includes_group_name(self, site, rf, superuser, analytics_group):
        admin = DiscoveredCookieAdmin(DiscoveredCookie, site)
        request = rf.get("/admin/")
        request.user = superuser
        actions = admin.get_actions(request)
        _, _, description = actions[f"assign_to_group_{analytics_group.pk}"]
        assert "Analytics" in str(description)

    def test_action_creates_cookie_and_marks_resolved(self, site, rf, superuser, analytics_group):
        discovered = self._make_discovered("_fbp", domain="facebook.com")
        admin = DiscoveredCookieAdmin(DiscoveredCookie, site)
        request = _attach_messages(rf.post("/admin/"))
        request.user = superuser

        action = _make_assign_to_group_action(analytics_group)
        action(admin, request, DiscoveredCookie.objects.filter(pk=discovered.pk))

        cookie = Cookie.objects.get(group=analytics_group, name="_fbp")
        assert cookie.slug == "fbp"
        assert cookie.provider == "facebook.com"
        assert cookie.is_required is False  # group is not required

        discovered.refresh_from_db()
        assert discovered.is_resolved is True

    def test_action_inherits_is_required_from_group(self, site, rf, superuser, essential_group):
        discovered = self._make_discovered("csrftoken", domain="")
        admin = DiscoveredCookieAdmin(DiscoveredCookie, site)
        request = _attach_messages(rf.post("/admin/"))
        request.user = superuser

        action = _make_assign_to_group_action(essential_group)
        action(admin, request, DiscoveredCookie.objects.filter(pk=discovered.pk))

        cookie = Cookie.objects.get(group=essential_group, name="csrftoken")
        assert cookie.is_required is True

    def test_action_is_idempotent_for_existing_name(
        self, site, rf, superuser, analytics_group, analytics_cookies
    ):
        # analytics_cookies fixture already creates a Cookie name="_ga" in this group.
        discovered = self._make_discovered("_ga", domain="google.com")
        admin = DiscoveredCookieAdmin(DiscoveredCookie, site)
        request = _attach_messages(rf.post("/admin/"))
        request.user = superuser

        before = Cookie.objects.filter(group=analytics_group, name="_ga").count()
        action = _make_assign_to_group_action(analytics_group)
        action(admin, request, DiscoveredCookie.objects.filter(pk=discovered.pk))
        after = Cookie.objects.filter(group=analytics_group, name="_ga").count()

        assert before == after == 1
        discovered.refresh_from_db()
        assert discovered.is_resolved is True

    def test_action_processes_multiple_selected_rows(self, site, rf, superuser, analytics_group):
        d1 = self._make_discovered("_fbp", domain="facebook.com")
        d2 = self._make_discovered("_ttp", domain="tiktok.com")
        admin = DiscoveredCookieAdmin(DiscoveredCookie, site)
        request = _attach_messages(rf.post("/admin/"))
        request.user = superuser

        action = _make_assign_to_group_action(analytics_group)
        action(admin, request, DiscoveredCookie.objects.filter(pk__in=[d1.pk, d2.pk]))

        assert Cookie.objects.filter(group=analytics_group, name="_fbp").exists()
        assert Cookie.objects.filter(group=analytics_group, name="_ttp").exists()
        d1.refresh_from_db()
        d2.refresh_from_db()
        assert d1.is_resolved is True
        assert d2.is_resolved is True

    def test_action_handles_slug_collision(self, site, rf, superuser, analytics_group, analytics_cookies):
        # analytics_cookies creates slug="ga"; a new cookie named "ga" must get "ga-2".
        discovered = self._make_discovered("ga", domain="other.example.com")
        admin = DiscoveredCookieAdmin(DiscoveredCookie, site)
        request = _attach_messages(rf.post("/admin/"))
        request.user = superuser

        action = _make_assign_to_group_action(analytics_group)
        action(admin, request, DiscoveredCookie.objects.filter(pk=discovered.pk))

        cookie = Cookie.objects.get(group=analytics_group, name="ga")
        assert cookie.slug == "ga-2"
