"""API views for cookie consent."""

import json

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect

from .constants import (
    COOKIE_DURATION,
    COOKIE_HTTPONLY,
    COOKIE_NAME,
    COOKIE_SAMESITE,
    COOKIE_SECURE,
)
from .models import Cookie, CookieConsentConfig, CookieGroup, UserConsent
from .utils import get_client_ip, hash_ip

# ---------------------------------------------------------------------------
# GET /cookie-love/api/config/
# ---------------------------------------------------------------------------


def config_view(request):
    """Return the active banner configuration as JSON."""
    if request.method != "GET":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    config = CookieConsentConfig.get_active()
    if not config:
        return JsonResponse({"error": "No active configuration"}, status=404)

    current_version = config.get_current_version()
    groups = config.cookie_groups.all().prefetch_related("cookie_items").order_by("order")

    data = {
        "title": str(config.title),
        "description": str(config.description),
        "privacy_policy_url": config.privacy_policy_url,
        "imprint_url": config.imprint_url,
        "position": config.position,
        "buttons": {
            "accept_all": str(config.accept_all_label),
            "reject_all": str(config.reject_all_label),
            "settings": str(config.settings_label),
            "save": str(config.save_label),
        },
        "version": current_version.version if current_version else "0.0",
        "cookie_groups": [
            {
                "slug": group.slug,
                "name": str(group.name),
                "description": str(group.description),
                "is_required": group.is_required,
                "cookies": [
                    {
                        "slug": cookie.slug,
                        "name": cookie.name,
                        "provider": cookie.provider,
                        "duration": cookie.duration,
                        "purpose": cookie.purpose,
                        "is_required": cookie.is_required,
                    }
                    for cookie in group.cookie_items.all().order_by("order", "name")
                ]
                or (group.cookies or []),
            }
            for group in groups
        ],
    }
    return JsonResponse(data)


# ---------------------------------------------------------------------------
# GET/POST /cookie-love/api/consent/
# ---------------------------------------------------------------------------


@csrf_protect
def consent_view(request):
    """
    GET  – Return current consent status for this user (via cookie).
    POST – Save a new consent decision.
    """
    if request.method == "GET":
        return _get_consent_status(request)
    elif request.method == "POST":
        return _save_consent(request)
    return JsonResponse({"error": "Method not allowed"}, status=405)


def _get_consent_status(request):
    """Return the user's current consent status."""
    consent_id = request.COOKIES.get(COOKIE_NAME)
    if not consent_id:
        return JsonResponse({"has_consent": False, "requires_consent": True, "reason": "no_consent"})

    consent = UserConsent.get_by_consent_id(consent_id)
    if not consent:
        return JsonResponse({"has_consent": False, "requires_consent": True, "reason": "no_consent"})

    is_valid = consent.is_valid()
    return JsonResponse(
        {
            "has_consent": True,
            "consent_id": str(consent.consent_id),
            "version": consent.version.version,
            "accepted_groups": list(consent.accepted_groups.values_list("slug", flat=True)),
            "accepted_cookies": consent.get_accepted_cookie_slugs(),
            "is_current_version": is_valid,
            **({} if is_valid else {"requires_consent": True, "reason": "version_outdated"}),
        }
    )


