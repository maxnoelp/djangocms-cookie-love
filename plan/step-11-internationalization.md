# Step 11 – Internationalization (i18n)

## Goal

Full internationalization support with German and English as shipped languages. All user-facing strings (models, templates, JavaScript) are translatable via Django's i18n framework.

## Languages

| Code | Language | Status  |
| ---- | -------- | ------- |
| `en` | English  | Default |
| `de` | German   | Shipped |

## Tasks

### 11.1 Django i18n Configuration

```python
# settings.py (project or test settings)
from django.utils.translation import gettext_lazy as _

LANGUAGE_CODE = "en"

LANGUAGES = [
    ("en", _("English")),
    ("de", _("German")),
]

USE_I18N = True
USE_L10N = True

LOCALE_PATHS = [
    # The package ships its own locale
]
```

### 11.2 Locale Directory Structure

```
djangocms_cookie_love/
└── locale/
    ├── en/
    │   └── LC_MESSAGES/
    │       ├── django.po
    │       └── django.mo
    └── de/
        └── LC_MESSAGES/
            ├── django.po
            └── django.mo
```

### 11.3 Model Translations

All model `verbose_name`, `verbose_name_plural`, `help_text`, choice labels, and default values must use `gettext_lazy`:

```python
from django.utils.translation import gettext_lazy as _

class CookieConsentConfig(models.Model):
    title = models.CharField(
        max_length=255,
        default=_("Cookie Settings"),
        verbose_name=_("Title"),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Main text displayed in the cookie banner"),
    )
    privacy_policy_url = models.URLField(
        blank=True,
        verbose_name=_("Privacy Policy URL"),
        help_text=_("Link to privacy policy page"),
    )
    imprint_url = models.URLField(
        blank=True,
        verbose_name=_("Imprint URL"),
        help_text=_("Link to imprint/legal notice page"),
    )

    POSITION_CHOICES = [
        ("bottom", _("Bottom Bar")),
        ("top", _("Top Bar")),
        ("center", _("Center Modal")),
    ]
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default="bottom",
        verbose_name=_("Position"),
    )

    # Button labels with translated defaults
    accept_all_label = models.CharField(
        max_length=50,
        default=_("Accept All"),
        verbose_name=_("Accept All Button Label"),
    )
    reject_all_label = models.CharField(
        max_length=50,
        default=_("Only Essential"),
        verbose_name=_("Reject Button Label"),
    )
    settings_label = models.CharField(
        max_length=50,
        default=_("Settings"),
        verbose_name=_("Settings Button Label"),
    )
    save_label = models.CharField(
        max_length=50,
        default=_("Save Preferences"),
        verbose_name=_("Save Button Label"),
    )

    class Meta:
        verbose_name = _("Cookie Consent Configuration")
        verbose_name_plural = _("Cookie Consent Configurations")


class CookieGroup(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Explains to the user what this cookie group does"),
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_("Required"),
        help_text=_("Required groups cannot be deactivated (e.g. Essential)"),
    )

    class Meta:
        verbose_name = _("Cookie Group")
        verbose_name_plural = _("Cookie Groups")


class ConsentVersion(models.Model):
    change_description = models.TextField(
        verbose_name=_("Change Description"),
        help_text=_("What changed in this version"),
    )
    requires_reconsent = models.BooleanField(
        default=False,
        verbose_name=_("Requires Re-consent"),
        help_text=_("If True, all users must re-consent"),
    )

    class Meta:
        verbose_name = _("Consent Version")
        verbose_name_plural = _("Consent Versions")


class UserConsent(models.Model):
    CONSENT_METHOD_CHOICES = [
        ("banner_accept_all", _("Banner – Accept All")),
        ("banner_reject", _("Banner – Reject Optional")),
        ("settings", _("Settings Modal")),
        ("api", _("API")),
    ]

    class Meta:
        verbose_name = _("User Consent")
        verbose_name_plural = _("User Consents")
```

### 11.4 Template Translations

All templates use `{% load i18n %}` and `{% trans %}` / `{% blocktrans %}` for static strings:

```html
{% load i18n static %}

<!-- banner.html -->
<div class="cl-banner__links">
  {% if cookie_config.privacy_policy_url %}
  <a href="{{ cookie_config.privacy_policy_url }}" class="cl-banner__link">
    {% trans "Privacy Policy" %}
  </a>
  {% endif %} {% if cookie_config.imprint_url %}
  <a href="{{ cookie_config.imprint_url }}" class="cl-banner__link">
    {% trans "Imprint" %}
  </a>
  {% endif %}
</div>

<!-- cookie_group.html -->
{% if group.is_required %}
<span class="badge bg-secondary cl-group__badge"
  >{% trans "Always Active" %}</span
>
{% endif %}

<details class="cl-group__details">
  <summary>
    {% blocktrans with count=group.cookies|length %}Show cookies ({{ count }}){%
    endblocktrans %}
  </summary>
  <table class="table table-sm cl-group__table">
    <thead>
      <tr>
        <th>{% trans "Name" %}</th>
        <th>{% trans "Provider" %}</th>
        <th>{% trans "Duration" %}</th>
        <th>{% trans "Purpose" %}</th>
      </tr>
    </thead>
  </table>
</details>
```

