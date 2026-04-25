# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
