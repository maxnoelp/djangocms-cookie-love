"""Admin configuration for cookie consent."""

import csv

from django.contrib import admin
from django.http import HttpResponse
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .models import ConsentVersion, Cookie, CookieConsentConfig, CookieGroup, DiscoveredCookie, UserConsent

# ---------------------------------------------------------------------------
# Inline
# ---------------------------------------------------------------------------


class CookieInline(admin.TabularInline):
    """Inline for editing individual cookies within a cookie group."""

    model = Cookie
    extra = 0
    fields = [
        "name",
        "slug",
        "provider",
        "duration",
        "purpose",
        "is_required",
        "order",
    ]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order", "name"]


class CookieGroupInline(admin.TabularInline):
    """Inline for editing cookie groups on the config page."""

    model = CookieGroup
    extra = 0
    fields = [
        "name",
        "slug",
        "description",
        "is_required",
        "is_default_enabled",
        "order",
    ]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]
    show_change_link = True


# ---------------------------------------------------------------------------
# CookieConsentConfig  (Singleton)
# ---------------------------------------------------------------------------


@admin.register(CookieConsentConfig)
class CookieConsentConfigAdmin(admin.ModelAdmin):
    """Admin for the singleton cookie consent configuration."""

    list_display = ["title", "position", "is_active", "updated_at"]
    list_filter = ["is_active"]
    fieldsets = [
        (
            None,
            {
                "fields": ["title", "description", "is_active"],
            },
        ),
        (
            _("Links"),
            {
                "fields": [
                    "privacy_policy_path",
                    "privacy_policy_url",
                    "imprint_path",
                    "imprint_url",
                ],
            },
        ),
        (
            _("Design"),
            {
                "fields": ["position"],
            },
        ),
        (
            _("Button Labels"),
            {
                "fields": [
                    "accept_all_label",
                    "reject_all_label",
                    "settings_label",
                    "save_label",
                ],
                "classes": ["collapse"],
            },
        ),
    ]
    inlines = [CookieGroupInline]

    def has_add_permission(self, request):
        """Singleton: only allow adding if no config exists yet."""
        if CookieConsentConfig.objects.exists():
            return False
        return super().has_add_permission(request)


# ---------------------------------------------------------------------------
# CookieGroup  (own admin page with CookieInline)
# ---------------------------------------------------------------------------


