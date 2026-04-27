"""Cookie consent middleware."""

from .constants import COOKIE_NAME
from .models import DiscoveredCookie, UserConsent, get_configured_cookie_names


class CookieConsentMiddleware:
    """
    Check the user's cookie consent status on each request.

    Sets on ``request``:

    - ``cookie_consent`` – *UserConsent* instance or *None*
    - ``cookie_consent_required`` – *True* if the banner should be shown
    - ``cookie_consent_groups`` – list of accepted group slugs
    - ``cookie_consent_cookies`` – list of accepted cookie slugs (``group_slug:cookie_slug``)

    Add to ``MIDDLEWARE`` **after** ``SessionMiddleware``::

        MIDDLEWARE = [
            ...
            "djangocms_cookie_love.middleware.CookieConsentMiddleware",
        ]
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        self._process_consent(request)
        return self.get_response(request)

    def _process_consent(self, request):
        """Populate consent attributes on the request."""
        request.cookie_consent = None
        request.cookie_consent_required = True
        request.cookie_consent_groups = []
        request.cookie_consent_cookies = []

        consent_id = request.COOKIES.get(COOKIE_NAME)
        if not consent_id:
            return

        consent = UserConsent.get_by_consent_id(consent_id)
        if not consent:
            return

        if not consent.is_valid():
            return  # Version outdated – show banner again

        request.cookie_consent = consent
        request.cookie_consent_required = False
        request.cookie_consent_groups = list(consent.accepted_groups.values_list("slug", flat=True))
        request.cookie_consent_cookies = consent.get_accepted_cookie_slugs()


class CookieDiscoveryMiddleware:
    """
    Optional middleware. Compares ``Set-Cookie`` headers on the outgoing
    response against the configured cookie catalog and records any unknown
    name as a :class:`DiscoveredCookie`.

    This catches every cookie the Django app itself sets (including
    ``HttpOnly`` ones). It does **not** see cookies set by client-side JS or
    by third parties — use the ``discover_cookies`` management command from
    ``djangocms_cookie_love.contrib.playwright`` for those.

    Add **after** ``CookieConsentMiddleware`` in production-mirroring
    environments only — it adds one DB read (cached) and at most one DB write
    per response that sets an unknown cookie::

        MIDDLEWARE = [
            ...
            "djangocms_cookie_love.middleware.CookieConsentMiddleware",
            "djangocms_cookie_love.middleware.CookieDiscoveryMiddleware",
        ]

    Cookie *values* are never stored.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._record_unknown(request, response)
        except Exception:
            # Discovery must never break the response cycle.
            pass
        return response

    def _record_unknown(self, request, response):
        cookies = getattr(response, "cookies", None)
        if not cookies:
            return
        configured = get_configured_cookie_names()
        for name in cookies.keys():
            if name in configured:
                continue
            DiscoveredCookie.record(
                name=name,
                source="server",
                path=request.path,
                user_agent=request.META.get("HTTP_USER_AGENT", ""),
            )
