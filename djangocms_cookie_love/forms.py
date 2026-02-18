"""Forms for cookie consent editing."""

from django import forms

from .models import CookieConsentConfig, CookieGroup


class CookieConsentConfigForm(forms.ModelForm):
    """Form for editing the cookie consent configuration (frontend edit page)."""

    class Meta:
        model = CookieConsentConfig
        fields = [
            "title",
            "description",
            "privacy_policy_page",
            "privacy_policy_url",
            "imprint_page",
            "imprint_url",
            "position",
            "accept_all_label",
            "reject_all_label",
            "settings_label",
            "save_label",
            "is_active",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "privacy_policy_url": forms.URLInput(attrs={"class": "form-control"}),
            "imprint_url": forms.URLInput(attrs={"class": "form-control"}),
            "position": forms.Select(attrs={"class": "form-select"}),
            "accept_all_label": forms.TextInput(attrs={"class": "form-control"}),
            "reject_all_label": forms.TextInput(attrs={"class": "form-control"}),
            "settings_label": forms.TextInput(attrs={"class": "form-control"}),
            "save_label": forms.TextInput(attrs={"class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class CookieGroupForm(forms.ModelForm):
    """Form for editing a single cookie group."""

    class Meta:
        model = CookieGroup
        fields = [
            "name",
            "slug",
            "description",
            "is_required",
            "is_default_enabled",
            "order",
            "cookies",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "slug": forms.TextInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "is_required": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_default_enabled": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "order": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }


CookieGroupFormSet = forms.inlineformset_factory(
    CookieConsentConfig,
    CookieGroup,
    form=CookieGroupForm,
    extra=1,
    can_delete=True,
)
