/**
 * Cookie Love – Cookie Consent Manager
 * Vanilla JS, no dependencies
 *
 * Public API:
 *   CookieLove.init()            – Auto-called on DOMContentLoaded
 *   CookieLove.openSettings()    – Open settings modal
 *   CookieLove.closeSettings()   – Close settings modal
 *   CookieLove.acceptAll()       – Accept all cookie groups
 *   CookieLove.rejectAll()       – Reject optional groups
 *   CookieLove.saveSettings()    – Save current toggle states
 *   CookieLove.getConsent()      – Get current consent state
 *   CookieLove.hasConsent(slug)  – Check if a group is consented
 *   CookieLove.hasCookieConsent(groupSlug, cookieSlug) – Check cookie-level consent
 *   CookieLove.onConsent(cb)     – Register callback for consent changes
 *   CookieLove.revokeConsent()   – Revoke all optional consent
 */
(function () {
  "use strict";

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------

  const state = {
    banner: null,
    modal: null,
    config: null,
    csrfToken: "",
    consentUrl: "",
    revokeUrl: "",
    acceptedGroups: [],
    acceptedCookies: [],
    listeners: [],
    focusTrap: null,
    previousFocus: null,
  };

  // ---------------------------------------------------------------------------
  // Cookie helpers
  // ---------------------------------------------------------------------------

  function getCookie(name) {
    const match = document.cookie.match(
      new RegExp("(^| )" + name + "=([^;]+)")
    );
    return match ? decodeURIComponent(match[2]) : null;
  }

  // ---------------------------------------------------------------------------
  // DOM helpers
  // ---------------------------------------------------------------------------

  function show(el) {
    if (!el) return;
    el.style.display = "";
    el.setAttribute("data-cl-visible", "true");
  }

  function hide(el) {
    if (!el) return;
    el.style.display = "none";
    el.removeAttribute("data-cl-visible");
  }

  // ---------------------------------------------------------------------------
  // Focus trap for modal
  // ---------------------------------------------------------------------------

  function enableFocusTrap(container) {
    state.previousFocus = document.activeElement;
    const focusable = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    );
    if (focusable.length === 0) return;

    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    first.focus();

    state.focusTrap = function (e) {
      if (e.key === "Tab") {
        if (e.shiftKey) {
          if (document.activeElement === first) {
            e.preventDefault();
            last.focus();
          }
        } else {
          if (document.activeElement === last) {
            e.preventDefault();
            first.focus();
          }
        }
      }
      if (e.key === "Escape") {
        CookieLove.closeSettings();
      }
    };
    container.addEventListener("keydown", state.focusTrap);
  }

  function disableFocusTrap(container) {
    if (state.focusTrap) {
      container.removeEventListener("keydown", state.focusTrap);
      state.focusTrap = null;
    }
    if (state.previousFocus) {
      state.previousFocus.focus();
      state.previousFocus = null;
    }
  }

  // ---------------------------------------------------------------------------
  // Script activation / deactivation
  // ---------------------------------------------------------------------------

  function activateScripts(acceptedGroups, acceptedCookies) {
    var cookieSet = {};
    (acceptedCookies || []).forEach(function (ref) {
      cookieSet[ref] = true;
    });

    document
      .querySelectorAll('script[type="text/plain"][data-cookie-group]')
      .forEach(function (script) {
        var group = script.getAttribute("data-cookie-group");
        var cookieSlug = script.getAttribute("data-cookie-slug");
        var allowed = false;

        if (cookieSlug && group) {
          // Cookie-level blocking: check specific cookie
          allowed = !!cookieSet[group + ":" + cookieSlug];
        } else {
          // Group-level blocking
          allowed = acceptedGroups.indexOf(group) !== -1;
        }

        if (allowed) {
          var newScript = document.createElement("script");
          for (var i = 0; i < script.attributes.length; i++) {
            var attr = script.attributes[i];
            if (
              attr.name !== "type" &&
              attr.name !== "data-cookie-group" &&
              attr.name !== "data-cookie-slug" &&
              attr.name !== "data-src"
            ) {
              newScript.setAttribute(attr.name, attr.value);
            }
          }
          var dataSrc = script.getAttribute("data-src");
          if (dataSrc) {
            newScript.src = dataSrc;
          } else if (script.src) {
            newScript.src = script.src;
          } else {
            newScript.textContent = script.textContent;
          }
          script.parentNode.replaceChild(newScript, script);
        }
      });
  }

  // ---------------------------------------------------------------------------
  // API calls
  // ---------------------------------------------------------------------------

  function postConsent(data, callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", state.consentUrl, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", state.csrfToken);
    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        var result = JSON.parse(xhr.responseText);
        callback(null, result);
      } else {
        callback(new Error("Consent save failed: " + xhr.status));
      }
    };
    xhr.onerror = function () {
      callback(new Error("Network error"));
    };
    xhr.send(JSON.stringify(data));
  }

  function postRevoke(callback) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", state.revokeUrl, true);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.setRequestHeader("X-CSRFToken", state.csrfToken);
    xhr.onload = function () {
      if (xhr.status >= 200 && xhr.status < 300) {
        var result = JSON.parse(xhr.responseText);
        callback(null, result);
      } else {
        callback(new Error("Revoke failed: " + xhr.status));
      }
    };
    xhr.onerror = function () {
      callback(new Error("Network error"));
    };
    xhr.send("{}");
  }

  // ---------------------------------------------------------------------------
  // Consent handling
  // ---------------------------------------------------------------------------

  function handleConsentResult(err, result) {
    if (err) {
      console.error("[CookieLove]", err.message);
      return;
    }
    state.acceptedGroups = result.accepted_groups || [];
    state.acceptedCookies = result.accepted_cookies || [];
    activateScripts(state.acceptedGroups, state.acceptedCookies);
    notifyListeners(state.acceptedGroups, state.acceptedCookies);
    hide(state.banner);
    hide(state.modal);
    if (state.modal) disableFocusTrap(state.modal);
  }

  function notifyListeners(acceptedGroups, acceptedCookies) {
    state.listeners.forEach(function (cb) {
      try {
        cb(acceptedGroups, acceptedCookies);
      } catch (e) {
        console.error("[CookieLove] Listener error:", e);
      }
    });
    document.dispatchEvent(
      new CustomEvent("cookie-love:consent", {
        detail: {
          acceptedGroups: acceptedGroups,
          acceptedCookies: acceptedCookies,
        },
      })
    );
  }

  function getSelectedSlugs() {
    var slugs = [];
    if (!state.modal) return slugs;
    state.modal
      .querySelectorAll(".cl-toggle__input")
      .forEach(function (input) {
        if (input.checked) {
          slugs.push(input.getAttribute("data-group-slug"));
        }
      });
    return slugs;
  }

  function getAllSlugs() {
    var slugs = [];
    if (!state.modal) return slugs;
    state.modal
      .querySelectorAll(".cl-toggle__input")
      .forEach(function (input) {
        slugs.push(input.getAttribute("data-group-slug"));
      });
    return slugs;
  }

  function getRequiredSlugs() {
    var slugs = [];
    if (!state.modal) return slugs;
    state.modal
      .querySelectorAll(".cl-toggle__input[disabled]")
      .forEach(function (input) {
        slugs.push(input.getAttribute("data-group-slug"));
      });
    return slugs;
  }

  /**
   * Get individually selected cookies (not from fully-selected groups).
   * Returns array of "group_slug:cookie_slug" strings.
   */
  function getSelectedCookieRefs() {
    var refs = [];
    if (!state.modal) return refs;
    var selectedGroups = getSelectedSlugs();
    state.modal
      .querySelectorAll(".cl-cookie-item__checkbox")
      .forEach(function (input) {
        if (input.checked) {
          var groupSlug = input.getAttribute("data-group-slug");
          var cookieSlug = input.getAttribute("data-cookie-slug");
          // Only include individually if the group toggle is NOT fully checked
          if (selectedGroups.indexOf(groupSlug) === -1) {
            refs.push(groupSlug + ":" + cookieSlug);
          }
        }
      });
    return refs;
  }

  /**
   * Get all cookie refs (for accept all).
   */
  function getAllCookieRefs() {
    var refs = [];
    if (!state.modal) return refs;
    state.modal
      .querySelectorAll(".cl-cookie-item__checkbox")
      .forEach(function (input) {
        var groupSlug = input.getAttribute("data-group-slug");
        var cookieSlug = input.getAttribute("data-cookie-slug");
        refs.push(groupSlug + ":" + cookieSlug);
      });
    return refs;
  }

  function setToggles(slugs) {
    if (!state.modal) return;
    state.modal
      .querySelectorAll(".cl-toggle__input")
      .forEach(function (input) {
        if (!input.disabled) {
          input.checked =
            slugs.indexOf(input.getAttribute("data-group-slug")) !== -1;
        }
      });
  }

  /**
   * Set cookie checkboxes based on accepted cookies list.
   * @param {string[]} acceptedCookies – Array of "group_slug:cookie_slug"
   * @param {string[]} acceptedGroups – Array of group slugs (all cookies in group)
   */
  function setCookieCheckboxes(acceptedGroups, acceptedCookies) {
    if (!state.modal) return;
    var cookieSet = {};
    (acceptedCookies || []).forEach(function (ref) {
      cookieSet[ref] = true;
    });

    state.modal
      .querySelectorAll(".cl-cookie-item__checkbox")
      .forEach(function (input) {
        if (input.disabled) return;
        var groupSlug = input.getAttribute("data-group-slug");
        var cookieSlug = input.getAttribute("data-cookie-slug");
        var ref = groupSlug + ":" + cookieSlug;
        // Check if group is fully accepted or this specific cookie is accepted
        input.checked =
          (acceptedGroups && acceptedGroups.indexOf(groupSlug) !== -1) ||
          !!cookieSet[ref];
      });
  }

  /**
   * Update group toggle state based on its cookie checkboxes.
   * Sets checked, unchecked, or indeterminate.
   */
  function updateGroupToggleState(groupSlug) {
    if (!state.modal) return;
    var groupToggle = state.modal.querySelector(
      '.cl-toggle__input[data-group-slug="' + groupSlug + '"]'
    );
    if (!groupToggle || groupToggle.disabled) return;

    var cookieCheckboxes = state.modal.querySelectorAll(
      '.cl-cookie-item__checkbox[data-group-slug="' + groupSlug + '"]'
    );
    if (cookieCheckboxes.length === 0) return;

    var total = 0;
    var checked = 0;
    cookieCheckboxes.forEach(function (cb) {
      if (!cb.disabled) {
        total++;
        if (cb.checked) checked++;
      }
    });

    if (checked === 0) {
      groupToggle.checked = false;
      groupToggle.indeterminate = false;
    } else if (checked === total) {
      groupToggle.checked = true;
      groupToggle.indeterminate = false;
    } else {
      groupToggle.checked = false;
      groupToggle.indeterminate = true;
    }
    updateGroupHint(groupSlug);
  }

  /**
   * Update the status hint text for a cookie group.
   * Shows "X / Y active" below the group header.
   */
  function updateGroupHint(groupSlug) {
    if (!state.modal) return;
    var hint = state.modal.querySelector(
      '.cl-group__hint[data-group-slug="' + groupSlug + '"]'
    );
    if (!hint) return;

    var checkboxes = state.modal.querySelectorAll(
      '.cl-cookie-item__checkbox[data-group-slug="' + groupSlug + '"]'
    );
    if (checkboxes.length === 0) {
      hint.textContent = "";
      hint.className = "cl-group__hint";
      return;
    }

    var total = 0;
    var checked = 0;
    checkboxes.forEach(function (cb) {
      total++;
      if (cb.checked) checked++;
    });

    // Remove old modifier classes
    hint.classList.remove(
      "cl-group__hint--all",
      "cl-group__hint--partial",
      "cl-group__hint--none"
    );

    if (checked === 0) {
      hint.textContent = "";
      hint.classList.add("cl-group__hint--none");
    } else if (checked === total) {
      hint.textContent = total + " / " + total + " active";
      hint.classList.add("cl-group__hint--all");
    } else {
      hint.textContent = checked + " / " + total + " active";
      hint.classList.add("cl-group__hint--partial");
    }
  }

  /**
   * Update all group hints in the modal.
   */
  function updateAllGroupHints() {
    if (!state.modal) return;
    state.modal
      .querySelectorAll(".cl-group__hint")
      .forEach(function (hint) {
        var slug = hint.getAttribute("data-group-slug");
        if (slug) updateGroupHint(slug);
      });
  }

  /**
   * When group toggle changes, update all cookie checkboxes in that group.
   */
  function handleGroupToggleChange(groupSlug, isChecked) {
    if (!state.modal) return;
    state.modal
      .querySelectorAll(
        '.cl-cookie-item__checkbox[data-group-slug="' + groupSlug + '"]'
      )
      .forEach(function (cb) {
        if (!cb.disabled) {
          cb.checked = isChecked;
        }
      });
    updateGroupHint(groupSlug);
  }

  // ---------------------------------------------------------------------------
  // Check existing consent
  // ---------------------------------------------------------------------------

  function checkExistingConsent() {
    var consentId = getCookie("cookie_love_consent");
    if (!consentId) {
      show(state.banner);
      return;
    }

    // Check consent status via API
    var xhr = new XMLHttpRequest();
    xhr.open("GET", state.consentUrl, true);
    xhr.onload = function () {
      if (xhr.status === 200) {
        var data = JSON.parse(xhr.responseText);
        if (data.has_consent && data.is_current_version) {
          // Valid consent exists
          state.acceptedGroups = data.accepted_groups || [];
          state.acceptedCookies = data.accepted_cookies || [];
          activateScripts(state.acceptedGroups, state.acceptedCookies);
          notifyListeners(state.acceptedGroups, state.acceptedCookies);
        } else {
          // No consent or outdated version
          show(state.banner);
        }
      } else {
        show(state.banner);
      }
    };
    xhr.onerror = function () {
      show(state.banner);
    };
    xhr.send();
  }

  // ---------------------------------------------------------------------------
  // Event delegation
  // ---------------------------------------------------------------------------

  function handleAction(action) {
    switch (action) {
      case "accept-all":
        CookieLove.acceptAll();
        break;
      case "reject":
        CookieLove.rejectAll();
        break;
      case "settings":
        CookieLove.openSettings();
        break;
      case "close-settings":
        CookieLove.closeSettings();
        break;
      case "save-settings":
        CookieLove.saveSettings();
        break;
    }
  }

  // ---------------------------------------------------------------------------
  // Public API
  // ---------------------------------------------------------------------------

  var CookieLove = {
    init: function () {
      state.banner = document.getElementById("cookie-love-banner");
      state.modal = document.getElementById("cookie-love-settings");

      if (!state.banner) return;

      state.csrfToken = state.banner.getAttribute("data-csrf-token") || "";
      state.consentUrl = state.banner.getAttribute("data-consent-url") || "";
      state.revokeUrl = state.banner.getAttribute("data-revoke-url") || "";

      // Also try to get CSRF token from cookie (Django default)
      if (!state.csrfToken) {
        state.csrfToken = getCookie("csrftoken") || "";
      }

      // Event delegation
      document.addEventListener("click", function (e) {
        var target = e.target.closest("[data-cl-action]");
        if (target) {
          e.preventDefault();
          handleAction(target.getAttribute("data-cl-action"));
        }
      });

      // Group toggle → sync cookie checkboxes
      if (state.modal) {
        state.modal.addEventListener("change", function (e) {
          var target = e.target;
          // Group toggle changed
          if (target.classList.contains("cl-toggle__input")) {
            var groupSlug = target.getAttribute("data-group-slug");
            handleGroupToggleChange(groupSlug, target.checked);
          }
          // Individual cookie checkbox changed
          if (target.classList.contains("cl-cookie-item__checkbox")) {
            var groupSlug = target.getAttribute("data-group-slug");
            updateGroupToggleState(groupSlug);
          }
        });
      }

      checkExistingConsent();
    },

    openSettings: function () {
      if (!state.modal) return;
      // Restore toggle states from current consent
      if (state.acceptedGroups.length > 0) {
        setToggles(state.acceptedGroups);
      }
      // Restore cookie checkbox states
      setCookieCheckboxes(state.acceptedGroups, state.acceptedCookies);
      // Update group toggle indeterminate states and hints
      if (state.modal) {
        state.modal
          .querySelectorAll(".cl-toggle__input")
          .forEach(function (input) {
            if (!input.disabled) {
              updateGroupToggleState(input.getAttribute("data-group-slug"));
            }
          });
        updateAllGroupHints();
      }
      hide(state.banner);
      show(state.modal);
      enableFocusTrap(state.modal.querySelector(".cl-modal__dialog"));
    },

    closeSettings: function () {
      if (!state.modal) return;
      hide(state.modal);
      disableFocusTrap(
        state.modal.querySelector(".cl-modal__dialog")
      );
      // Show banner again if no consent yet
      if (state.acceptedGroups.length === 0) {
        show(state.banner);
      }
    },

    acceptAll: function () {
      var allSlugs = getAllSlugs();
      postConsent(
        {
          accepted_groups: allSlugs,
          accepted_cookies: [],
          consent_method: "banner_accept_all",
        },
        handleConsentResult
      );
    },

    rejectAll: function () {
      var requiredSlugs = getRequiredSlugs();
      postConsent(
        {
          accepted_groups: requiredSlugs,
          accepted_cookies: [],
          consent_method: "banner_reject",
        },
        handleConsentResult
      );
    },

    saveSettings: function () {
      var selectedSlugs = getSelectedSlugs();
      var selectedCookies = getSelectedCookieRefs();
      postConsent(
        {
          accepted_groups: selectedSlugs,
          accepted_cookies: selectedCookies,
          consent_method: "settings",
        },
        handleConsentResult
      );
    },

    getConsent: function () {
      return {
        hasConsent: state.acceptedGroups.length > 0,
        acceptedGroups: state.acceptedGroups.slice(),
        acceptedCookies: state.acceptedCookies.slice(),
      };
    },

    hasConsent: function (groupSlug) {
      return state.acceptedGroups.indexOf(groupSlug) !== -1;
    },

    hasCookieConsent: function (groupSlug, cookieSlug) {
      var ref = groupSlug + ":" + cookieSlug;
      // Cookie is accepted if its group is fully accepted or it's individually accepted
      return (
        state.acceptedGroups.indexOf(groupSlug) !== -1 ||
        state.acceptedCookies.indexOf(ref) !== -1
      );
    },

    onConsent: function (callback) {
      if (typeof callback === "function") {
        state.listeners.push(callback);
      }
    },

    revokeConsent: function () {
      postRevoke(function (err, result) {
        if (err) {
          console.error("[CookieLove]", err.message);
          return;
        }
        state.acceptedGroups = result.accepted_groups || [];
        state.acceptedCookies = result.accepted_cookies || [];
        notifyListeners(state.acceptedGroups, state.acceptedCookies);
        document.dispatchEvent(
          new CustomEvent("cookie-love:revoke", {
            detail: {
              acceptedGroups: state.acceptedGroups,
              acceptedCookies: state.acceptedCookies,
            },
          })
        );
      });
    },
  };

  // ---------------------------------------------------------------------------
  // Auto-init
  // ---------------------------------------------------------------------------

  window.CookieLove = CookieLove;

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", CookieLove.init);
  } else {
    CookieLove.init();
  }
})();
