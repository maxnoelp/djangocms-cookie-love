"""Squashed migration combining the original 0001..0007 chain.

Replaces the migration history that originally referenced ``cms.Page`` via
``PageField``. The current schema uses plain ``CharField`` paths and has no
runtime django-cms dependency — neither at import time nor at migration time.
Existing installs that have applied any of the replaced migrations transition
cleanly via the ``replaces`` declaration: Django runs the still-present legacy
files to reach the "all replaced applied" state and then marks this squash as
applied with no further operations. Fresh installs run only this single file.
"""

import uuid

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    replaces = [
        ("djangocms_cookie_love", "0001_initial"),
        ("djangocms_cookie_love", "0002_default_cookie_groups"),
        ("djangocms_cookie_love", "0003_alter_userconsent_consent_method"),
        ("djangocms_cookie_love", "0004_cookie_model"),
        ("djangocms_cookie_love", "0005_cookieconsentconfig_imprint_page_and_more"),
        ("djangocms_cookie_love", "0006_discoveredcookie"),
        ("djangocms_cookie_love", "0007_replace_page_fields_with_paths"),
    ]

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CookieConsentConfig",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(default="Cookie Settings", max_length=255, verbose_name="Title")),
                (
                    "description",
                    models.TextField(
                        default=(
                            "We use cookies to improve your experience on our website. "
                            "Some cookies are essential for the website to function, while others "
                            "help us understand how you use our site."
                        ),
                        help_text="Main text displayed in the cookie banner",
                        verbose_name="Description",
                    ),
                ),
                (
                    "privacy_policy_path",
                    models.CharField(
                        blank=True,
                        help_text="Internal path, e.g. /privacy/ – takes precedence over the external URL",
                        max_length=500,
                        verbose_name="Privacy Policy Path",
                    ),
                ),
                (
                    "privacy_policy_url",
                    models.URLField(
                        blank=True,
                        help_text="External URL – only used if no internal path is set",
                        verbose_name="Privacy Policy URL (external)",
                    ),
                ),
                (
                    "imprint_path",
                    models.CharField(
                        blank=True,
                        help_text="Internal path, e.g. /imprint/ – takes precedence over the external URL",
                        max_length=500,
                        verbose_name="Imprint Path",
                    ),
                ),
                (
                    "imprint_url",
                    models.URLField(
                        blank=True,
                        help_text="External URL – only used if no internal path is set",
                        verbose_name="Imprint URL (external)",
                    ),
                ),
                (
                    "position",
                    models.CharField(
                        choices=[("bottom", "Bottom Bar"), ("top", "Top Bar"), ("center", "Center Modal")],
                        default="bottom",
                        max_length=20,
                        verbose_name="Position",
                    ),
                ),
                (
                    "accept_all_label",
                    models.CharField(default="Accept All", max_length=50, verbose_name="Accept All Button Label"),
                ),
                (
                    "reject_all_label",
                    models.CharField(default="Only Essential", max_length=50, verbose_name="Reject Button Label"),
                ),
                (
                    "settings_label",
                    models.CharField(default="Settings", max_length=50, verbose_name="Settings Button Label"),
                ),
                (
                    "save_label",
                    models.CharField(default="Save Preferences", max_length=50, verbose_name="Save Button Label"),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Active")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Created At")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Updated At")),
            ],
            options={
                "verbose_name": "Cookie Consent Configuration",
                "verbose_name_plural": "Cookie Consent Configurations",
            },
        ),
        migrations.CreateModel(
            name="CookieGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100, verbose_name="Name")),
                ("slug", models.SlugField(max_length=100, unique=True, verbose_name="Slug")),
                (
                    "description",
                    models.TextField(
                        help_text="Explains to the user what this cookie group does",
                        verbose_name="Description",
                    ),
                ),
                (
                    "is_required",
                    models.BooleanField(
                        default=False,
                        help_text="Required groups cannot be deactivated (e.g. Essential)",
                        verbose_name="Required",
                    ),
                ),
                (
                    "is_default_enabled",
                    models.BooleanField(
                        default=False,
                        help_text="Pre-selected state (only allowed for required groups per GDPR)",
                        verbose_name="Enabled by Default",
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Order")),
                (
                    "cookies",
                    models.JSONField(
                        blank=True,
                        default=list,
                        help_text=(
                            'List of cookies: [{"name": "...", "provider": "...", '
                            '"duration": "...", "purpose": "..."}]'
                        ),
                        verbose_name="Cookies",
                    ),
                ),
                (
                    "config",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cookie_groups",
                        to="djangocms_cookie_love.cookieconsentconfig",
                        verbose_name="Configuration",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cookie Group",
                "verbose_name_plural": "Cookie Groups",
                "ordering": ["order"],
            },
        ),
        migrations.CreateModel(
            name="Cookie",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "name",
                    models.CharField(
                        help_text="Technical cookie name, e.g. _ga, _fbp",
                        max_length=100,
                        verbose_name="Cookie Name",
                    ),
                ),
                (
                    "slug",
                    models.SlugField(
                        help_text="Unique identifier within the group, used for API identification",
                        max_length=100,
                        verbose_name="Slug",
                    ),
                ),
                (
                    "provider",
                    models.CharField(
                        blank=True,
                        help_text="Service that sets this cookie, e.g. Google Analytics",
                        max_length=200,
                        verbose_name="Provider",
                    ),
                ),
                (
                    "duration",
                    models.CharField(
                        blank=True,
                        help_text="How long the cookie persists, e.g. 2 years, Session",
                        max_length=100,
                        verbose_name="Duration",
                    ),
                ),
                (
                    "purpose",
                    models.TextField(
                        blank=True,
                        help_text="Description of what this cookie is used for",
                        verbose_name="Purpose",
                    ),
                ),
                (
                    "is_required",
                    models.BooleanField(
                        default=False,
                        help_text="Required cookies cannot be deselected by the user",
                        verbose_name="Required",
                    ),
                ),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Order")),
                (
                    "group",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="cookie_items",
                        to="djangocms_cookie_love.cookiegroup",
                        verbose_name="Cookie Group",
                    ),
                ),
            ],
            options={
                "verbose_name": "Cookie",
                "verbose_name_plural": "Cookies",
                "ordering": ["order", "name"],
                "unique_together": {("group", "slug")},
            },
        ),
        migrations.CreateModel(
            name="ConsentVersion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("version", models.CharField(max_length=20, verbose_name="Version")),
                (
                    "change_description",
                    models.TextField(help_text="What changed in this version", verbose_name="Change Description"),
                ),
                (
                    "requires_reconsent",
                    models.BooleanField(
                        default=False,
                        help_text="If checked, all users must re-consent",
                        verbose_name="Requires Re-consent",
                    ),
                ),
                ("published_at", models.DateTimeField(auto_now_add=True, verbose_name="Published At")),
                (
                    "snapshot",
                    models.JSONField(
                        help_text="Complete snapshot of config and cookie groups at time of publishing",
                        verbose_name="Snapshot",
                    ),
                ),
                (
                    "config",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="versions",
                        to="djangocms_cookie_love.cookieconsentconfig",
                        verbose_name="Configuration",
                    ),
                ),
            ],
            options={
                "verbose_name": "Consent Version",
                "verbose_name_plural": "Consent Versions",
                "ordering": ["-published_at"],
                "unique_together": {("config", "version")},
            },
        ),
        migrations.CreateModel(
            name="UserConsent",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                (
                    "consent_id",
                    models.UUIDField(default=uuid.uuid4, editable=False, unique=True, verbose_name="Consent ID"),
                ),
                (
                    "ip_hash",
                    models.CharField(
                        help_text="SHA-256 hash of the user's IP address",
                        max_length=64,
                        verbose_name="IP Hash",
                    ),
                ),
                ("user_agent", models.TextField(blank=True, verbose_name="User Agent")),
                (
                    "consent_method",
                    models.CharField(
                        choices=[
                            ("banner_accept_all", "Banner – Accept All"),
                            ("banner_reject", "Banner – Reject Optional"),
                            ("settings", "Settings Modal"),
                            ("revoke", "Revoke"),
                            ("api", "API"),
                        ],
                        max_length=30,
                        verbose_name="Consent Method",
                    ),
                ),
                ("consent_given_at", models.DateTimeField(auto_now_add=True, verbose_name="Consent Given At")),
                (
                    "accepted_groups",
                    models.ManyToManyField(
                        blank=True,
                        related_name="consents",
                        to="djangocms_cookie_love.cookiegroup",
                        verbose_name="Accepted Groups",
                    ),
                ),
                (
                    "accepted_cookies",
                    models.ManyToManyField(
                        blank=True,
                        related_name="consents",
                        to="djangocms_cookie_love.cookie",
                        verbose_name="Accepted Cookies",
                    ),
                ),
                (
                    "version",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="user_consents",
                        to="djangocms_cookie_love.consentversion",
                        verbose_name="Consent Version",
                    ),
                ),
            ],
            options={
                "verbose_name": "User Consent",
                "verbose_name_plural": "User Consents",
                "ordering": ["-consent_given_at"],
            },
        ),
        migrations.CreateModel(
            name="DiscoveredCookie",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=200, verbose_name="Cookie Name")),
                (
                    "domain",
                    models.CharField(
                        blank=True,
                        help_text="Empty for first-party cookies on the host domain",
                        max_length=200,
                        verbose_name="Domain",
                    ),
                ),
                (
                    "source",
                    models.CharField(
                        choices=[("server", "Server response"), ("crawler", "Crawler")],
                        max_length=20,
                        verbose_name="Source",
                    ),
                ),
                ("first_seen", models.DateTimeField(auto_now_add=True, verbose_name="First Seen")),
                ("last_seen", models.DateTimeField(auto_now_add=True, verbose_name="Last Seen")),
                ("occurrence_count", models.PositiveIntegerField(default=1, verbose_name="Occurrence Count")),
                ("sample_path", models.CharField(blank=True, max_length=500, verbose_name="Sample Path")),
                ("sample_user_agent", models.CharField(blank=True, max_length=500, verbose_name="Sample User Agent")),
                (
                    "seen_in",
                    models.JSONField(
                        blank=True,
                        default=dict,
                        help_text="Crawler context tags: role, consent state, locale",
                        verbose_name="Seen In",
                    ),
                ),
                (
                    "is_resolved",
                    models.BooleanField(
                        default=False,
                        help_text="Tick once the cookie has been documented or dismissed",
                        verbose_name="Resolved",
                    ),
                ),
                ("notes", models.TextField(blank=True, verbose_name="Notes")),
            ],
            options={
                "verbose_name": "Discovered Cookie",
                "verbose_name_plural": "Discovered Cookies",
                "ordering": ["-last_seen"],
                "unique_together": {("name", "domain", "source")},
            },
        ),
    ]
