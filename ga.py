"""
Google Analytics injection helper.

Usage (add to the top of every page file, right after st.set_page_config):

    from ga import inject_ga
    inject_ga()
"""
import streamlit as st

_GA_ID = "G-H1EWMGSPYG"

def inject_ga() -> None:
    """Inject Google Analytics gtag.js into the current Streamlit page."""
    st.markdown(
        f"""
<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={_GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{_GA_ID}');
</script>
""",
        unsafe_allow_html=True,
    )
