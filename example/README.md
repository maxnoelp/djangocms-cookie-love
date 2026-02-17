# Example Project – Cookie Love

Kleines Django CMS Projekt zum manuellen Testen des Cookie-Consent-Banners.

## Setup

```bash
cd example
chmod +x setup.sh
bash setup.sh
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
