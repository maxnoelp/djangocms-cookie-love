# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Cookie discovery: `CookieDiscoveryMiddleware` and an optional Playwright crawler
  (`discover_cookies` management command) that record undocumented cookies into
  `DiscoveredCookie` for review.
- Per-cookie-group admin actions on `DiscoveredCookie` to assign discoveries to a
  group (creates a `Cookie` and marks the row resolved).
- `DiscoveredCookie` admin defaults to filtering by *Unresolved*; pick *Resolved*
  or *All* explicitly.
- Plain Django support: `django-cms` is now an optional dependency. Install
  `djangocms-cookie-love[cms]` and add
  `djangocms_cookie_love.contrib.cms.apps.CookieLoveCmsConfig` to
  `INSTALLED_APPS` to enable the **Cookie Consent Banner** plugin. Without the
  extra, the package is fully functional via the existing template tags, admin,
  middleware and API.

### Changed

- **Breaking:** `privacy_policy_page` / `imprint_page` (django CMS `PageField`)
  on `CookieConsentConfig` are replaced by `privacy_policy_path` /
  `imprint_path` (`CharField`). This decouples the package from django CMS at
  runtime. **No automatic data migration is performed**: any existing Page
  references will be dropped on upgrade. Before applying migrations, capture
  the absolute URL of each configured Page and re-enter it into the new
  `*_path` field after upgrade. The standalone `*_url` external links are
  preserved unchanged.

### Fixed

- `DiscoveredCookie.record()` now wraps the `seen_in` read-modify-write in
  `transaction.atomic()` + `select_for_update()` so concurrent observations of
  the same cookie no longer drop per-context increments.

## [0.1.1] - 2026-04-25

### Added

- `setup_example` management command for cross-platform example project setup (replaces bash-only `setup.sh`)
- Automatic `ConsentVersion 1.0` creation when a new `CookieConsentConfig` is saved

### Fixed

- Bootstrap 5.3.3 SRI integrity hash corrected in example base template

### Changed

- Expanded Theming section in README with full CSS custom properties reference, dark mode and corporate style examples, and template override instructions
- Admin Interface section in README now documents automatic version creation and when to create new versions manually

## [0.1.0] - 2026-04-25

### Added

- Initial project scaffolding
- Cookie consent data models (CookieConsentConfig, CookieGroup, ConsentVersion, UserConsent)
- Django CMS plugin and template tag
- Bootstrap 5 cookie banner with settings modal
- GDPR-compliant consent management with versioning
- Admin interface for configuration
- REST API for consent CRUD
- Middleware and context processor
- German and English translations
- Full test suite
