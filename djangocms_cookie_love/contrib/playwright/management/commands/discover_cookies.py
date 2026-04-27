"""Crawl the site with Playwright and record observed cookies."""

from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from djangocms_cookie_love.constants import COOKIE_NAME
from djangocms_cookie_love.models import (
    Cookie,
    CookieConsentConfig,
    DiscoveredCookie,
    UserConsent,
)


class Command(BaseCommand):
    help = (
        "Crawl the site with a headless browser and record every cookie observed. "
        "Sweeps the matrix of (anonymous + configured users) × (no-consent, rejected, accepted) "
        "× URLs and writes findings to DiscoveredCookie (source='crawler')."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--base-url",
            default="http://localhost:8000",
            help="Site root, e.g. https://staging.example.com",
        )
        parser.add_argument(
            "--urls",
            nargs="*",
            help="Override COOKIE_LOVE_DISCOVERY_URLS. Each entry is a path like /contact/.",
        )
        parser.add_argument(
            "--login-url",
            default=None,
            help="Login URL path (default: COOKIE_LOVE_DISCOVERY_LOGIN_URL or /admin/login/).",
        )
        parser.add_argument(
            "--include-cms-pages",
            action="store_true",
            help="If django CMS is installed, sample one published page per template.",
        )
        parser.add_argument(
            "--no-headless",
            action="store_true",
            help="Run with the browser UI visible (debugging only).",
        )
        parser.add_argument(
            "--anon-only",
            action="store_true",
            help="Skip authenticated sweeps even if users are configured.",
        )

    # -----------------------------------------------------------------
    # Entry point
    # -----------------------------------------------------------------

    def handle(self, *args, **options):
        try:
            from playwright.sync_api import sync_playwright
        except ImportError as exc:
            raise CommandError(
                "Playwright is not installed. Install the optional extra:\n"
                "    pip install 'djangocms-cookie-love[playwright]'\n"
                "    playwright install chromium"
            ) from exc

        base_url = options["base_url"].rstrip("/")
        urls = self._resolve_urls(options)
        roles = self._resolve_roles(options)
        login_url = options["login_url"] or getattr(
            settings, "COOKIE_LOVE_DISCOVERY_LOGIN_URL", "/admin/login/"
        )
        consent_states = ["no_consent", "rejected", "accepted"]

        self.stdout.write(
            self.style.NOTICE(
                f"Sweeping {len(roles)} role(s) × {len(consent_states)} consent state(s) × {len(urls)} URL(s) "
                f"= {len(roles) * len(consent_states) * len(urls)} page loads."
            )
        )

        total_recorded = 0
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not options["no_headless"])
            try:
                for role in roles:
                    for consent_state in consent_states:
                        recorded = self._run_sweep(
                            browser=browser,
                            base_url=base_url,
                            login_url=login_url,
                            role=role,
                            consent_state=consent_state,
                            urls=urls,
                        )
                        total_recorded += recorded
            finally:
                browser.close()

        self.stdout.write(self.style.SUCCESS(f"Done. {total_recorded} cookie observation(s) recorded."))

    # -----------------------------------------------------------------
    # Configuration
    # -----------------------------------------------------------------

    def _resolve_urls(self, options):
        urls = options["urls"] or list(getattr(settings, "COOKIE_LOVE_DISCOVERY_URLS", ["/"]))
        if options["include_cms_pages"]:
            urls.extend(self._sample_cms_pages())
        # de-duplicate, preserving order
        seen = set()
        deduped = []
        for url in urls:
            if url not in seen:
                seen.add(url)
                deduped.append(url)
        return deduped

    def _sample_cms_pages(self):
        """Return one published-page URL per CMS template, if django CMS is available."""
        try:
            from cms.models import Page
        except ImportError:
            return []
        sampled = {}
        for page in Page.objects.public_pages().select_related().order_by("id"):
            template = getattr(page, "template", None) or "default"
            if template in sampled:
                continue
            try:
                sampled[template] = page.get_absolute_url()
            except Exception:
                continue
        return list(sampled.values())

    def _resolve_roles(self, options):
        roles = [{"label": "anon"}]
        if options["anon_only"]:
            return roles
        configured = getattr(settings, "COOKIE_LOVE_DISCOVERY_USERS", [])
        for entry in configured:
            if not entry.get("username") or not entry.get("password"):
                continue
            roles.append(
                {
                    "label": entry.get("label", entry["username"]),
                    "username": entry["username"],
                    "password": entry["password"],
                }
            )
        return roles

    # -----------------------------------------------------------------
    # One sweep = one (role, consent_state) combination
    # -----------------------------------------------------------------

    def _run_sweep(self, *, browser, base_url, login_url, role, consent_state, urls):
        self.stdout.write(f"  → role={role['label']} consent={consent_state}")
        context = browser.new_context()
        recorded = 0
        try:
            if role["label"] != "anon":
                if not self._login(context, base_url, login_url, role):
                    self.stdout.write(self.style.WARNING(f"     login failed for {role['label']} – skipping sweep"))
                    return 0

            if consent_state != "no_consent":
                self._inject_consent(context, base_url, consent_state)

            tags = {"role": role["label"], "consent": consent_state}

            for url in urls:
                page = context.new_page()
                try:
                    page.goto(base_url + url, wait_until="load", timeout=30000)
                    # A short settle gives third-party scripts time to fire.
                    page.wait_for_timeout(1500)
                except Exception as exc:
                    self.stdout.write(self.style.WARNING(f"     {url}: {exc}"))
                    page.close()
                    continue

                for cookie in context.cookies():
                    DiscoveredCookie.record(
                        name=cookie["name"],
                        domain=cookie.get("domain", ""),
                        source="crawler",
                        path=url,
                        context=tags,
                    )
                    recorded += 1
                page.close()
        finally:
            context.close()
        return recorded

    # -----------------------------------------------------------------
    # Login + consent helpers
    # -----------------------------------------------------------------

    def _login(self, context, base_url, login_url, role):
        """Best-effort login via the standard Django admin login form."""
        page = context.new_page()
        try:
            page.goto(base_url + login_url, wait_until="load", timeout=30000)
            page.fill("input[name='username']", role["username"])
            page.fill("input[name='password']", role["password"])
            page.click("button[type='submit'], input[type='submit']")
            page.wait_for_load_state("load", timeout=15000)
            return True
        except Exception:
            return False
        finally:
            page.close()

    def _inject_consent(self, context, base_url, consent_state):
        """Pre-create a UserConsent and set its UUID as the consent cookie."""
        config = CookieConsentConfig.get_active()
        if not config:
            return
        version = config.get_current_version()
        if not version:
            return

        if consent_state == "rejected":
            groups = config.cookie_groups.filter(is_required=True)
        else:  # accepted
            groups = config.cookie_groups.all()

        consent = UserConsent.objects.create(
            version=version,
            ip_hash="crawler",
            user_agent="djangocms-cookie-love-crawler",
            consent_method="api",
        )
        consent.accepted_groups.set(groups)
        consent.accepted_cookies.set(Cookie.objects.filter(group__in=groups))

        host = urlparse(base_url).hostname or "localhost"
        context.add_cookies(
            [
                {
                    "name": COOKIE_NAME,
                    "value": str(consent.consent_id),
                    "domain": host,
                    "path": "/",
                }
            ]
        )
