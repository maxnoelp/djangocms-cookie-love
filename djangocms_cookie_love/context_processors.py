"""Context processors for cookie consent."""


def cookie_consent(request):
    """
    Make cookie consent data available in all templates.

    Adds to the template context:

    - ``cookie_consent`` – *UserConsent* instance or *None*
    - ``cookie_consent_required`` – *True* if consent banner should show
    - ``cookie_consent_groups`` – list of accepted group slugs
    - ``cookie_consent_cookies`` – list of accepted cookie slugs (``group_slug:cookie_slug``)

    Add to ``TEMPLATES["OPTIONS"]["context_processors"]``::

        "djangocms_cookie_love.context_processors.cookie_consent",
    """
    return {
        "cookie_consent": getattr(request, "cookie_consent", None),
        "cookie_consent_required": getattr(request, "cookie_consent_required", True),
        "cookie_consent_groups": getattr(request, "cookie_consent_groups", []),
        "cookie_consent_cookies": getattr(request, "cookie_consent_cookies", []),
    }
