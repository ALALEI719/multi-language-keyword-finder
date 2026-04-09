"""
Pre-start script: inject GA snippet into Streamlit's own static/index.html <head>.

Run this ONCE before starting Streamlit so that the GA tag appears in the
raw HTML source returned to every browser/crawler — not just after React
hydrates. This fixes Google Analytics verification failures.

Usage (called automatically by Procfile):
    python inject_ga_head.py
"""
import os
import streamlit

GA_ID = "G-H1EWMGSPYG"

GA_SNIPPET = f"""<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id={GA_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_ID}');
</script>"""

def main():
    st_static = os.path.join(os.path.dirname(streamlit.__file__), "static", "index.html")

    if not os.path.exists(st_static):
        print(f"⚠️  Streamlit index.html not found at: {st_static}")
        return

    with open(st_static, "r", encoding="utf-8") as f:
        content = f.read()

    if GA_ID in content:
        print("✅ GA tag already present in Streamlit index.html — skipping.")
        return

    if "</head>" not in content:
        print("⚠️  </head> tag not found in index.html — cannot inject.")
        return

    patched = content.replace("</head>", GA_SNIPPET + "\n</head>", 1)

    with open(st_static, "w", encoding="utf-8") as f:
        f.write(patched)

    print(f"✅ GA tag ({GA_ID}) injected into Streamlit index.html <head>.")

if __name__ == "__main__":
    main()
