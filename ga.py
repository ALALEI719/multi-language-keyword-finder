"""
Google Analytics injection for Streamlit.

Why this approach:
- st.markdown() scripts are silently dropped by React's dangerouslySetInnerHTML
- components.v1.html() creates a real iframe whose JS CAN access window.parent
- We inject the gtag script directly into the parent document <head>
- A deduplication guard (id="ga-gtag-script") prevents double injection on reruns

Usage — add to every page file right after st.set_page_config():
    from ga import inject_ga
    inject_ga()
"""
import streamlit.components.v1 as components

_GA_ID = "G-H1EWMGSPYG"

_INJECT_JS = """
<script>
(function() {
  var parent = window.parent;
  var doc    = parent.document;

  // Guard: only inject once per page load
  if (doc.getElementById('ga-gtag-script')) { return; }

  // 1. Load gtag.js into parent <head>
  var s = doc.createElement('script');
  s.id    = 'ga-gtag-script';
  s.async = true;
  s.src   = 'https://www.googletagmanager.com/gtag/js?id=__GA_ID__';
  doc.head.appendChild(s);

  // 2. Initialise dataLayer in parent window
  parent.dataLayer = parent.dataLayer || [];
  parent.gtag = function() { parent.dataLayer.push(arguments); };
  parent.gtag('js', new Date());
  parent.gtag('config', '__GA_ID__');
})();
</script>
""".replace("__GA_ID__", _GA_ID)


def inject_ga() -> None:
    """Inject Google Analytics into the Streamlit parent page <head>."""
    components.html(_INJECT_JS, height=0)
