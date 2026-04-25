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

```bash
cd example
python manage.py setup_example
```

Das funktioniert auf Linux, macOS und Windows gleich. Der Command führt Migrationen aus, legt den Superuser an, konfiguriert die Site-Domain, erstellt die Cookie-Konfiguration und sammelt Static Files.

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
