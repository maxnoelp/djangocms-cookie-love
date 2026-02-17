"""Cookie consent data models."""

import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _


class CookieConsentConfig(models.Model):
    """
    Global cookie consent banner configuration.
    Singleton pattern – only one active config per site.
    """

    title = models.CharField(
        max_length=255,
        default=_("Cookie Settings"),
        verbose_name=_("Title"),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Main text displayed in the cookie banner"),
        default=_(
            "We use cookies to improve your experience on our website. "
            "Some cookies are essential for the website to function, while others "
            "help us understand how you use our site."
        ),
    )
    privacy_policy_url = models.URLField(
        blank=True,
        verbose_name=_("Privacy Policy URL"),
        help_text=_("Link to privacy policy page"),
    )
    imprint_url = models.URLField(
        blank=True,
        verbose_name=_("Imprint URL"),
        help_text=_("Link to imprint/legal notice page"),
    )

    # Design options
    POSITION_CHOICES = [
        ("bottom", _("Bottom Bar")),
        ("top", _("Top Bar")),
        ("center", _("Center Modal")),
    ]
    position = models.CharField(
        max_length=20,
        choices=POSITION_CHOICES,
        default="bottom",
        verbose_name=_("Position"),
    )

    # Button labels (customizable)
    accept_all_label = models.CharField(
        max_length=50,
        default=_("Accept All"),
        verbose_name=_("Accept All Button Label"),
    )
    reject_all_label = models.CharField(
        max_length=50,
        default=_("Only Essential"),
        verbose_name=_("Reject Button Label"),
    )
    settings_label = models.CharField(
        max_length=50,
        default=_("Settings"),
        verbose_name=_("Settings Button Label"),
    )
    save_label = models.CharField(
        max_length=50,
        default=_("Save Preferences"),
        verbose_name=_("Save Button Label"),
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At"),
    )

    class Meta:
        verbose_name = _("Cookie Consent Configuration")
        verbose_name_plural = _("Cookie Consent Configurations")

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Singleton enforcement: deactivate other configs when saving as active
        if self.is_active:
            CookieConsentConfig.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @classmethod
    def get_active(cls):
        """Return the currently active configuration, or None."""
        return cls.objects.filter(is_active=True).first()

    def get_current_version(self):
        """Return the latest published ConsentVersion for this config."""
        return self.versions.order_by("-published_at").first()

    def create_snapshot(self):
        """Create a JSON snapshot of the current config and its cookie groups."""
        return {
            "title": str(self.title),
            "description": str(self.description),
            "privacy_policy_url": self.privacy_policy_url,
            "imprint_url": self.imprint_url,
            "position": self.position,
            "accept_all_label": str(self.accept_all_label),
            "reject_all_label": str(self.reject_all_label),
            "settings_label": str(self.settings_label),
            "save_label": str(self.save_label),
            "cookie_groups": [
                {
                    "name": group.name,
                    "slug": group.slug,
                    "description": group.description,
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
                    or group.cookies,
                }
                for group in self.cookie_groups.all().order_by("order")
            ],
        }


class CookieGroup(models.Model):
    """
    A category of cookies (e.g. Essential, Analytics, Marketing).
    Users can toggle groups individually for granular consent control.
    """

    config = models.ForeignKey(
        CookieConsentConfig,
        on_delete=models.CASCADE,
        related_name="cookie_groups",
        verbose_name=_("Configuration"),
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name"),
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_("Slug"),
    )
    description = models.TextField(
        verbose_name=_("Description"),
        help_text=_("Explains to the user what this cookie group does"),
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_("Required"),
        help_text=_("Required groups cannot be deactivated (e.g. Essential)"),
    )
    is_default_enabled = models.BooleanField(
        default=False,
        verbose_name=_("Enabled by Default"),
        help_text=_("Pre-selected state (only allowed for required groups per GDPR)"),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
    )
    cookies = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Cookies"),
        help_text=_('List of cookies: [{"name": "...", "provider": "...", "duration": "...", "purpose": "..."}]'),
    )

    class Meta:
        verbose_name = _("Cookie Group")
        verbose_name_plural = _("Cookie Groups")
        ordering = ["order"]

    def __str__(self):
        return self.name

    def clean(self):
        """GDPR: optional groups must not be pre-selected."""
        if self.is_default_enabled and not self.is_required:
            raise ValidationError(_("Only required cookie groups may be enabled by default (GDPR compliance)."))


class Cookie(models.Model):
    """
    An individual cookie within a CookieGroup.
    Allows granular per-cookie consent instead of only group-level consent.
    """

    group = models.ForeignKey(
        CookieGroup,
        on_delete=models.CASCADE,
        related_name="cookie_items",
        verbose_name=_("Cookie Group"),
    )
    name = models.CharField(
        max_length=100,
        verbose_name=_("Cookie Name"),
        help_text=_("Technical cookie name, e.g. _ga, _fbp"),
    )
    slug = models.SlugField(
        max_length=100,
        verbose_name=_("Slug"),
        help_text=_("Unique identifier within the group, used for API identification"),
    )
    provider = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("Provider"),
        help_text=_("Service that sets this cookie, e.g. Google Analytics"),
    )
    duration = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("Duration"),
        help_text=_("How long the cookie persists, e.g. 2 years, Session"),
    )
    purpose = models.TextField(
        blank=True,
        verbose_name=_("Purpose"),
        help_text=_("Description of what this cookie is used for"),
    )
    is_required = models.BooleanField(
        default=False,
        verbose_name=_("Required"),
        help_text=_("Required cookies cannot be deselected by the user"),
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Order"),
    )

    class Meta:
        verbose_name = _("Cookie")
        verbose_name_plural = _("Cookies")
        ordering = ["order", "name"]
        unique_together = [("group", "slug")]

    def __str__(self):
        return f"{self.name} ({self.group.name})"

    def clean(self):
        """If the parent group is required, this cookie must also be required."""
        if self.group_id and self.group.is_required and not self.is_required:
            raise ValidationError(_("Cookies in a required group must also be marked as required."))