### 11.5 JavaScript Translations

For JS strings, use Django's `JavaScriptCatalog` or inline translated strings via data attributes:

**Option A: Data attributes (preferred – simpler)**

```html
<div
  id="cookie-love-banner"
  data-i18n-close="{% trans 'Close' %}"
  data-i18n-show-cookies="{% trans 'Show cookies' %}"
  ...
></div>
```

```javascript
// cookie-love.js reads translations from data attributes
const banner = document.getElementById("cookie-love-banner");
const i18n = {
  close: banner.dataset.i18nClose,
  showCookies: banner.dataset.i18nShowCookies,
};
```

**Option B: Django JavaScript Catalog**

```python
# urls.py
from django.views.i18n import JavaScriptCatalog

urlpatterns = [
    path("cookie-love/jsi18n/", JavaScriptCatalog.as_view(
        packages=["djangocms_cookie_love"]
    ), name="cookie-love-jsi18n"),
]
```

### 11.6 German Translation File (`locale/de/LC_MESSAGES/django.po`)

Key translations shipped with the package:

```po
# djangocms-cookie-love German translations
msgid "Cookie Settings"
msgstr "Cookie-Einstellungen"

msgid "Accept All"
msgstr "Alle akzeptieren"

msgid "Only Essential"
msgstr "Nur Notwendige"

msgid "Settings"
msgstr "Einstellungen"

msgid "Save Preferences"
msgstr "Einstellungen speichern"

msgid "Privacy Policy"
msgstr "Datenschutzerklärung"

msgid "Imprint"
msgstr "Impressum"

msgid "Always Active"
msgstr "Immer aktiv"

msgid "Name"
msgstr "Name"

msgid "Provider"
msgstr "Anbieter"

msgid "Duration"
msgstr "Dauer"

msgid "Purpose"
msgstr "Zweck"

msgid "Cookie Consent Configuration"
msgstr "Cookie-Einwilligungs-Konfiguration"

msgid "Cookie Group"
msgstr "Cookie-Gruppe"

msgid "Cookie Groups"
msgstr "Cookie-Gruppen"

msgid "Consent Version"
msgstr "Einwilligungs-Version"

msgid "User Consent"
msgstr "Nutzer-Einwilligung"

msgid "Required"
msgstr "Erforderlich"

msgid "Bottom Bar"
msgstr "Leiste unten"

msgid "Top Bar"
msgstr "Leiste oben"

msgid "Center Modal"
msgstr "Zentriertes Modal"

msgid "Main text displayed in the cookie banner"
msgstr "Haupttext der im Cookie-Banner angezeigt wird"

msgid "Link to privacy policy page"
msgstr "Link zur Datenschutzerklärung"

msgid "Link to imprint/legal notice page"
msgstr "Link zum Impressum"

msgid "Required groups cannot be deactivated (e.g. Essential)"
msgstr "Erforderliche Gruppen können nicht deaktiviert werden (z.B. Notwendige)"

msgid "What changed in this version"
msgstr "Was hat sich in dieser Version geändert"

msgid "If True, all users must re-consent"
msgstr "Wenn aktiviert, müssen alle Nutzer erneut einwilligen"

msgid "Banner – Accept All"
msgstr "Banner – Alle akzeptieren"

msgid "Banner – Reject Optional"
msgstr "Banner – Optionale ablehnen"

msgid "Settings Modal"
msgstr "Einstellungs-Dialog"

msgid "Close"
msgstr "Schließen"

msgid "Show cookies"
msgstr "Cookies anzeigen"
```

### 11.7 Generate & Compile Messages

```bash
# Extract translatable strings
cd djangocms_cookie_love
django-admin makemessages -l de -l en

# After translating, compile
django-admin compilemessages
```

### 11.8 MANIFEST.in Update

Ensure locale files are included in the package:

```
recursive-include djangocms_cookie_love/locale *
```

## Notes

- **Model field defaults** (like button labels) use `gettext_lazy` so they are translated at runtime based on active language
- **Admin interface** is automatically translated via Django's built-in admin translations
- **User-entered content** (e.g. custom banner text) is NOT auto-translated – the admin enters text in their site's language. For multi-language sites with Django CMS, the CMS page translation system handles this
- Additional languages can be added by the user via standard Django `makemessages`

## Verification

- [ ] `makemessages -l de` extracts all strings
- [ ] `compilemessages` produces `.mo` files without errors
- [ ] Banner shows German text when `LANGUAGE_CODE = "de"`
- [ ] Banner shows English text when `LANGUAGE_CODE = "en"`
- [ ] Admin interface labels are translated
- [ ] Model verbose names are translated
- [ ] Template static strings are translated
- [ ] JavaScript strings are accessible in both languages
- [ ] Package ships with compiled `.mo` files for de and en