@admin.register(CookieGroup)
class CookieGroupAdmin(admin.ModelAdmin):
    """Admin for cookie groups with individual cookie inline editing."""

    list_display = ["name", "slug", "config", "is_required", "order", "cookie_count"]
    list_filter = ["is_required", "config"]
    search_fields = ["name", "slug"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [CookieInline]
    fields = [
        "config",
        "name",
        "slug",
        "description",
        "is_required",
        "is_default_enabled",
        "order",
    ]

    @admin.display(description=_("Cookies"))
    def cookie_count(self, obj):
        return obj.cookie_items.count()


# ---------------------------------------------------------------------------
# ConsentVersion
# ---------------------------------------------------------------------------


@admin.register(ConsentVersion)
class ConsentVersionAdmin(admin.ModelAdmin):
    """Admin for cookie consent version management."""

    list_display = ["version", "config", "requires_reconsent", "published_at"]
    list_filter = ["requires_reconsent", "published_at"]
    readonly_fields = ["snapshot", "published_at"]
    fields = [
        "config",
        "version",
        "change_description",
        "requires_reconsent",
        "snapshot",
        "published_at",
    ]

    def save_model(self, request, obj, form, change):
        """Auto-generate snapshot from config on creation."""
        if not change:
            obj.snapshot = obj.config.create_snapshot()
        super().save_model(request, obj, form, change)


# ---------------------------------------------------------------------------
# UserConsent  (Read-only audit trail)
# ---------------------------------------------------------------------------


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    """Read-only admin for GDPR consent audit trail."""

    list_display = [
        "consent_id",
        "version",
        "consent_method",
        "consent_given_at",
    ]
    list_filter = ["consent_method", "consent_given_at", "version"]
    search_fields = ["consent_id", "ip_hash"]
    readonly_fields = [
        "consent_id",
        "version",
        "ip_hash",
        "user_agent",
        "accepted_groups",
        "accepted_cookies",
        "consent_method",
        "consent_given_at",
    ]
    actions = ["export_consent_csv"]

    def has_add_permission(self, request):
        return False  # Consents are only created via the API

    def has_change_permission(self, request, obj=None):
        return False  # Consents are immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Consents must not be deleted (audit trail)

    @admin.action(description=_("Export selected consent records as CSV"))
    def export_consent_csv(self, request, queryset):
        """Export selected consent records as CSV for GDPR compliance."""
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="consent_records.csv"'
        writer = csv.writer(response)
        writer.writerow(
            [
                "Consent ID",
                "Version",
                "IP Hash",
                "User Agent",
                "Consent Method",
                "Accepted Groups",
                "Accepted Cookies",
                "Consent Given At",
            ]
        )
        for consent in queryset.select_related("version").prefetch_related(
            "accepted_groups", "accepted_cookies__group"
        ):
            writer.writerow(
                [
                    str(consent.consent_id),
                    str(consent.version),
                    consent.ip_hash,
                    consent.user_agent,
                    consent.get_consent_method_display(),
                    ", ".join(g.name for g in consent.accepted_groups.all()),
                    ", ".join(f"{c.group.slug}:{c.slug}" for c in consent.accepted_cookies.all()),
                    consent.consent_given_at.isoformat(),
                ]
            )
        return response


# ---------------------------------------------------------------------------
# DiscoveredCookie  (read-mostly, populated by middleware / crawler)
# ---------------------------------------------------------------------------


class ResolvedStatusFilter(admin.SimpleListFilter):
    """Three-way filter that defaults to showing only unresolved cookies."""

    title = _("status")
    parameter_name = "status"

    def lookups(self, request, model_admin):
        return [
            ("unresolved", _("Unresolved")),
            ("resolved", _("Resolved")),
            ("all", _("All")),
        ]

    def queryset(self, request, queryset):
        value = self.value() or "unresolved"
        if value == "resolved":
            return queryset.filter(is_resolved=True)
        if value == "all":
            return queryset
        return queryset.filter(is_resolved=False)

    def choices(self, changelist):
        # Skip the default "All" entry; we render our own three options and
        # mark "Unresolved" as selected when no query param is present.
        value = self.value() or "unresolved"
        for lookup, title in self.lookup_choices:
            yield {
                "selected": value == lookup,
                "query_string": changelist.get_query_string(
                    {self.parameter_name: lookup}
                ),
                "display": title,
            }


@admin.register(DiscoveredCookie)
class DiscoveredCookieAdmin(admin.ModelAdmin):
    """Admin for cookies observed at runtime but not yet documented."""

    list_display = [
        "name",
        "domain",
        "source",
        "occurrence_count",
        "first_seen",
        "last_seen",
        "is_resolved",
    ]
    list_filter = [ResolvedStatusFilter, "source", "domain"]
    search_fields = ["name", "domain", "sample_path", "notes"]
    readonly_fields = [
        "name",
        "domain",
        "source",
        "first_seen",
        "last_seen",
        "occurrence_count",
        "sample_path",
        "sample_user_agent",
        "seen_in",
    ]
    fields = [
        "name",
        "domain",
        "source",
        "occurrence_count",
        "first_seen",
        "last_seen",
        "sample_path",
        "sample_user_agent",
        "seen_in",
        "is_resolved",
        "notes",
    ]
    actions = ["mark_resolved", "mark_unresolved"]

    def has_add_permission(self, request):
        return False  # Only populated by middleware / crawler

    @admin.action(description=_("Mark selected as resolved"))
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)

    @admin.action(description=_("Mark selected as unresolved"))
    def mark_unresolved(self, request, queryset):
        queryset.update(is_resolved=False)

    def get_actions(self, request):
        actions = super().get_actions(request)
        for group in CookieGroup.objects.select_related("config").order_by(
            "config_id", "order", "name"
        ):
            action_name = f"assign_to_group_{group.pk}"
            actions[action_name] = (
                _make_assign_to_group_action(group),
                action_name,
                _('Assign to cookie group: "%s"') % group.name,
            )
        return actions


def _unique_cookie_slug(group, name):
    """Generate a slug that is unique within the given CookieGroup."""
    base = slugify(name) or "cookie"
    base = base[:100]
    slug = base
    suffix = 2
    while Cookie.objects.filter(group=group, slug=slug).exists():
        tail = f"-{suffix}"
        slug = f"{base[: 100 - len(tail)]}{tail}"
        suffix += 1
    return slug


def _make_assign_to_group_action(group):
    """Build an admin action that assigns selected DiscoveredCookies to ``group``."""

    def assign_action(modeladmin, request, queryset):
        created = 0
        reused = 0
        for discovered in queryset:
            cookie, was_created = Cookie.objects.get_or_create(
                group=group,
                name=discovered.name,
                defaults={
                    "slug": _unique_cookie_slug(group, discovered.name),
                    "provider": discovered.domain or "",
                    "is_required": group.is_required,
                },
            )
            if was_created:
                created += 1
            else:
                reused += 1
        resolved = queryset.update(is_resolved=True)
        modeladmin.message_user(
            request,
            _(
                'Assigned %(resolved)d cookie(s) to "%(group)s" '
                "(%(created)d created, %(reused)d already existed)."
            )
            % {
                "resolved": resolved,
                "group": group.name,
                "created": created,
                "reused": reused,
            },
        )

    assign_action.short_description = _('Assign to cookie group: "%s"') % group.name
    return assign_action
