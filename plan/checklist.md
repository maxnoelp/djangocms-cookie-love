# djangocms-cookie-love – Progress Checklist

> Track implementation progress. Check off tasks as they are completed.

---

## Step 01 – Project Scaffolding

- [ ] 1.1 Create `pyproject.toml` (PEP 621)
- [ ] 1.2 Create `setup.cfg`
- [ ] 1.3 Create `MANIFEST.in` (incl. templates, static, locale)
- [ ] 1.4 Create `.gitignore`
- [ ] 1.5 Create `README.md`
- [ ] 1.6 Create `LICENSE` (MIT)
- [ ] 1.7 Create `CHANGELOG.md`
- [ ] **Verify:** `pip install -e .` works

---

## Step 02 – Django App Skeleton

- [ ] 2.1 Create `djangocms_cookie_love/__init__.py`
- [ ] 2.2 Create `djangocms_cookie_love/apps.py`
- [ ] 2.3 Create stub module files (models, admin, views, urls, forms, cms_plugins, middleware, utils, constants)
- [ ] 2.4 Create `templatetags/__init__.py`
- [ ] 2.5 Create `templatetags/cookie_love_tags.py` (stub)
- [ ] 2.6 Create directory structure (migrations, templates, static, locale)
- [ ] **Verify:** `import djangocms_cookie_love` works

---

## Step 03 – Data Models

- [ ] 3.1 `CookieConsentConfig` model (singleton)
- [ ] 3.2 `CookieGroup` model
- [ ] 3.3 `ConsentVersion` model
- [ ] 3.4 `UserConsent` model
- [ ] 3.5 Create initial migration (`0001_initial.py`)
- [ ] 3.6 Data migration for default cookie groups
- [ ] **Verify:** `makemigrations --check` clean, `migrate` runs

---

## Step 04 – GDPR Compliance

- [ ] 4.1 Opt-in by default (no pre-selected optional cookies)
- [ ] 4.2 Granular control (per cookie group)
- [ ] 4.3 Informed consent (descriptions, cookie details)
- [ ] 4.4 Revocable consent (`CookieLove.openSettings()`)
- [ ] 4.5 Documented consent (audit trail via `UserConsent`)
- [ ] 4.6 IP address hashing (`utils.hash_ip()`)
- [ ] 4.7 Versioning & re-consent logic
- [ ] 4.8 Validation: `is_default_enabled` only for `is_required` groups
- [ ] **Verify:** All GDPR requirements met

---

## Step 05 – CMS Plugin

- [ ] 5.1 `CookieConsentPlugin` in `cms_plugins.py`
- [ ] 5.2 Template tag `{% cookie_love_banner %}`
- [ ] 5.3 URL configuration (`urls.py`)
- [ ] **Verify:** Plugin renders on CMS page, template tag works

---

## Step 06 – Admin & Edit Page

- [ ] 6.1 `CookieGroupInline`
- [ ] 6.2 `CookieConsentConfigAdmin` (with singleton enforcement)
- [ ] 6.3 `ConsentVersionAdmin` (snapshot auto-generation)
- [ ] 6.4 `UserConsentAdmin` (read-only, no add/change/delete)
- [ ] 6.5 Admin actions (publish version, export CSV)
- [ ] 6.6 Optional: Frontend edit view (`/cookie-love/edit/`)
- [ ] **Verify:** Admin interface complete and functional

---

## Step 07 – Views & API

- [ ] 7.1 `GET /cookie-love/api/config/` – Banner config
- [ ] 7.2 `POST /cookie-love/api/consent/` – Save consent
- [ ] 7.3 `GET /cookie-love/api/consent/` – Get consent status
- [ ] 7.4 `POST /cookie-love/api/consent/revoke/` – Revoke consent
- [ ] 7.5 CSRF protection
- [ ] 7.6 Input validation
- [ ] **Verify:** All API endpoints respond correctly

---

## Step 08 – Frontend

- [ ] 8.1 `banner.html` template
- [ ] 8.2 `settings_modal.html` template
- [ ] 8.3 `includes/cookie_group.html` template
- [ ] 8.4 `includes/toggle_switch.html` template
- [ ] 8.5 `cookie-love.css` (Bootstrap 5, BEM, CSS custom properties)
- [ ] 8.6 `cookie-love.js` (Vanilla JS, public API, script blocking)
- [ ] 8.7 Accessibility (ARIA, keyboard nav, focus trap)
- [ ] 8.8 Responsive design (mobile-first)
- [ ] **Verify:** Banner + modal work across devices and screen readers

---

## Step 09 – Middleware

- [ ] 9.1 `CookieConsentMiddleware`
- [ ] 9.2 Context processor (`cookie_consent`)
- [ ] 9.3 Documentation for `settings.py` integration
- [ ] **Verify:** `request.cookie_consent_*` attributes set correctly

---

## Step 10 – Tests

- [ ] 10.1 Test settings (`tests/settings.py`)
- [ ] 10.2 Fixtures (`tests/conftest.py`)
- [ ] 10.3 `test_models.py`
- [ ] 10.4 `test_views.py`
- [ ] 10.5 `test_middleware.py`
- [ ] 10.6 `test_plugins.py`
- [ ] 10.7 `test_gdpr.py` (GDPR compliance tests)
- [ ] 10.8 Coverage ≥ 90%
- [ ] **Verify:** `pytest` passes, coverage meets threshold

---

## Step 11 – Internationalization (i18n)

- [ ] 11.1 All model fields use `gettext_lazy` (verbose_name, help_text, defaults)
- [ ] 11.2 All templates use `{% trans %}` / `{% blocktrans %}`
- [ ] 11.3 JavaScript strings available via data attributes
- [ ] 11.4 German translation file (`locale/de/LC_MESSAGES/django.po`)
- [ ] 11.5 English translation file (`locale/en/LC_MESSAGES/django.po`)
- [ ] 11.6 Compile messages (`django-admin compilemessages`)
- [ ] 11.7 `MANIFEST.in` includes locale files
- [ ] **Verify:** Banner shows correct language based on `LANGUAGE_CODE`

---

## Final Release Checklist

- [ ] All steps above completed
- [ ] `pip install -e .` installs without errors
- [ ] `python manage.py makemigrations --check` – no missing migrations
- [ ] `python manage.py migrate` – runs clean
- [ ] `pytest --cov` – all tests pass, coverage ≥ 90%
- [ ] `ruff check .` – no linting errors
- [ ] README.md complete with install + usage docs
- [ ] CHANGELOG.md updated for v0.1.0
- [ ] Package builds: `python -m build`
- [ ] Manual test: banner displays, consent saves, re-consent works
