from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_cookie_love", "0005_cookieconsentconfig_imprint_page_and_more"),
    ]

    operations = [
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
