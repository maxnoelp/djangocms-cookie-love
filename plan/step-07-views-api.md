# Step 07 – Views & API

## Goal

Provide REST-like API endpoints for the JavaScript frontend to save, retrieve, and revoke cookie consent.

## Endpoints

### 7.1 `GET /cookie-love/api/config/`

Returns the current active banner configuration as JSON.

**Response:**

```json
{
  "title": "Cookie Settings",
  "description": "We use cookies to improve your experience...",
  "privacy_policy_url": "/privacy/",
  "imprint_url": "/imprint/",
  "position": "bottom",
  "buttons": {
    "accept_all": "Accept All",
    "reject_all": "Only Essential",
    "settings": "Settings",
    "save": "Save Preferences"
  },
  "version": "1.0",
  "cookie_groups": [
    {
      "slug": "essential",
      "name": "Essential",
      "description": "Required for the website to function properly.",
      "is_required": true,
      "cookies": [
        {
          "name": "sessionid",
          "provider": "This website",
          "duration": "Session",
          "purpose": "Session management"
        }
      ]
    },
    {
      "slug": "analytics",
      "name": "Analytics",
      "description": "Help us understand how visitors use our site.",
      "is_required": false,
      "cookies": [
        {
          "name": "_ga",
          "provider": "Google",
          "duration": "2 years",
          "purpose": "Distinguish users"
        }
      ]
    }
  ]
}
```

**Implementation:**

```python
class ConsentConfigAPIView(View):
    def get(self, request):
        config = CookieConsentConfig.get_active()
        if not config:
            return JsonResponse({"error": "No active config"}, status=404)

        current_version = config.get_current_version()
        data = {
            "title": config.title,
            "description": config.description,
            "privacy_policy_url": config.privacy_policy_url,
            "imprint_url": config.imprint_url,
            "position": config.position,
            "buttons": {
                "accept_all": config.accept_all_label,
                "reject_all": config.reject_all_label,
                "settings": config.settings_label,
                "save": config.save_label,
            },
            "version": current_version.version if current_version else "0.0",
            "cookie_groups": [...],
        }
        return JsonResponse(data)
```

### 7.2 `POST /cookie-love/api/consent/`

Save user's consent decision.

**Request Body:**

```json
{
  "accepted_groups": ["essential", "analytics"],
  "consent_method": "banner_accept_all"
}
```

**Response:**

```json
{
  "consent_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "1.0",
  "accepted_groups": ["essential", "analytics"],
  "consent_given_at": "2026-02-15T14:30:00Z"
}
```

**Implementation:**

```python
class ConsentAPIView(View):
    def post(self, request):
        data = json.loads(request.body)
        config = CookieConsentConfig.get_active()
        current_version = config.get_current_version()

        consent = UserConsent.objects.create(
            version=current_version,
            ip_hash=hash_ip(get_client_ip(request)),
            user_agent=request.META.get("HTTP_USER_AGENT", ""),
            consent_method=data["consent_method"],
        )

        groups = CookieGroup.objects.filter(slug__in=data["accepted_groups"])
        consent.accepted_groups.set(groups)

        response = JsonResponse({
            "consent_id": str(consent.consent_id),
            "version": current_version.version,
            "accepted_groups": data["accepted_groups"],
            "consent_given_at": consent.consent_given_at.isoformat(),
        })

        # Set consent cookie on client
        response.set_cookie(
            settings.COOKIE_LOVE_COOKIE_NAME,
            str(consent.consent_id),
            max_age=settings.COOKIE_LOVE_COOKIE_DURATION * 86400,
            secure=settings.COOKIE_LOVE_COOKIE_SECURE,
            samesite=settings.COOKIE_LOVE_COOKIE_SAMESITE,
            httponly=True,
        )

        return response
```

### 7.3 `GET /cookie-love/api/consent/`

Retrieve current consent status for the user.

**Response (if consent exists):**

```json
{
  "has_consent": true,
  "consent_id": "550e8400-e29b-41d4-a716-446655440000",
  "version": "1.0",
  "accepted_groups": ["essential", "analytics"],
  "is_current_version": true
}
```

**Response (if no consent / outdated):**

```json
{
    "has_consent": false,
    "requires_consent": true,
    "reason": "no_consent" | "version_outdated"
}
```

### 7.4 `POST /cookie-love/api/consent/revoke/`

Revoke all optional consent (keep only essential).

**Response:**

```json
{
  "consent_id": "new-uuid-here",
  "accepted_groups": ["essential"],
  "revoked_at": "2026-02-15T15:00:00Z"
}
```

## URL Configuration

```python
# urls.py
from django.urls import path
from . import views

app_name = "cookie_love"

urlpatterns = [
    path("api/config/", views.ConsentConfigAPIView.as_view(), name="api-config"),
    path("api/consent/", views.ConsentAPIView.as_view(), name="api-consent"),
    path("api/consent/revoke/", views.ConsentRevokeAPIView.as_view(), name="api-consent-revoke"),
]
```

## Security

- CSRF protection via Django's `@csrf_protect` or CSRF token in JS
- Rate limiting on consent endpoints (optional, via django-ratelimit)
- Input validation on `accepted_groups` slugs
- `consent_method` choices validation

## Verification

- [ ] Config endpoint returns complete banner configuration
- [ ] Consent POST creates UserConsent record with correct data
- [ ] Consent GET returns current consent status
- [ ] Version mismatch correctly detected
- [ ] Revoke endpoint creates new consent with only essential groups
- [ ] CSRF protection works
- [ ] Consent cookie is set correctly
- [ ] Invalid slugs are rejected
