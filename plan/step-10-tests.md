# Step 10 – Tests

## Goal

Comprehensive test suite covering models, views, CMS plugin, middleware, and GDPR compliance requirements.

## Test Configuration

### `tests/settings.py`

```python
SECRET_KEY = "test-secret-key-not-for-production"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.admin",
    "cms",
    "menus",
    "treebeard",
    "djangocms_cookie_love",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "djangocms_cookie_love.middleware.CookieConsentMiddleware",
]

ROOT_URLCONF = "tests.urls"
COOKIE_LOVE_IP_SALT = "test-salt"
COOKIE_LOVE_COOKIE_NAME = "cookie_love_consent"
COOKIE_LOVE_COOKIE_DURATION = 365
```

### `tests/conftest.py`

```python
import pytest
from djangocms_cookie_love.models import (
    CookieConsentConfig, CookieGroup, ConsentVersion
)


@pytest.fixture
def config():
    return CookieConsentConfig.objects.create(
        title="Test Cookie Banner",
        description="We use cookies for testing.",
        privacy_policy_url="https://example.com/privacy",
        imprint_url="https://example.com/imprint",
        is_active=True,
    )


@pytest.fixture
def essential_group(config):
    return CookieGroup.objects.create(
        config=config,
        name="Essential",
        slug="essential",
        description="Essential cookies",
        is_required=True,
        is_default_enabled=True,
        order=0,
    )


@pytest.fixture
def analytics_group(config):
    return CookieGroup.objects.create(
        config=config,
        name="Analytics",
        slug="analytics",
        description="Analytics cookies",
        is_required=False,
        is_default_enabled=False,
        order=1,
    )


@pytest.fixture
def version(config):
    return ConsentVersion.objects.create(
        config=config,
        version="1.0",
        change_description="Initial version",
        requires_reconsent=False,
        snapshot=config.create_snapshot(),
    )
```

## Test Files

### `test_models.py`

```python
class TestCookieConsentConfig:
    def test_create_config(self, config)
    def test_singleton_enforcement(self, config)
    def test_get_active(self, config)
    def test_get_active_returns_none_when_inactive(self, config)
    def test_create_snapshot(self, config, essential_group, analytics_group)

class TestCookieGroup:
    def test_create_group(self, essential_group)
    def test_required_group_validation(self, config)
    def test_default_enabled_only_for_required(self, config)
    def test_ordering(self, essential_group, analytics_group)
    def test_cookies_json_field(self, config)

class TestConsentVersion:
    def test_create_version(self, version)
    def test_version_uniqueness(self, config, version)
    def test_snapshot_content(self, version)
    def test_get_current_version(self, config, version)
    def test_requires_reconsent(self, config)

class TestUserConsent:
    def test_create_consent(self, version, essential_group)
    def test_consent_id_is_uuid(self)
    def test_accepted_groups(self, version, essential_group, analytics_group)
    def test_ip_hash_stored(self, version)
    def test_consent_immutability_concept(self)
```

### `test_views.py`

```python
class TestConsentConfigAPI:
    def test_get_config(self, client, config, essential_group)
    def test_get_config_no_active(self, client)
    def test_config_includes_groups(self, client, config, essential_group, analytics_group)
    def test_config_includes_version(self, client, config, version)

class TestConsentAPI:
    def test_post_consent(self, client, config, version, essential_group)
    def test_post_consent_sets_cookie(self, client, config, version, essential_group)
    def test_get_consent_status(self, client, config, version)
    def test_get_consent_no_cookie(self, client)
    def test_get_consent_outdated_version(self, client, config, version)
    def test_invalid_group_slugs(self, client, config, version)

class TestConsentRevokeAPI:
    def test_revoke_consent(self, client, config, version)
    def test_revoke_keeps_essential(self, client, config, version, essential_group)
```

### `test_middleware.py`

```python
class TestCookieConsentMiddleware:
    def test_no_consent_cookie(self, rf, config)
    def test_valid_consent(self, rf, config, version)
    def test_invalid_consent_id(self, rf, config)
    def test_outdated_version_requires_reconsent(self, rf, config)
    def test_outdated_version_no_reconsent(self, rf, config)
    def test_consent_groups_populated(self, rf, config, version)
    def test_no_active_config(self, rf)
```

### `test_plugins.py`

```python
class TestCookieConsentPlugin:
    def test_plugin_registered(self)
    def test_plugin_render(self, config, essential_group)
    def test_plugin_render_no_config(self)
    def test_template_tag(self, config, essential_group)
```

### `test_gdpr.py` (GDPR-specific compliance tests)

```python
class TestGDPRCompliance:
    def test_no_optional_cookies_preselected(self, config, analytics_group)
    def test_required_group_cannot_be_default_disabled(self)
    def test_optional_group_cannot_be_default_enabled(self, config)
    def test_ip_is_hashed(self, version)
    def test_consent_records_immutable(self)
    def test_version_change_forces_reconsent(self, config, version)
    def test_privacy_links_present(self, config)
    def test_reject_option_available(self, config)
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=djangocms_cookie_love --cov-report=html

# Run specific test file
pytest tests/test_models.py

# Run specific test class
pytest tests/test_models.py::TestCookieConsentConfig

# Run with verbose output
pytest -v
```

## Coverage Target

- **Minimum 90%** code coverage
- **100%** on models and GDPR compliance logic
- **100%** on API views
- **90%+** on middleware and plugin

## Verification

- [ ] All tests pass: `pytest` exits with 0
- [ ] Coverage meets minimum threshold
- [ ] GDPR compliance tests all pass
- [ ] No Django deprecation warnings in test output
- [ ] Tests run on SQLite in-memory (fast CI)
- [ ] Test fixtures provide clean, reusable test data
