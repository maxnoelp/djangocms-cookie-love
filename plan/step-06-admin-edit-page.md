# Step 06 – Admin & Edit Page

## Goal

Provide a full-featured Django Admin interface for managing cookie consent configuration, cookie groups, versions, and consent records. Optionally, a frontend edit view for non-technical users.

## Tasks

### 6.1 `CookieGroupInline`

Inline for editing cookie groups directly on the config page:

```python
class CookieGroupInline(admin.TabularInline):
    model = CookieGroup
    extra = 0
    fields = ["name", "slug", "description", "is_required", "is_default_enabled", "order", "cookies"]
    prepopulated_fields = {"slug": ("name",)}
    ordering = ["order"]
```

### 6.2 `CookieConsentConfigAdmin`

Main admin for the singleton config:

```python
@admin.register(CookieConsentConfig)
class CookieConsentConfigAdmin(admin.ModelAdmin):
    list_display = ["title", "position", "is_active", "updated_at"]
    fieldsets = [
        (None, {
            "fields": ["title", "description", "is_active"],
        }),
        ("Links", {
            "fields": ["privacy_policy_url", "imprint_url"],
        }),
        ("Design", {
            "fields": ["position"],
        }),
        ("Button Labels", {
            "fields": ["accept_all_label", "reject_all_label", "settings_label", "save_label"],
            "classes": ["collapse"],
        }),
    ]
    inlines = [CookieGroupInline]

    def has_add_permission(self, request):
        # Singleton: only allow add if no config exists yet
        if CookieConsentConfig.objects.exists():
            return False
        return super().has_add_permission(request)
```

### 6.3 `ConsentVersionAdmin`

Admin for version management:

```python
@admin.register(ConsentVersion)
class ConsentVersionAdmin(admin.ModelAdmin):
    list_display = ["version", "config", "requires_reconsent", "published_at"]
    list_filter = ["requires_reconsent", "published_at"]
    readonly_fields = ["snapshot", "published_at"]
    fields = ["config", "version", "change_description", "requires_reconsent", "snapshot", "published_at"]

    def save_model(self, request, obj, form, change):
        if not change:  # Only on creation
            obj.snapshot = obj.config.create_snapshot()
        super().save_model(request, obj, form, change)
```

### 6.4 `UserConsentAdmin`

Read-only admin for consent audit trail:

```python
@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ["consent_id", "version", "consent_method", "consent_given_at"]
    list_filter = ["consent_method", "consent_given_at", "version"]
    search_fields = ["consent_id", "ip_hash"]
    readonly_fields = [
        "consent_id", "version", "ip_hash", "user_agent",
        "accepted_groups", "consent_method", "consent_given_at",
    ]

    def has_add_permission(self, request):
        return False  # Consents are only created via the API

    def has_change_permission(self, request, obj=None):
        return False  # Consents are immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Consents must not be deleted (audit trail)
```

### 6.5 Admin Actions

Custom admin actions:

```python
# On CookieConsentConfigAdmin:
def publish_new_version(self, request, queryset):
    """Create a new ConsentVersion from current config state."""
    # Redirect to ConsentVersion add form with pre-filled config
    ...

# On UserConsentAdmin:
def export_consent_records(self, request, queryset):
    """Export selected consent records as CSV for GDPR compliance."""
    ...
```

### 6.6 Optional: Frontend Edit View

A simple, Bootstrap-styled frontend edit page at `/cookie-love/edit/`:

- Accessible only to staff users
- Shows simplified form for config and cookie groups
- Preview of how the banner will look
- "Publish New Version" button

```python
# views.py
class CookieConsentEditView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = CookieConsentConfig
    form_class = CookieConsentConfigForm
    template_name = "djangocms_cookie_love/edit_form.html"

    def test_func(self):
        return self.request.user.is_staff
```

## Verification

- [ ] Config admin shows all fields in organized fieldsets
- [ ] Cookie groups are editable inline on config page
- [ ] Singleton enforcement: cannot add second config
- [ ] Version admin auto-generates snapshot on creation
- [ ] Consent records are fully read-only in admin
- [ ] Consent records cannot be added, changed, or deleted
- [ ] CSV export of consent records works
- [ ] Frontend edit view (if implemented) is staff-only
