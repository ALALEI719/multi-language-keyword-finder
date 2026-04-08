import bcrypt
import streamlit as st

from db import create_user, get_user_by_email, get_user_by_id

AUTH_UI = {
    "en": {
        "system": "Account System",
        "guest_info": "Guest can query once for free (only top 5 results). Register/login to unlock full table and download.",
        "tab_login": "Login",
        "tab_register": "Register",
        "email": "Email",
        "password": "Password",
        "password_hint": "Password (at least 6 chars)",
        "btn_login": "Login",
        "btn_register": "Register and Login",
        "btn_guest": "Guest Mode (1 free trial)",
        "no_user": "User not found",
        "bad_pwd": "Incorrect password",
        "login_ok": "Login successful",
        "bad_email": "Invalid email format",
        "short_pwd": "Password must be at least 6 characters",
        "exists": "Email already registered",
        "register_ok": "Registration successful, auto-logged in (10 free credits).",
    },
    "zh": {
        "system": "账号系统",
        "guest_info": "游客可免费查询 1 次（仅显示前 5 条）。注册登录后可查看完整结果并下载。",
        "tab_login": "登录",
        "tab_register": "注册",
        "email": "邮箱",
        "password": "密码",
        "password_hint": "密码（至少6位）",
        "btn_login": "登录",
        "btn_register": "注册并登录",
        "btn_guest": "游客模式（免费试用 1 次）",
        "no_user": "用户不存在",
        "bad_pwd": "密码错误",
        "login_ok": "登录成功",
        "bad_email": "邮箱格式不正确",
        "short_pwd": "密码至少 6 位",
        "exists": "该邮箱已注册",
        "register_ok": "注册成功，已自动登录（赠送 10 credits）",
    },
}


def _t(key: str) -> str:
    lang = st.session_state.get("ui_lang", "en")
    return AUTH_UI.get(lang, AUTH_UI["en"]).get(key, AUTH_UI["en"][key])


def ensure_auth_state():
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "guest_used_free_query" not in st.session_state:
        st.session_state.guest_used_free_query = False


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def current_user():
    uid = st.session_state.get("user_id")
    if not uid:
        return None
    return get_user_by_id(uid)


def login_user(email: str, password: str) -> tuple[bool, str]:
    user = get_user_by_email(email)
    if not user:
        return False, _t("no_user")
    if not verify_password(password, user["password_hash"]):
        return False, _t("bad_pwd")
    st.session_state.user_id = int(user["id"])
    return True, _t("login_ok")


def register_user(email: str, password: str) -> tuple[bool, str]:
    email = (email or "").strip().lower()
    if "@" not in email:
        return False, _t("bad_email")
    if len(password or "") < 6:
        return False, _t("short_pwd")
    if get_user_by_email(email):
        return False, _t("exists")
    create_user(email, hash_password(password), credits=10)
    ok, msg = login_user(email, password)
    if ok:
        return True, _t("register_ok")
    return False, msg


def logout():
    st.session_state.user_id = None


def render_auth_gate():
    ensure_auth_state()
    user = current_user()
    if user:
        return True

    st.markdown(f"## {_t('system')}")
    st.info(_t("guest_info"))
    tab_login, tab_register = st.tabs([_t("tab_login"), _t("tab_register")])

    with tab_login:
        email = st.text_input(_t("email"), key="login_email")
        password = st.text_input(_t("password"), type="password", key="login_password")
        if st.button(_t("btn_login"), key="btn_login", type="primary"):
            ok, msg = login_user(email, password)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    with tab_register:
        email = st.text_input(_t("email"), key="register_email")
        password = st.text_input(_t("password_hint"), type="password", key="register_password")
        if st.button(_t("btn_register"), key="btn_register"):
            ok, msg = register_user(email, password)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

    if st.button(_t("btn_guest")):
        st.session_state.user_id = None
        st.session_state.allow_guest_mode = True
        st.rerun()

    return False
