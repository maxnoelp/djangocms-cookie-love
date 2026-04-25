from django.contrib.auth import get_user_model
from django.contrib.sites.models import Site
from django.core.management import call_command
from django.core.management.base import BaseCommand

from djangocms_cookie_love.models import Cookie, CookieConsentConfig, CookieGroup, ConsentVersion


class Command(BaseCommand):
    help = "Set up the example project with demo data"

    def handle(self, *args, **options):
        self.stdout.write("==> Migrationen ausführen...")
        call_command("migrate", verbosity=0)

        self.stdout.write("==> Superuser anlegen (admin/admin)...")
        User = get_user_model()
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@example.com", "admin")
            self.stdout.write("    Superuser erstellt.")
        else:
            self.stdout.write("    (Superuser existiert bereits)")

        self.stdout.write("==> Site-Domain auf localhost:8000 setzen...")
        site = Site.objects.get(pk=1)
        site.domain = "localhost:8000"
        site.name = "Cookie Love Example"
        site.save()

        self.stdout.write("==> Cookie-Consent-Konfiguration anlegen...")
        if not CookieConsentConfig.objects.exists():
            config = CookieConsentConfig.objects.create(
                title="Cookie-Einstellungen",
                description=(
                    "Wir verwenden Cookies, um Ihnen die bestmögliche Erfahrung auf unserer "
                    "Website zu bieten. Einige Cookies sind für den Betrieb der Website notwendig, "
                    "während andere uns helfen, die Website zu verbessern."
                ),
                privacy_policy_url="/datenschutz/",
                imprint_url="/impressum/",
                position="bottom",
                accept_all_label="Alle akzeptieren",
                reject_all_label="Nur Notwendige",
                settings_label="Einstellungen",
                save_label="Einstellungen speichern",
                is_active=True,
            )

            essential = CookieGroup.objects.create(
                config=config,
                name="Notwendige Cookies",
                slug="essential",
                description="Diese Cookies sind für die Grundfunktionen der Website erforderlich und können nicht deaktiviert werden.",
                is_required=True,
                is_default_enabled=True,
                order=0,
            )
            Cookie.objects.bulk_create([
                Cookie(group=essential, name="sessionid", slug="sessionid", provider="Diese Website", duration="Sitzung", purpose="Session-Verwaltung", is_required=True, order=0),
                Cookie(group=essential, name="csrftoken", slug="csrftoken", provider="Diese Website", duration="1 Jahr", purpose="CSRF-Schutz", is_required=True, order=1),
                Cookie(group=essential, name="cookie_love_consent", slug="cookie-love-consent", provider="Diese Website", duration="1 Jahr", purpose="Speichert Ihre Cookie-Einwilligung", is_required=True, order=2),
            ])

            analytics = CookieGroup.objects.create(
                config=config,
                name="Analyse-Cookies",
                slug="analytics",
                description="Diese Cookies helfen uns zu verstehen, wie Besucher unsere Website nutzen. Alle Daten werden anonymisiert.",
                is_required=False,
                is_default_enabled=False,
                order=1,
            )
            Cookie.objects.bulk_create([
                Cookie(group=analytics, name="_ga", slug="ga", provider="Google Analytics", duration="2 Jahre", purpose="Unterscheidung von Nutzern", order=0),
                Cookie(group=analytics, name="_gid", slug="gid", provider="Google Analytics", duration="24 Stunden", purpose="Unterscheidung von Nutzern", order=1),
                Cookie(group=analytics, name="_gat", slug="gat", provider="Google Analytics", duration="1 Minute", purpose="Anfragendrosselung", order=2),
            ])

            marketing = CookieGroup.objects.create(
                config=config,
                name="Marketing-Cookies",
                slug="marketing",
                description="Marketing-Cookies werden verwendet, um Besuchern relevante Werbung anzuzeigen.",
                is_required=False,
                is_default_enabled=False,
                order=2,
            )
            Cookie.objects.bulk_create([
                Cookie(group=marketing, name="_fbp", slug="fbp", provider="Facebook", duration="3 Monate", purpose="Werbeanzeigen-Tracking", order=0),
                Cookie(group=marketing, name="fr", slug="fr", provider="Facebook", duration="3 Monate", purpose="Werbeanzeigen-Auslieferung", order=1),
            ])

            preferences = CookieGroup.objects.create(
                config=config,
                name="Präferenz-Cookies",
                slug="preferences",
                description="Präferenz-Cookies ermöglichen es der Website, sich an Informationen zu erinnern, die die Art und Weise beeinflussen, wie sich die Website verhält.",
                is_required=False,
                is_default_enabled=False,
                order=3,
            )
            Cookie.objects.bulk_create([
                Cookie(group=preferences, name="django_language", slug="django-language", provider="Diese Website", duration="1 Jahr", purpose="Bevorzugte Sprache", order=0),
            ])

            ConsentVersion.objects.create(
                config=config,
                version="1.0",
                change_description="Initiale Cookie-Konfiguration",
                requires_reconsent=False,
            )
            self.stdout.write("    Cookie-Konfiguration erstellt!")
        else:
            self.stdout.write("    (Cookie-Konfiguration existiert bereits)")

        self.stdout.write("==> Static files sammeln...")
        call_command("collectstatic", verbosity=0, interactive=False)

        self.stdout.write("")
        self.stdout.write("==========================================")
        self.stdout.write("  Example-Projekt ist bereit!")
        self.stdout.write("")
        self.stdout.write("  Server starten:  python manage.py runserver")
        self.stdout.write("  Admin:           http://localhost:8000/admin/")
        self.stdout.write("  Login:           admin / admin")
        self.stdout.write("==========================================")
