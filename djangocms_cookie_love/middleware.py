"""Cookie consent middleware."""

from .constants import COOKIE_NAME
from .models import UserConsent


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