def _save_consent(request):
    """Create a new UserConsent from the submitted data."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    accepted_slugs = data.get("accepted_groups", [])
    accepted_cookie_refs = data.get("accepted_cookies", [])
    consent_method = data.get("consent_method", "")

    # Validate consent_method
    valid_methods = [choice[0] for choice in UserConsent.CONSENT_METHOD_CHOICES]
    if consent_method not in valid_methods:
        return JsonResponse(
            {"error": f"Invalid consent_method. Must be one of: {', '.join(valid_methods)}"},
            status=400,
        )

    # Validate accepted_groups
    if not isinstance(accepted_slugs, list):
        return JsonResponse({"error": "accepted_groups must be a list of slugs"}, status=400)

    # Validate accepted_cookies
    if not isinstance(accepted_cookie_refs, list):
        return JsonResponse(
            {"error": "accepted_cookies must be a list of 'group_slug:cookie_slug' strings"},
            status=400,
        )

    config = CookieConsentConfig.get_active()
    if not config:
        return JsonResponse({"error": "No active configuration"}, status=404)

    current_version = config.get_current_version()
    if not current_version:
        return JsonResponse({"error": "No published version"}, status=404)

    # Validate slugs against existing groups
    valid_groups = CookieGroup.objects.filter(config=config, slug__in=accepted_slugs)
    valid_slugs = set(valid_groups.values_list("slug", flat=True))
    invalid_slugs = set(accepted_slugs) - valid_slugs
    if invalid_slugs:
        return JsonResponse({"error": f"Unknown cookie groups: {', '.join(invalid_slugs)}"}, status=400)

    # Always include required groups
    required_groups = CookieGroup.objects.filter(config=config, is_required=True)
    all_groups = (valid_groups | required_groups).distinct()

    # Resolve individual cookie references (format: "group_slug:cookie_slug")
    individual_cookies = Cookie.objects.none()
    if accepted_cookie_refs:
        from django.db.models import Q

        cookie_q = Q()
        for ref in accepted_cookie_refs:
            if ":" in ref:
                group_slug, cookie_slug = ref.split(":", 1)
                cookie_q |= Q(group__slug=group_slug, slug=cookie_slug)
        if cookie_q:
            individual_cookies = Cookie.objects.filter(cookie_q, group__config=config)

    # Collect all accepted cookies:
    # 1. All cookies from fully accepted groups
    # 2. Individually selected cookies
    # 3. All required cookies (from required groups)
    group_cookies = Cookie.objects.filter(group__in=all_groups)
    required_cookies = Cookie.objects.filter(group__in=required_groups)
    all_cookies = (group_cookies | individual_cookies | required_cookies).distinct()

    consent = UserConsent.objects.create(
        version=current_version,
        ip_hash=hash_ip(get_client_ip(request)),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        consent_method=consent_method,
    )
    consent.accepted_groups.set(all_groups)
    consent.accepted_cookies.set(all_cookies)

    response = JsonResponse(
        {
            "consent_id": str(consent.consent_id),
            "version": current_version.version,
            "accepted_groups": list(all_groups.values_list("slug", flat=True)),
            "accepted_cookies": consent.get_accepted_cookie_slugs(),
            "consent_given_at": consent.consent_given_at.isoformat(),
        },
        status=201,
    )

    # Set consent cookie
    response.set_cookie(
        COOKIE_NAME,
        str(consent.consent_id),
        max_age=COOKIE_DURATION * 86400,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        httponly=COOKIE_HTTPONLY,
    )

    return response


# ---------------------------------------------------------------------------
# POST /cookie-love/api/consent/revoke/
# ---------------------------------------------------------------------------


@csrf_protect
def revoke_view(request):
    """Revoke optional consent — create new consent with only essential groups."""
    if request.method != "POST":
        return JsonResponse({"error": "Method not allowed"}, status=405)

    config = CookieConsentConfig.get_active()
    if not config:
        return JsonResponse({"error": "No active configuration"}, status=404)

    current_version = config.get_current_version()
    if not current_version:
        return JsonResponse({"error": "No published version"}, status=404)

    # Create new consent with only essential groups and their cookies
    essential_groups = CookieGroup.objects.filter(config=config, is_required=True)
    essential_cookies = Cookie.objects.filter(group__in=essential_groups)

    consent = UserConsent.objects.create(
        version=current_version,
        ip_hash=hash_ip(get_client_ip(request)),
        user_agent=request.META.get("HTTP_USER_AGENT", ""),
        consent_method="revoke",
    )
    consent.accepted_groups.set(essential_groups)
    consent.accepted_cookies.set(essential_cookies)

    response = JsonResponse(
        {
            "consent_id": str(consent.consent_id),
            "accepted_groups": list(essential_groups.values_list("slug", flat=True)),
            "revoked_at": consent.consent_given_at.isoformat(),
        }
    )

    # Update consent cookie
    response.set_cookie(
        COOKIE_NAME,
        str(consent.consent_id),
        max_age=COOKIE_DURATION * 86400,
        secure=COOKIE_SECURE,
        samesite=COOKIE_SAMESITE,
        httponly=COOKIE_HTTPONLY,
    )

    return response
