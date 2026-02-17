"""Add Cookie model and accepted_cookies M2M on UserConsent.

Data migration: converts existing JSON cookies from CookieGroup.cookies
into Cookie model instances.
"""

import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def migrate_json_cookies_to_model(apps, schema_editor):
    """Convert CookieGroup.cookies JSON entries into Cookie objects."""
    CookieGroup = apps.get_model("djangocms_cookie_love", "CookieGroup")
    Cookie = apps.get_model("djangocms_cookie_love", "Cookie")

    for group in CookieGroup.objects.all():
        if not group.cookies:
            continue
        for idx, cookie_data in enumerate(group.cookies):
            name = cookie_data.get("name", f"cookie-{idx}")
            slug = slugify(name) or f"cookie-{idx}"
            # Ensure slug uniqueness within the group
            base_slug = slug
            counter = 1
            while Cookie.objects.filter(group=group, slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            Cookie.objects.create(
                group=group,
                name=name,
                slug=slug,
                provider=cookie_data.get("provider", ""),
                duration=cookie_data.get("duration", ""),
                purpose=cookie_data.get("purpose", ""),
                is_required=group.is_required,
                order=idx,
            )


def reverse_migration(apps, schema_editor):
    """No-op reverse – JSON field still contains the data."""
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_cookie_love", "0003_alter_userconsent_consent_method"),
    ]

    operations = [
        # 1. Create Cookie model
        migrations.CreateModel(
            name="Cookie",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
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
                (
                    "order",
                    models.PositiveIntegerField(default=0, verbose_name="Order"),
                ),
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
        # 2. Add accepted_cookies M2M to UserConsent
        migrations.AddField(
            model_name="userconsent",
            name="accepted_cookies",
            field=models.ManyToManyField(
                blank=True,
                related_name="consents",
                to="djangocms_cookie_love.cookie",
                verbose_name="Accepted Cookies",
            ),
        ),
        # 3. Data migration: convert JSON cookies to Cookie objects
        migrations.RunPython(
            migrate_json_cookies_to_model,
            reverse_migration,
        ),
    ]