class ConsentVersion(models.Model):
    """
    Tracks changes to the cookie configuration.
    Stores a snapshot for audit trail and can force re-consent.
    """

    config = models.ForeignKey(
        CookieConsentConfig,
        on_delete=models.CASCADE,
        related_name="versions",
        verbose_name=_("Configuration"),
    )
    version = models.CharField(
        max_length=20,
        verbose_name=_("Version"),
    )
    change_description = models.TextField(
        verbose_name=_("Change Description"),
        help_text=_("What changed in this version"),
    )
    requires_reconsent = models.BooleanField(
        default=False,
        verbose_name=_("Requires Re-consent"),
        help_text=_("If checked, all users must re-consent"),
    )
    published_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Published At"),
    )
    snapshot = models.JSONField(
        verbose_name=_("Snapshot"),
        help_text=_("Complete snapshot of config and cookie groups at time of publishing"),
    )

    class Meta:
        verbose_name = _("Consent Version")
        verbose_name_plural = _("Consent Versions")
        ordering = ["-published_at"]
        unique_together = [("config", "version")]

    def __str__(self):
        return f"v{self.version}"

    def save(self, *args, **kwargs):
        # Auto-generate snapshot on creation
        if not self.pk and not self.snapshot:
            self.snapshot = self.config.create_snapshot()
        super().save(*args, **kwargs)

    @classmethod
    def get_current(cls, config=None):
        """Return the latest published version, optionally for a specific config."""
        qs = cls.objects.all()
        if config:
            qs = qs.filter(config=config)
        return qs.order_by("-published_at").first()


class UserConsent(models.Model):
    """
    Records an individual user's consent decision.
    Immutable audit trail – records are never updated or deleted.
    """

    consent_id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name=_("Consent ID"),
    )
    version = models.ForeignKey(
        ConsentVersion,
        on_delete=models.PROTECT,
        related_name="user_consents",
        verbose_name=_("Consent Version"),
    )
    ip_hash = models.CharField(
        max_length=64,
        verbose_name=_("IP Hash"),
        help_text=_("SHA-256 hash of the user's IP address"),
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name=_("User Agent"),
    )
    accepted_groups = models.ManyToManyField(
        CookieGroup,
        blank=True,
        related_name="consents",
        verbose_name=_("Accepted Groups"),
    )
    accepted_cookies = models.ManyToManyField(
        "Cookie",
        blank=True,
        related_name="consents",
        verbose_name=_("Accepted Cookies"),
    )

    CONSENT_METHOD_CHOICES = [
        ("banner_accept_all", _("Banner – Accept All")),
        ("banner_reject", _("Banner – Reject Optional")),
        ("settings", _("Settings Modal")),
        ("revoke", _("Revoke")),
        ("api", _("API")),
    ]
    consent_method = models.CharField(
        max_length=30,
        choices=CONSENT_METHOD_CHOICES,
        verbose_name=_("Consent Method"),
    )

    consent_given_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Consent Given At"),
    )

    class Meta:
        verbose_name = _("User Consent")
        verbose_name_plural = _("User Consents")
        ordering = ["-consent_given_at"]

    def __str__(self):
        return f"Consent {self.consent_id} (v{self.version.version})"

    def get_accepted_cookie_slugs(self):
        """Return a list of all accepted cookie slugs in 'group_slug:cookie_slug' format."""
        return [f"{c.group.slug}:{c.slug}" for c in self.accepted_cookies.select_related("group").all()]

    def is_cookie_accepted(self, cookie_slug):
        """
        Check if a specific cookie is accepted.
        cookie_slug can be 'group_slug:cookie_slug' or just 'cookie_slug'.
        """
        if ":" in cookie_slug:
            group_slug, slug = cookie_slug.split(":", 1)
            return self.accepted_cookies.filter(group__slug=group_slug, slug=slug).exists()
        return self.accepted_cookies.filter(slug=cookie_slug).exists()

    def is_valid(self):
        """
        Check if this consent is still valid.
        Invalid if a newer version with requires_reconsent=True exists.
        """
        newer_versions = ConsentVersion.objects.filter(
            config=self.version.config,
            published_at__gt=self.version.published_at,
            requires_reconsent=True,
        )
        return not newer_versions.exists()

    @classmethod
    def get_by_consent_id(cls, consent_id_str):
        """
        Retrieve a UserConsent by its UUID string from the cookie.
        Returns None if not found or invalid UUID.
        """
        try:
            return cls.objects.select_related("version", "version__config").get(consent_id=consent_id_str)
        except (cls.DoesNotExist, ValueError, ValidationError):
            return None
