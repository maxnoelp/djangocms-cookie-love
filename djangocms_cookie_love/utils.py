"""Utility functions for cookie consent."""

import hashlib

from django.conf import settings


def hash_ip(ip_address: str) -> str:
    """
    Hash an IP address with SHA-256 and a configurable salt.
    Returns a 64-character hex string. Never stores the raw IP.
    """
    salt = getattr(settings, "COOKIE_LOVE_IP_SALT", "cookie-love-default-salt")
    return hashlib.sha256(f"{salt}:{ip_address}".encode()).hexdigest()


def get_client_ip(request) -> str:
    """
    Extract the client IP address from a Django request.
    Supports X-Forwarded-For header for reverse proxies.
    """
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")
