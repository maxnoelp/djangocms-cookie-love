# Example Project – Cookie Love

Kleines Django CMS Projekt zum manuellen Testen des Cookie-Consent-Banners.

## Setup

### 1. Virtuelle Umgebung erstellen und aktivieren

Zuerst im **Root-Verzeichnis** des Projekts (nicht im `example/`-Ordner):

**Linux / macOS**
```bash
python -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell)**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

### 2. Abhängigkeiten installieren

```bash
pip install -e ".[dev]"
```

### 3. Projekt initialisieren

**Linux / macOS**
```bash
cd example
chmod +x setup.sh
bash setup.sh
```

**Windows (PowerShell)**
```powershell
cd example

python manage.py migrate

$env:DJANGO_SUPERUSER_PASSWORD = "admin"
python manage.py createsuperuser --username admin --email admin@example.com --noinput

python manage.py shell -c "from django.contrib.sites.models import Site; s = Site.objects.get(pk=1); s.domain = 'localhost:8000'; s.name = 'Cookie Love Example'; s.save()"

python manage.py collectstatic --noinput -v 0
```

## Server starten

```bash
python manage.py runserver
```

- **Website:** http://localhost:8000/
- **Admin:** http://localhost:8000/admin/
- **Login:** `admin` / `admin`

## Was testen?

1. Banner erscheint beim ersten Besuch
2. "Alle akzeptieren" → Banner verschwindet, Cookie wird gesetzt
3. "Nur Notwendige" → Nur Essential-Cookies akzeptiert
4. "Einstellungen" → Modal öffnet sich, Gruppen einzeln togglen
5. Footer-Link "Cookie-Einstellungen ändern" → Settings-Modal
6. Admin: Consent-Records einsehen, CSV exportieren
7. Neue Version anlegen mit `requires_reconsent=True` → Banner erscheint erneut
