"""Tests for CMS plugin and template tags."""


class TestCookieConsentPlugin:
    def test_plugin_registered(self, db):
        from cms.plugin_pool import plugin_pool

        plugins = plugin_pool.get_all_plugins()
        plugin_names = [p.__name__ for p in plugins]
        assert "CookieConsentPlugin" in plugin_names

    def test_plugin_attributes(self, db):
        from djangocms_cookie_love.contrib.cms.cms_plugins import CookieConsentPlugin

        assert CookieConsentPlugin.cache is False
        assert CookieConsentPlugin.allow_children is False
        assert "banner.html" in CookieConsentPlugin.render_template


class TestTemplateTags:
    def test_template_tags_import(self):
        from djangocms_cookie_love.templatetags.cookie_love_tags import (
            cookie_love_banner,
            cookie_love_css,
            cookie_love_js,
        )

        assert callable(cookie_love_banner)
        assert callable(cookie_love_css)
        assert callable(cookie_love_js)

    def test_cookie_love_css_output(self):
        from djangocms_cookie_love.templatetags.cookie_love_tags import (
            cookie_love_css,
        )

        output = cookie_love_css()
        assert "cookie-love.css" in str(output)
        assert "<link" in str(output)

    def test_cookie_love_js_output(self):
        from djangocms_cookie_love.templatetags.cookie_love_tags import (
            cookie_love_js,
        )

        output = cookie_love_js()
        assert "cookie-love.js" in str(output)
        assert "<script" in str(output)
        assert "defer" in str(output)
