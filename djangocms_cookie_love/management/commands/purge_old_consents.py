"""Management command to delete expired UserConsent records."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from djangocms_cookie_love.constants import CONSENT_RETENTION_DAYS
from djangocms_cookie_love.models import UserConsent


class Command(BaseCommand):
    help = (
        "Delete UserConsent records older than the configured retention period "
        "(default: 3 years / 1095 days). Run this periodically via cron or Celery "
        "to comply with GDPR Art. 5(1)(e) storage limitation."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--days",
            type=int,
            default=CONSENT_RETENTION_DAYS,
            help=f"Delete records older than this many days (default: {CONSENT_RETENTION_DAYS})",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting anything",
        )

    def handle(self, *args, **options):
        days = options["days"]
        dry_run = options["dry_run"]
        cutoff = timezone.now() - timedelta(days=days)

        qs = UserConsent.objects.filter(consent_given_at__lt=cutoff)
        count = qs.count()

        if dry_run:
            self.stdout.write(
                f"[DRY RUN] Would delete {count} consent record(s) older than {days} days (before {cutoff.date()})."
            )
            return

        deleted, _ = qs.delete()
        self.stdout.write(self.style.SUCCESS(f"Deleted {deleted} consent record(s) older than {days} days."))
