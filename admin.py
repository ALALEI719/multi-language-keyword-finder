import os
import streamlit as st

from db import init_db, list_users, adjust_credits


st.set_page_config(page_title="SEO Tool Admin", layout="wide")
init_db()

st.title("Admin - User Credits")

admin_password = os.getenv("ADMIN_PASSWORD", "").strip()
if not admin_password:
    st.error("ADMIN_PASSWORD is not set in environment variables.")
    st.stop()

pwd = st.text_input("Admin password", type="password")
if pwd != admin_password:
    st.warning("Enter correct admin password.")
    st.stop()

users = list_users()
if not users:
    st.info("No registered users yet.")
    st.stop()

rows = []
for u in users:
    rows.append(
        {
            "id": int(u["id"]),
            "email": u["email"],
            "credits": int(u["credits"]),
            "has_api_key": bool((u["api_key"] or "").strip()),
            "created_at": u["created_at"],
        }
    )

st.dataframe(rows, use_container_width=True, height=420)

st.markdown("### Top up credits")
user_map = {f'{r["email"]} (id={r["id"]})': r["id"] for r in rows}
selected_user = st.selectbox("Select user", list(user_map.keys()))
delta = st.number_input("Add credits", min_value=1, value=10, step=1)

if st.button("Apply top-up", type="primary"):
    adjust_credits(user_map[selected_user], int(delta))
    st.success("Credits updated.")
    st.rerun()
