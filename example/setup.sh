#!/usr/bin/env bash
# Setup-Skript für das Example-Projekt
# Führt Migrationen aus, erstellt Superuser und eine Startseite.

set -e
cd "$(dirname "$0")"

echo "==> Migrationen ausführen..."
python manage.py migrate

echo ""
echo "==> Superuser anlegen (admin/admin)..."
DJANGO_SUPERUSER_PASSWORD=admin \
python manage.py createsuperuser \
    --username admin \
    --email admin@example.com \
    --noinput 2>/dev/null || echo "    (Superuser existiert bereits)"

echo ""
echo "==> Site-Domain auf localhost:8000 setzen..."
python manage.py shell -c "
from django.contrib.sites.models import Site
site = Site.objects.get(pk=1)
site.domain = 'localhost:8000'
site.name = 'Cookie Love Example'
site.save()
"

echo ""
echo "==> Cookie-Consent-Konfiguration anlegen..."
python manage.py shell -c "
from djangocms_cookie_love.models import CookieConsentConfig, CookieGroup, ConsentVersion

if not CookieConsentConfig.objects.exists():
    config = CookieConsentConfig.objects.create(
        title='Cookie-Einstellungen',
        description='Wir verwenden Cookies, um Ihnen die bestmögliche Erfahrung auf unserer Website zu bieten. Einige Cookies sind für den Betrieb der Website notwendig, während andere uns helfen, die Website zu verbessern.',
        privacy_policy_url='/datenschutz/',
        imprint_url='/impressum/',
        position='bottom',
        accept_all_label='Alle akzeptieren',
        reject_all_label='Nur Notwendige',
        settings_label='Einstellungen',
        save_label='Einstellungen speichern',
        is_active=True,
    )

    CookieGroup.objects.create(
        config=config,
        name='Notwendige Cookies',
        slug='essential',
        description='Diese Cookies sind für die Grundfunktionen der Website erforderlich und können nicht deaktiviert werden.',
        is_required=True,
        is_default_enabled=True,
        order=0,
        cookies=[
            {'name': 'sessionid', 'provider': 'Diese Website', 'duration': 'Sitzung', 'purpose': 'Session-Verwaltung'},
            {'name': 'csrftoken', 'provider': 'Diese Website', 'duration': '1 Jahr', 'purpose': 'CSRF-Schutz'},
            {'name': 'cookie_love_consent', 'provider': 'Diese Website', 'duration': '1 Jahr', 'purpose': 'Speichert Ihre Cookie-Einwilligung'},
        ],
    )

    CookieGroup.objects.create(
        config=config,
        name='Analyse-Cookies',
        slug='analytics',
        description='Diese Cookies helfen uns zu verstehen, wie Besucher unsere Website nutzen. Alle Daten werden anonymisiert.',
        is_required=False,
        is_default_enabled=False,
        order=1,
        cookies=[
            {'name': '_ga', 'provider': 'Google Analytics', 'duration': '2 Jahre', 'purpose': 'Unterscheidung von Nutzern'},
            {'name': '_gid', 'provider': 'Google Analytics', 'duration': '24 Stunden', 'purpose': 'Unterscheidung von Nutzern'},
            {'name': '_gat', 'provider': 'Google Analytics', 'duration': '1 Minute', 'purpose': 'Anfragendrosselung'},
        ],
    )

    CookieGroup.objects.create(
        config=config,
        name='Marketing-Cookies',
        slug='marketing',
        description='Marketing-Cookies werden verwendet, um Besuchern relevante Werbung anzuzeigen.',
        is_required=False,
        is_default_enabled=False,
        order=2,
        cookies=[
            {'name': '_fbp', 'provider': 'Facebook', 'duration': '3 Monate', 'purpose': 'Werbeanzeigen-Tracking'},
            {'name': 'fr', 'provider': 'Facebook', 'duration': '3 Monate', 'purpose': 'Werbeanzeigen-Auslieferung'},
        ],
    )

    CookieGroup.objects.create(
        config=config,
        name='Präferenz-Cookies',
        slug='preferences',
        description='Präferenz-Cookies ermöglichen es der Website, sich an Informationen zu erinnern, die die Art und Weise beeinflussen, wie sich die Website verhält (z.B. bevorzugte Sprache).',
        is_required=False,
        is_default_enabled=False,
        order=3,
        cookies=[
            {'name': 'django_language', 'provider': 'Diese Website', 'duration': '1 Jahr', 'purpose': 'Bevorzugte Sprache'},
        ],
    )

    # Create initial version
    ConsentVersion.objects.create(
        config=config,
        version='1.0',
        change_description='Initiale Cookie-Konfiguration',
        requires_reconsent=False,
    )
    print('    Cookie-Konfiguration erstellt!')
else:
    print('    Cookie-Konfiguration existiert bereits.')
"

echo ""
echo "==> Static files sammeln..."
python manage.py collectstatic --noinput -v 0

echo ""
echo "=========================================="
echo "  Example-Projekt ist bereit!"
echo ""
echo "  Server starten:  cd example && python manage.py runserver"
echo "  Admin:           http://localhost:8000/admin/"
echo "  Login:           admin / admin"
echo "=========================================="
