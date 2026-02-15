# Step 04 – GDPR Compliance

## Goal

Ensure full DSGVO/GDPR compliance across all aspects of the cookie consent system.

## Requirements & Implementation

### 4.1 Opt-In by Default

**Requirement:** No optional cookies may be set before explicit user consent.

**Implementation:**

- All non-essential `CookieGroup` entries have `is_default_enabled=False`
- Only groups with `is_required=True` may have `is_default_enabled=True`
- Validation in `CookieGroup.clean()`: reject `is_default_enabled=True` when `is_required=False`
- JavaScript blocks all script tags with `data-cookie-group` attribute until consent is given
- Scripts use `type="text/plain"` and are activated only after consent

```html
<!-- Before consent: blocked -->
<script type="text/plain" data-cookie-group="analytics">
  // Google Analytics code
</script>

<!-- After consent for "analytics": activated by cookie-love.js -->
<script type="text/javascript">
  // Google Analytics code
</script>
```

### 4.2 Granular Control

**Requirement:** Users must be able to choose individual cookie categories.

**Implementation:**

- Settings modal shows each `CookieGroup` with toggle switch
- Required groups are shown but toggle is disabled (always on)
- Each group displays: name, description, list of individual cookies
- "Accept All" and "Only Essential" are convenience buttons
- Users can selectively enable/disable each optional group

### 4.3 Informed Consent

**Requirement:** Users must know what they're consenting to.

**Implementation:**

- Banner shows clear, understandable `description` text
- Each `CookieGroup` has a `description` field
- Cookie details (name, provider, duration, purpose) are shown in settings modal
- Links to privacy policy and imprint are always visible
- No dark patterns: reject button is equally prominent as accept button

### 4.4 Revocable Consent

**Requirement:** Users must be able to withdraw consent at any time.

**Implementation:**

- Persistent "Cookie Settings" link/button (configurable position)
- Reopens settings modal where users can change their preferences
- Changes create a new `UserConsent` record
- Previously set cookies for revoked groups are deleted
- JavaScript provides `CookieLove.openSettings()` API for custom trigger placement

### 4.5 Documented Consent (Audit Trail)

**Requirement:** Website operators must be able to prove that consent was given.

**Implementation:**

- `UserConsent` model stores:
  - Unique `consent_id` (UUID)
  - Which `ConsentVersion` was shown
  - Which `CookieGroup`s were accepted
  - Timestamp (`consent_given_at`)
  - Method of consent (`consent_method`)
  - Hashed IP address (`ip_hash`)
  - User agent string
- Records are immutable (never updated, only new records created)
- `on_delete=PROTECT` on version FK prevents orphaned records

### 4.6 IP Address Handling

**Requirement:** IP addresses are personal data and must be handled carefully.

**Implementation:**

- IPs are hashed with SHA-256 + salt before storage
- Salt is configurable via `COOKIE_LOVE_IP_SALT` setting
- Raw IP is never stored in the database
- Hash allows proof that a specific session gave consent without storing PII

```python
# utils.py
import hashlib
from django.conf import settings

def hash_ip(ip_address: str) -> str:
    salt = getattr(settings, "COOKIE_LOVE_IP_SALT", "cookie-love-default-salt")
    return hashlib.sha256(f"{salt}:{ip_address}".encode()).hexdigest()
```

### 4.7 Versioning & Re-Consent

**Requirement:** When cookie usage changes, users must re-consent.

**Implementation:**

- `ConsentVersion` tracks all changes with snapshots
- When a new version with `requires_reconsent=True` is published:
  - All users see the banner again on next visit
  - Previous consent is not deleted (audit trail preserved)
  - JavaScript checks `version` in stored cookie vs. current version
- Minor text changes (typo fixes) can be versioned without re-consent

### 4.8 No Pre-Selected Optional Cookies

**Requirement:** Optional cookie categories must not be pre-checked.

**Implementation:**

- Model validation: `is_default_enabled=True` only allowed when `is_required=True`
- Frontend: toggle switches for optional groups are OFF by default
- "Accept All" button explicitly sets all toggles to ON (user action)

## Django Settings

```python
# settings.py
COOKIE_LOVE_IP_SALT = "your-secret-salt-here"      # Required for IP hashing
COOKIE_LOVE_COOKIE_NAME = "cookie_love_consent"     # Name of the consent cookie
COOKIE_LOVE_COOKIE_DURATION = 365                    # Days until consent cookie expires
COOKIE_LOVE_COOKIE_SECURE = True                     # Secure flag on consent cookie
COOKIE_LOVE_COOKIE_SAMESITE = "Lax"                  # SameSite policy
```

## Verification

- [ ] No optional cookies are set before consent
- [ ] Users can select individual cookie categories
- [ ] Reject button is equally prominent as accept button
- [ ] Users can reopen settings and change preferences
- [ ] Consent records are complete and immutable
- [ ] IP addresses are hashed, never stored in plain text
- [ ] Re-consent is forced when `requires_reconsent=True` version is published
- [ ] Optional groups are never pre-selected
- [ ] Privacy policy and imprint links are visible in banner
