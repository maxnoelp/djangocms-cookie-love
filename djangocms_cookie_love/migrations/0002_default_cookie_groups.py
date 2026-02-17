"""Data migration: create default cookie groups when first config is created."""

from django.db import migrations


def create_default_groups(apps, schema_editor):
    """This is a no-op forward migration.
    Default groups are created via constants.DEFAULT_COOKIE_GROUPS
    when an admin creates the first CookieConsentConfig.
    This migration exists as a placeholder for custom data seeding.
    """
    pass


def remove_default_groups(apps, schema_editor):
    """Reverse: nothing to undo."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_cookie_love", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_default_groups, remove_default_groups),
    ]
