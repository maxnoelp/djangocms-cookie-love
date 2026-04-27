# Test Coverage Report

> Generated: 2026-02-17 | Python 3.12.3 | Django 6.0.2 | pytest + pytest-cov

## Summary

| Metric               | Value                               |
| -------------------- | ----------------------------------- |
| **Total tests**      | 116                                 |
| **Passing**          | 116 (100%)                          |
| **Overall coverage** | **93%** (441 statements, 29 missed) |

## Coverage by Module

| Module                                     | Statements | Missed | Coverage | Missing Lines          |
| ------------------------------------------ | ---------- | ------ | -------- | ---------------------- |
| `__init__.py`                              | 2          | 0      | 100%     | –                      |
| `admin.py`                                 | 71         | 0      | 100%     | –                      |
| `apps.py`                                  | 6          | 0      | 100%     | –                      |
| `contrib/cms/cms_plugins.py`               | 16         | 4      | 75%      | 23–32                  |
| `constants.py`                             | 7          | 0      | 100%     | –                      |
| `context_processors.py`                    | 2          | 0      | 100%     | –                      |
| `forms.py`                                 | 13         | 0      | 100%     | –                      |
| `middleware.py`                            | 25         | 0      | 100%     | –                      |
| `models.py`                                | 127        | 2      | 98%      | 317, 325               |
| `templatetags/cookie_love_tags.py`         | 19         | 4      | 79%      | 22–31                  |
| `urls.py`                                  | 4          | 0      | 100%     | –                      |
| `utils.py`                                 | 10         | 1      | 90%      | 24                     |
| `views.py`                                 | 97         | 5      | 95%      | 88, 136, 140, 151, 235 |
| **Migrations**                             |            |        |          |                        |
| `0001_initial.py`                          | 7          | 0      | 100%     | –                      |
| `0002_default_cookie_groups.py`            | 8          | 1      | 88%      | 17                     |
| `0003_alter_userconsent_consent_method.py` | 4          | 0      | 100%     | –                      |
| `0004_cookie_model.py`                     | 23         | 12     | 48%      | 18–29, 43              |

## Tests by File

| Test File                    | Tests | What It Covers                                                          |
| ---------------------------- | ----- | ----------------------------------------------------------------------- |
| `test_models.py`             | 45    | All 5 models, field validation, relationships, methods, constraints     |
| `test_views.py`              | 26    | API endpoints (config, consent, revoke), CSRF, input validation         |
| `test_gdpr.py`               | 15    | GDPR/TTDSG compliance: opt-in, granularity, revocability, versioning    |
| `test_admin.py`              | 9     | Admin permissions, singleton enforcement, CSV export, snapshot creation |
| `test_middleware.py`         | 8     | Consent middleware, request attributes, version validation              |
| `test_forms.py`              | 6     | Config form validation, formset constraints                             |
| `test_plugins.py`            | 5     | CMS plugin rendering, template tag output                               |
| `test_context_processors.py` | 2     | Context processor with/without consent                                  |

## Uncovered Areas

| Area                                     | Reason                                                                                 |
| ---------------------------------------- | -------------------------------------------------------------------------------------- |
| `contrib/cms/cms_plugins.py` (75%)       | CMS plugin `render()` method requires full CMS page rendering context                  |
| `templatetags/cookie_love_tags.py` (79%) | Template tags that render full HTML blocks (tested indirectly via plugin tests)        |
| `migrations/0004_cookie_model.py` (48%)  | Data migration reverse function and migration operations (standard Django boilerplate) |
| `views.py` (95%)                         | Edge cases: missing config on GET, cookie ref parsing edge cases                       |
| `models.py` (98%)                        | Two fallback return paths in `create_snapshot()`                                       |

## Running Tests

### Linux / macOS

```bash
# Run all tests
.venv/bin/python -m pytest tests/ -v

# Run with coverage
.venv/bin/python -m pytest tests/ --cov=djangocms_cookie_love --cov-report=term-missing

# Run a specific test file
.venv/bin/python -m pytest tests/test_models.py -v

# Run a specific test
.venv/bin/python -m pytest tests/test_models.py::TestCookieModel::test_unique_together -v
```

### Windows

```powershell
# Run all tests
.venv\Scripts\python -m pytest tests/ -v

# Run with coverage
.venv\Scripts\python -m pytest tests/ --cov=djangocms_cookie_love --cov-report=term-missing

# Run a specific test file
.venv\Scripts\python -m pytest tests/test_models.py -v

# Run a specific test
.venv\Scripts\python -m pytest tests/test_models.py::TestCookieModel::test_unique_together -v
```
