"""Tests for the purge_old_consents management command."""

from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.utils import timezone

from djangocms_cookie_love.models import UserConsent
from djangocms_cookie_love.utils import hash_ip


def _make_consent(version, days_ago):
    """Create a UserConsent with consent_given_at set to `days_ago` days in the past."""
    consent = UserConsent.objects.create(
        version=version,
        ip_hash=hash_ip("127.0.0.1"),
        user_agent="TestAgent/1.0",
        consent_method="banner_accept_all",
    )
    # Bypass auto_now_add by using update()
    UserConsent.objects.filter(pk=consent.pk).update(consent_given_at=timezone.now() - timedelta(days=days_ago))
    return consent


@pytest.mark.django_db
class TestPurgeOldConsents:
    def test_deletes_old_records(self, version):
        """Records older than --days are deleted."""
        old = _make_consent(version, days_ago=1100)
        recent = _make_consent(version, days_ago=10)

        call_command("purge_old_consents", "--days=1095")

        assert not UserConsent.objects.filter(pk=old.pk).exists()
        assert UserConsent.objects.filter(pk=recent.pk).exists()

    def test_dry_run_does_not_delete(self, version):
        """--dry-run reports but does not delete anything."""
        old = _make_consent(version, days_ago=1100)

        out = StringIO()
        call_command("purge_old_consents", "--days=1095", "--dry-run", stdout=out)

        assert UserConsent.objects.filter(pk=old.pk).exists()
        assert "DRY RUN" in out.getvalue()
        assert "1 consent record" in out.getvalue()

    def test_custom_days_argument(self, version):
        """--days overrides the default retention period."""
        consent_30d = _make_consent(version, days_ago=30)
        consent_5d = _make_consent(version, days_ago=5)

        call_command("purge_old_consents", "--days=10")

        assert not UserConsent.objects.filter(pk=consent_30d.pk).exists()
        assert UserConsent.objects.filter(pk=consent_5d.pk).exists()

    def test_nothing_to_delete(self, version):
        """Command runs cleanly when no records match."""
        _make_consent(version, days_ago=10)

        out = StringIO()
        call_command("purge_old_consents", "--days=1095", stdout=out)

        assert UserConsent.objects.count() == 1
        assert "0 consent record" in out.getvalue()
