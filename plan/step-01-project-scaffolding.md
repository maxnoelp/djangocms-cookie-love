# Step 01 – Project Scaffolding

## Goal

Set up the Python package structure with modern build tooling, documentation stubs, and version control configuration.

## Tasks

### 1.1 Create `pyproject.toml`

PEP 621 compliant build configuration:

```toml
[build-system]
requires = ["setuptools>=68.0", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "djangocms-cookie-love"
version = "0.1.0"
description = "A GDPR-compliant cookie consent banner plugin for Django CMS"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Your Name", email = "your@email.com"},
]
classifiers = [
    "Development Status :: 3 - Alpha",
    "Framework :: Django",
    "Framework :: Django :: 4.2",
    "Framework :: Django :: 5.0",
    "Framework :: Django CMS",
    "Framework :: Django CMS :: 4.0",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Internet :: WWW/HTTP",
    "Natural Language :: English",
    "Natural Language :: German",
]
dependencies = [
    "django>=4.2",
    "django-cms>=4.0",
]

[project.optional-dependencies]
dev = [
    "pytest",
    "pytest-django",
    "pytest-cov",
    "ruff",
    "pre-commit",
]

[project.urls]
Homepage = "https://github.com/yourname/djangocms-cookie-love"
Repository = "https://github.com/yourname/djangocms-cookie-love"
Changelog = "https://github.com/yourname/djangocms-cookie-love/blob/main/CHANGELOG.md"

[tool.setuptools.packages.find]
include = ["djangocms_cookie_love*"]

[tool.ruff]
line-length = 120
target-version = "py310"

[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "tests.settings"
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
```

### 1.2 Create `setup.cfg`

```ini
[metadata]
long_description = file: README.md
long_description_content_type = text/markdown

[options]
include_package_data = True
```

### 1.3 Create `MANIFEST.in`

```
include LICENSE
include README.md
include CHANGELOG.md
recursive-include djangocms_cookie_love/templates *
recursive-include djangocms_cookie_love/static *
recursive-include djangocms_cookie_love/locale *
```

### 1.4 Create `.gitignore`

Standard Python/Django .gitignore with:

- `__pycache__/`, `*.pyc`, `*.pyo`
- `.venv/`, `venv/`, `env/`
- `*.egg-info/`, `dist/`, `build/`
- `.tox/`, `.pytest_cache/`, `.coverage`
- `db.sqlite3`
- `.env`
- `node_modules/`
- `.idea/`, `.vscode/`

### 1.5 Create `README.md`

Basic README with:

- Package name and description
- Installation instructions (`pip install djangocms-cookie-love`)
- Quick start guide
- Feature list
- License

### 1.6 Create `LICENSE`

MIT License

### 1.7 Create `CHANGELOG.md`

Initial changelog entry for v0.1.0 (Unreleased)

## Verification

- [ ] `pip install -e .` installs successfully
- [ ] Package structure is recognized by setuptools
- [ ] `git init && git add .` works with .gitignore
