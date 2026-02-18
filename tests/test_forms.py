"""Tests for forms."""

import pytest

from djangocms_cookie_love.forms import (
    CookieConsentConfigForm,
    CookieGroupForm,
    CookieGroupFormSet,
)
from djangocms_cookie_love.models import CookieConsentConfig, CookieGroup


@pytest.mark.django_db
class TestCookieConsentConfigForm:
    """Test the config form."""

    def test_form_fields(self):
        """All expected fields are present."""
        form = CookieConsentConfigForm()
        expected = {
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
        }
        assert set(form.fields.keys()) == expected

    def test_form_widgets_have_bootstrap_classes(self):
        """Widgets use Bootstrap form-control class."""
        form = CookieConsentConfigForm()
        assert "form-control" in form.fields["title"].widget.attrs.get("class", "")
        assert "form-select" in form.fields["position"].widget.attrs.get("class", "")
        assert "form-check-input" in form.fields["is_active"].widget.attrs.get("class", "")

    def test_form_valid_data(self):
        """Form validates with correct data."""
        data = {
            "title": "Cookies",
            "description": "We use cookies",
            "privacy_policy_url": "https://example.com/privacy",
            "imprint_url": "https://example.com/imprint",
            "position": "bottom",
            "accept_all_label": "Accept All",
            "reject_all_label": "Reject All",
            "settings_label": "Settings",
            "save_label": "Save",
            "is_active": True,
        }
        form = CookieConsentConfigForm(data=data)
        assert form.is_valid(), form.errors


@pytest.mark.django_db
class TestCookieGroupForm:
    """Test the cookie group form."""

    def test_form_fields(self):
        """All expected fields are present."""
        form = CookieGroupForm()
        expected = {
            "name",
            "slug",
            "description",
            "is_required",
            "is_default_enabled",
            "order",
            "cookies",
        }
        assert set(form.fields.keys()) == expected


@pytest.mark.django_db
class TestCookieGroupFormSet:
    """Test the inline formset."""

    def test_formset_model(self):
        """Formset is configured for CookieGroup."""
        assert CookieGroupFormSet.model == CookieGroup

    def test_formset_extra(self):
        """Formset provides one extra empty form."""
        config = CookieConsentConfig.objects.create(
            title="Test",
            description="Test",
            privacy_policy_url="https://example.com/privacy",
            imprint_url="https://example.com/imprint",
        )
        formset = CookieGroupFormSet(instance=config)
        assert formset.extra == 1
