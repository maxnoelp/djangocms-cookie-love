# Step 08 – Frontend (Templates, CSS, JavaScript)

## Goal

Build a responsive, accessible, Bootstrap 5-based cookie consent banner with settings modal. All frontend code uses Vanilla JS (no jQuery).

## Templates

### 8.1 `banner.html` – Main Banner

```html
{% load static %} {% if cookie_config %}
<div
  id="cookie-love-banner"
  class="cl-banner cl-banner--{{ cookie_config.position }}"
  role="dialog"
  aria-label="Cookie Consent"
  aria-modal="false"
  data-version="{{ current_version.version }}"
  style="display: none;"
>
  <div class="cl-banner__container container">
    <div class="cl-banner__content">
      <h2 class="cl-banner__title">{{ cookie_config.title }}</h2>
      <p class="cl-banner__text">{{ cookie_config.description }}</p>

      <div class="cl-banner__links">
        {% if cookie_config.privacy_policy_url %}
        <a href="{{ cookie_config.privacy_policy_url }}" class="cl-banner__link"
          >Privacy Policy</a
        >
        {% endif %} {% if cookie_config.imprint_url %}
        <a href="{{ cookie_config.imprint_url }}" class="cl-banner__link"
          >Imprint</a
        >
        {% endif %}
      </div>
    </div>

    <div class="cl-banner__actions">
      <button
        type="button"
        class="btn btn-outline-secondary cl-btn cl-btn--reject"
        data-cl-action="reject"
      >
        {{ cookie_config.reject_all_label }}
      </button>
      <button
        type="button"
        class="btn btn-outline-primary cl-btn cl-btn--settings"
        data-cl-action="settings"
      >
        {{ cookie_config.settings_label }}
      </button>
      <button
        type="button"
        class="btn btn-primary cl-btn cl-btn--accept"
        data-cl-action="accept-all"
      >
        {{ cookie_config.accept_all_label }}
      </button>
    </div>
  </div>
</div>

{% include "djangocms_cookie_love/settings_modal.html" %}

<link
  rel="stylesheet"
  href="{% static 'djangocms_cookie_love/css/cookie-love.css' %}"
/>
<script
  src="{% static 'djangocms_cookie_love/js/cookie-love.js' %}"
  defer
></script>
{% endif %}
```

### 8.2 `settings_modal.html` – Detailed Settings

```html
<div
  id="cookie-love-settings"
  class="cl-modal"
  role="dialog"
  aria-label="Cookie Settings"
  aria-modal="true"
  style="display: none;"
>
  <div class="cl-modal__overlay" data-cl-action="close-settings"></div>
  <div class="cl-modal__dialog">
    <div class="cl-modal__header">
      <h3 class="cl-modal__title">{{ cookie_config.title }}</h3>
      <button
        type="button"
        class="btn-close cl-modal__close"
        data-cl-action="close-settings"
        aria-label="Close"
      ></button>
    </div>
    <div class="cl-modal__body">
      <p class="cl-modal__description">{{ cookie_config.description }}</p>

      {% for group in cookie_groups %} {% include
      "djangocms_cookie_love/includes/cookie_group.html" with group=group %} {%
      endfor %}
    </div>
    <div class="cl-modal__footer">
      <button
        type="button"
        class="btn btn-outline-secondary cl-btn"
        data-cl-action="reject"
      >
        {{ cookie_config.reject_all_label }}
      </button>
      <button
        type="button"
        class="btn btn-primary cl-btn"
        data-cl-action="save-settings"
      >
        {{ cookie_config.save_label }}
      </button>
    </div>
  </div>
</div>
```

### 8.3 `includes/cookie_group.html` – Single Group

```html
<div class="cl-group" data-group-slug="{{ group.slug }}">
  <div class="cl-group__header">
    <div class="cl-group__info">
      <h4 class="cl-group__name">{{ group.name }}</h4>
      {% if group.is_required %}
      <span class="badge bg-secondary cl-group__badge">Always Active</span>
      {% endif %}
    </div>
    {% include "djangocms_cookie_love/includes/toggle_switch.html" with
    group=group %}
  </div>
  <p class="cl-group__description">{{ group.description }}</p>

  {% if group.cookies %}
  <details class="cl-group__details">
    <summary>Show cookies ({{ group.cookies|length }})</summary>
    <table class="table table-sm cl-group__table">
      <thead>
        <tr>
          <th>Name</th>
          <th>Provider</th>
          <th>Duration</th>
          <th>Purpose</th>
        </tr>
      </thead>
      <tbody>
        {% for cookie in group.cookies %}
        <tr>
          <td>{{ cookie.name }}</td>
          <td>{{ cookie.provider }}</td>
          <td>{{ cookie.duration }}</td>
          <td>{{ cookie.purpose }}</td>
        </tr>
        {% endfor %}
      </tbody>
    </table>
  </details>
  {% endif %}
</div>
```

