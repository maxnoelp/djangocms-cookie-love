from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("djangocms_cookie_love", "0006_discoveredcookie"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cookieconsentconfig",
            name="privacy_policy_page",
        ),
        migrations.RemoveField(
            model_name="cookieconsentconfig",
            name="imprint_page",
        ),
        migrations.AddField(
            model_name="cookieconsentconfig",
            name="privacy_policy_path",
            field=models.CharField(
                blank=True,
                help_text="Internal path, e.g. /privacy/ – takes precedence over the external URL",
                max_length=500,
                verbose_name="Privacy Policy Path",
            ),
        ),
        migrations.AddField(
            model_name="cookieconsentconfig",
            name="imprint_path",
            field=models.CharField(
                blank=True,
                help_text="Internal path, e.g. /imprint/ – takes precedence over the external URL",
                max_length=500,
                verbose_name="Imprint Path",
            ),
        ),
    ]
