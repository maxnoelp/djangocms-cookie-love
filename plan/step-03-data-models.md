# Step 03 – Data Models

## Goal

Define the core data models for cookie consent management with versioning support.

## Models

### 3.1 `CookieConsentConfig` – Global Banner Configuration (Singleton)

The central configuration model. Only one active config per site.

```python
class CookieConsentConfig(models.Model):
    title = models.CharField(max_length=255, default="Cookie Settings")
    description = models.TextField(
        help_text="Main text displayed in the cookie banner"
    )
    privacy_policy_url = models.URLField(
        blank=True,
        help_text="Link to privacy policy page"
    )
    imprint_url = models.URLField(
        blank=True,
        help_text="Link to imprint/legal notice page"
    )

    # Design options
    POSITION_CHOICES = [
        ("bottom", "Bottom Bar"),
        ("top", "Top Bar"),
        ("center", "Center Modal"),
    ]
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default="bottom",
    )

    # Button labels (customizable)
    accept_all_label = models.CharField(max_length=50, default="Accept All")
    reject_all_label = models.CharField(max_length=50, default="Only Essential")
    settings_label = models.CharField(max_length=50, default="Settings")
    save_label = models.CharField(max_length=50, default="Save Preferences")

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Key behaviors:**

- Singleton enforcement via `save()` override or custom manager
- `get_active()` class method returns the current active config
- `__str__` returns title

### 3.2 `CookieGroup` – Cookie Categories

Groups cookies into categories for granular user control.

```python
class CookieGroup(models.Model):
    config = models.ForeignKey(
        CookieConsentConfig,
        on_delete=models.CASCADE,
        related_name="cookie_groups",
    )
    name = models.CharField(max_length=100)  # e.g. "Essential", "Analytics", "Marketing"
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(
        help_text="Explains to the user what this cookie group does"
    )
    is_required = models.BooleanField(
        default=False,
        help_text="Required groups cannot be deactivated (e.g. Essential)"
    )
    is_default_enabled = models.BooleanField(
        default=False,
        help_text="Pre-selected state (only for required groups per GDPR)"
    )
    order = models.PositiveIntegerField(default=0)

    # Cookie details as JSON for flexibility
    cookies = models.JSONField(
        default=list,
        blank=True,
        help_text='List of cookies: [{"name": "...", "provider": "...", "duration": "...", "purpose": "..."}]'
    )
```

**Default groups created on first setup:**

1. **Essential** (`essential`) – required=True, default_enabled=True
2. **Analytics** (`analytics`) – required=False, default_enabled=False
3. **Marketing** (`marketing`) – required=False, default_enabled=False
4. **Preferences** (`preferences`) – required=False, default_enabled=False

### 3.3 `ConsentVersion` – Version Tracking

Tracks changes to the cookie configuration for GDPR compliance.

```python
class ConsentVersion(models.Model):
    config = models.ForeignKey(
        CookieConsentConfig,
        on_delete=models.CASCADE,
        related_name="versions",
    )
    version = models.CharField(max_length=20)  # Semantic: "1.0", "1.1", "2.0"
    change_description = models.TextField(
        help_text="What changed in this version"
    )
    requires_reconsent = models.BooleanField(
        default=False,
        help_text="If True, all users must re-consent"
    )
    published_at = models.DateTimeField(auto_now_add=True)

    # Snapshot of config at time of publishing
    snapshot = models.JSONField(
        help_text="Complete snapshot of config and cookie groups"
    )

    class Meta:
        ordering = ["-published_at"]
        unique_together = [("config", "version")]
```

**Key behaviors:**

- `snapshot` is auto-generated from current config state on creation
- `get_current()` returns the latest published version
- When `requires_reconsent=True`, all existing consents become invalid

### 3.4 `UserConsent` – Consent Records

Stores individual user consent decisions for audit trail.

```python
class UserConsent(models.Model):
    consent_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
    )
    version = models.ForeignKey(
        ConsentVersion,
        on_delete=models.PROTECT,
        related_name="user_consents",
    )
    ip_hash = models.CharField(
        max_length=64,
        help_text="SHA-256 hash of the user's IP address"
    )
    user_agent = models.TextField(blank=True)
    accepted_groups = models.ManyToManyField(
        CookieGroup,
        blank=True,
        related_name="consents",
    )

    CONSENT_METHOD_CHOICES = [
        ("banner_accept_all", "Banner – Accept All"),
        ("banner_reject", "Banner – Reject Optional"),
        ("settings", "Settings Modal"),
        ("api", "API"),
    ]
    consent_method = models.CharField(
        max_length=30,
        choices=CONSENT_METHOD_CHOICES,
    )

    consent_given_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-consent_given_at"]
```

**Key behaviors:**

- `ip_hash` is generated via `utils.hash_ip(ip_address)`
- `consent_id` is stored in a cookie on the client side
- Consent records are never deleted (audit trail)
- `on_delete=PROTECT` prevents accidental version deletion

## Relationships

```
CookieConsentConfig (1) ──── (N) CookieGroup
CookieConsentConfig (1) ──── (N) ConsentVersion
ConsentVersion      (1) ──── (N) UserConsent
UserConsent         (N) ──── (N) CookieGroup (accepted_groups)
```

## Migrations

- `0001_initial.py` – Create all four models
- Consider data migration for default cookie groups

## Verification

- [ ] All models can be created and saved
- [ ] Singleton enforcement works for CookieConsentConfig
- [ ] ConsentVersion snapshot is auto-generated
- [ ] UserConsent correctly stores accepted groups
- [ ] IP hashing produces consistent results
- [ ] `makemigrations` generates clean migration
- [ ] `migrate` runs without errors