### 8.4 `includes/toggle_switch.html` – Toggle Component

```html
<div class="form-check form-switch cl-toggle">
  <input
    class="form-check-input cl-toggle__input"
    type="checkbox"
    role="switch"
    id="cl-toggle-{{ group.slug }}"
    data-group-slug="{{ group.slug }}"
    {%
    if
    group.is_required
    %}checked
    disabled{%
    endif
    %}
    aria-label="Toggle {{ group.name }}"
  />
</div>
```

## CSS (`cookie-love.css`)

### Design Principles

- Bootstrap 5 utilities and components
- BEM naming convention with `cl-` prefix (Cookie Love)
- CSS custom properties for easy theming
- Mobile-first responsive design
- Respects `prefers-reduced-motion`

### CSS Custom Properties

```css
:root {
  --cl-primary: var(--bs-primary, #0d6efd);
  --cl-bg: var(--bs-body-bg, #ffffff);
  --cl-text: var(--bs-body-color, #212529);
  --cl-border: var(--bs-border-color, #dee2e6);
  --cl-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  --cl-z-index: 9999;
  --cl-modal-z-index: 10000;
  --cl-border-radius: var(--bs-border-radius, 0.375rem);
}
```

### Layout Variants

- `.cl-banner--bottom` – Fixed to bottom of viewport
- `.cl-banner--top` – Fixed to top of viewport
- `.cl-banner--center` – Centered modal overlay

## JavaScript (`cookie-love.js`)

### Architecture

Vanilla JS module with public API:

```javascript
window.CookieLove = {
    init(config),           // Initialize with config from server or inline
    openSettings(),         // Open settings modal
    closeSettings(),        // Close settings modal
    acceptAll(),            // Accept all cookie groups
    rejectAll(),            // Reject optional groups
    saveSettings(),         // Save current toggle states
    getConsent(),           // Get current consent state
    hasConsent(groupSlug),  // Check if specific group is consented
    onConsent(callback),    // Register callback for consent changes
    revokeConsent(),        // Revoke all optional consent
};
```

### Script Blocking/Unblocking

```javascript
// Activate scripts for consented groups
function activateScripts(acceptedGroups) {
  document.querySelectorAll("script[data-cookie-group]").forEach((script) => {
    const group = script.getAttribute("data-cookie-group");
    if (acceptedGroups.includes(group)) {
      const newScript = document.createElement("script");
      newScript.textContent = script.textContent;
      if (script.src) newScript.src = script.src;
      script.parentNode.replaceChild(newScript, script);
    }
  });
}

// Delete cookies for revoked groups
function deleteCookiesForGroup(groupSlug, cookieNames) {
  cookieNames.forEach((name) => {
    document.cookie = `${name}=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;`;
  });
}
```

### Event System

```javascript
// Custom events for integration
document.dispatchEvent(
  new CustomEvent("cookie-love:consent", {
    detail: { acceptedGroups: ["essential", "analytics"] },
  }),
);

document.dispatchEvent(
  new CustomEvent("cookie-love:revoke", {
    detail: { revokedGroups: ["analytics"] },
  }),
);
```

### Flow

1. Page loads → JS checks for existing consent cookie
2. If no consent or version outdated → show banner
3. User clicks action → send to API → set cookie → activate scripts
4. If consent exists and current → activate consented scripts immediately

## Accessibility

- `role="dialog"` and `aria-label` on banner and modal
- `aria-modal="true"` on settings modal
- Focus trap in settings modal
- Keyboard navigation (Tab, Enter, Escape)
- `prefers-reduced-motion` respected for animations
- Sufficient color contrast (WCAG AA)
- Screen reader compatible toggle switches

## Verification

- [ ] Banner renders correctly in bottom, top, and center positions
- [ ] Settings modal opens and closes properly
- [ ] Toggle switches work for optional groups
- [ ] Required groups are always on and disabled
- [ ] Cookie details table shows correctly
- [ ] Responsive on mobile devices
- [ ] Keyboard navigation works
- [ ] Screen reader announces banner correctly
- [ ] CSS variables allow easy theming
- [ ] Scripts are blocked before consent and activated after
- [ ] `CookieLove.openSettings()` API works
