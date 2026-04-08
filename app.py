import os
import streamlit as st
import requests
import pandas as pd
import json, time, uuid
from collections import Counter
from deep_translator import GoogleTranslator
from auth import ensure_auth_state, render_auth_gate, current_user, logout
from db import (
    init_db,
    log_query,
    update_user_api_key,
    deduct_credit_if_possible,
)

# ---------------------------------------------------------------------------
# i18n — Interface Language
# ---------------------------------------------------------------------------
UI = {
    "en": {
        "page_title": "Cross-Language SEO Intent Tool",
        "main_title": "Cross-Language SEO Intent Tool",
        "subtitle": "Enter a source keyword \u2192 Discover real search terms in the target market \u2192 Deep analysis of search data & intent",
        "settings": "\u2699\ufe0f Settings",
        "ui_lang_label": "Interface Language",
        "api_token_label": "Ahrefs API Token",
        "api_token_help": "Get your API Bearer Token from Ahrefs dashboard",
        "lang_settings": "\U0001f524 Language Settings",
        "source_lang_label": "Source Language (your keyword\u2019s language)",
        "target_country_label": "Target Country / Market",
        "result_settings": "\U0001f4ca Result Settings",
        "result_limit_label": "Max keywords to return",
        "step1_header": "Step 1: Keyword Discovery \u2014 Find real search terms in the target market",
        "input_placeholder": "e.g.: bluetooth headphones, Robot Lawn Mower, SEO tools \u2026",
        "discover_btn": "\U0001f50d Discover Keywords",
        "warn_no_token": "Please enter your Ahrefs API Token in the sidebar.",
        "warn_no_kw": "Please enter a search keyword.",
        "status_translating": "Translating keyword\u2026",
        "status_direct": "Looking up direct translation\u2026",
        "status_related_orig": "Fetching cross-language related terms\u2026",
        "status_related_trans": "Fetching related terms for translation\u2026",
        "status_roots": "Extracting root terms\u2026",
        "status_filter": "Filtering irrelevant keywords\u2026",
        "status_brand": "Filtering brand / product keywords\u2026",
        "status_overview": "Verifying data via Ahrefs Overview\u2026",
        "status_rel_translate": "Translating keywords for relevance scoring\u2026",
        "status_done": "Found {n} target-language candidate keywords (filtered & verified) \u2705",
        "status_none": "No candidate keywords found \u2014 try another keyword",
        "candidates_title": "\U0001f3af Target Keywords \u2014 Select one for deep analysis",
        "candidates_caption": "Discovered via translation, parent topics, suggestions & related terms. Choose the keyword with highest volume that matches your intent.",
        "step2_header": "Step 2: Deep Analysis \u2014 Select a keyword for full data",
        "select_kw_label": "Select keyword for deep analysis",
        "select_kw_help": "Recommend picking the highest-volume keyword",
        "analyze_btn": "\U0001f4ca Deep Analysis",
        "status_overview2": "Fetching keyword overview\u2026",
        "status_overview2_done": "Keyword overview fetched \u2705",
        "status_overview2_err": "No overview data found",
        "overview_title": "\U0001f4cc \u201c{kw}\u201d ({meaning}) search overview in {country}",
        "metric_vol": "Monthly Volume",
        "metric_gvol": "Global Volume",
        "metric_kd": "KD ({label})",
        "metric_tp": "Traffic Potential",
        "metric_cpc": "CPC",
        "label_intent": "Search Intent",
        "label_parent": "Parent Topic",
        "status_related2": "Fetching related keywords\u2026",
        "status_related2_done": "Found {n} related keywords \u2705",
        "status_related2_err": "No related keywords found",
        "related_title": "\U0001f517 Related keywords for \u201c{kw}\u201d",
        "translating_meanings": "Translating keyword meanings\u2026",
        "filter_title": "\U0001f3af Filters",
        "filter_min_vol": "Min Monthly Volume",
        "filter_max_kd": "Max KD",
        "filter_intent": "Search Intent Filter",
        "filter_showing": "Showing **{shown}** / {total} keywords",
        "download_csv": "\U0001f4e5 Download CSV",
        "col_keyword": "Target Keyword",
        "col_meaning": "Meaning ({lang})",
        "col_volume": "Monthly Volume",
        "col_gvolume": "Global Volume",
        "col_kd": "KD",
        "col_kd_level": "KD Level",
        "col_cpc": "CPC ($)",
        "col_tp": "Traffic Potential",
        "col_intent": "Search Intent",
        "col_parent": "Parent Topic",
        "kd_super_easy": "Super Easy",
        "kd_easy": "Easy",
        "kd_medium": "Medium",
        "kd_hard": "Hard",
        "kd_super_hard": "Super Hard",
        "intent_info": "\U0001f50d Informational",
        "intent_nav": "\U0001f9ed Navigational",
        "intent_comm": "\U0001f4b0 Commercial",
        "intent_trans": "\U0001f6d2 Transactional",
        "intent_brand": "\U0001f3f7\ufe0f Branded",
        "intent_local": "\U0001f4cd Local",
        "landing_title": "\U0001f4a1 How to Use",
        "landing_body": """**Step 1 \u2014 Keyword Discovery**
1. Enter your Ahrefs API Token in the sidebar
2. Choose your source language and target country
3. Enter a keyword and click \u201cDiscover Keywords\u201d
4. The tool translates your keyword and uses Ahrefs to find **real search terms used in the target market**

**Step 2 \u2014 Deep Analysis**
1. Pick the highest-volume keyword that matches your intent
2. Click \u201cDeep Analysis\u201d for full data + all related terms

### \U0001f3af Why Two Steps?
> Direct translations are often **not** what target-market users actually search for.
> For example, \u201cRobot Lawn Mower\u201d translates to German \u201cRoboter-Rasenm\u00e4her\u201d (only 70 searches/mo),
> but German users actually search for \u201c**m\u00e4hroboter**\u201d (tens of thousands of searches/mo).
> Ahrefs suggestions help us find the real high-traffic keywords.""",
        "root_found": "Extracted {n} candidate root terms: {terms}",
    },
    "zh": {
        "page_title": "\u8de8\u8bed\u79cd SEO \u610f\u56fe\u67e5\u8bcd\u5de5\u5177",
        "main_title": "\u8de8\u8bed\u79cd SEO \u610f\u56fe\u67e5\u8bcd\u5de5\u5177",
        "subtitle": "\u8f93\u5165\u6e90\u8bed\u8a00\u5173\u952e\u8bcd \u2192 \u667a\u80fd\u53d1\u73b0\u76ee\u6807\u5e02\u573a\u771f\u5b9e\u641c\u7d22\u8bcd \u2192 \u6df1\u5ea6\u5206\u6790\u641c\u7d22\u6570\u636e\u4e0e\u610f\u56fe",
        "settings": "\u2699\ufe0f \u8bbe\u7f6e",
        "ui_lang_label": "\u754c\u9762\u8bed\u8a00",
        "api_token_label": "Ahrefs API Token",
        "api_token_help": "\u5728 Ahrefs \u540e\u53f0\u83b7\u53d6\u4f60\u7684 API Bearer Token",
        "lang_settings": "\U0001f524 \u8bed\u8a00\u8bbe\u7f6e",
        "source_lang_label": "\u6e90\u8bed\u8a00\uff08\u4f60\u8f93\u5165\u5173\u952e\u8bcd\u7684\u8bed\u8a00\uff09",
        "target_country_label": "\u76ee\u6807\u56fd\u5bb6/\u5e02\u573a",
        "result_settings": "\U0001f4ca \u7ed3\u679c\u8bbe\u7f6e",
        "result_limit_label": "\u76f8\u5173\u8bcd\u6570\u91cf\u4e0a\u9650",
        "step1_header": "\u7b2c\u4e00\u6b65\uff1a\u5173\u952e\u8bcd\u53d1\u73b0 \u2014 \u627e\u5230\u76ee\u6807\u5e02\u573a\u771f\u6b63\u7684\u641c\u7d22\u8bcd",
        "input_placeholder": "\u4f8b\u5982\uff1a\u84dd\u7259\u8033\u673a\u3001Robot Lawn Mower\u3001SEO\u5de5\u5177 \u2026",
        "discover_btn": "\U0001f50d \u53d1\u73b0\u5173\u952e\u8bcd",
        "warn_no_token": "\u8bf7\u5728\u5de6\u4fa7\u8fb9\u680f\u8f93\u5165\u4f60\u7684 Ahrefs API Token\u3002",
        "warn_no_kw": "\u8bf7\u8f93\u5165\u641c\u7d22\u5173\u952e\u8bcd\u3002",
        "status_translating": "\u6b63\u5728\u7ffb\u8bd1\u5173\u952e\u8bcd\u2026",
        "status_direct": "\u6b63\u5728\u67e5\u8be2\u76f4\u8bd1\u8bcd\u2026",
        "status_related_orig": "\u6b63\u5728\u83b7\u53d6\u8de8\u8bed\u8a00\u76f8\u5173\u8bcd\u2026",
        "status_related_trans": "\u6b63\u5728\u83b7\u53d6\u76f4\u8bd1\u76f8\u5173\u8bcd\u2026",
        "status_roots": "\u6b63\u5728\u63d0\u53d6\u6838\u5fc3\u8bcd\u6839\u2026",
        "status_filter": "\u6b63\u5728\u8fc7\u6ee4\u65e0\u5173\u5173\u952e\u8bcd\u2026",
        "status_brand": "\u6b63\u5728\u8fc7\u6ee4\u54c1\u724c\u8bcd\u548c\u4ea7\u54c1\u8bcd\u2026",
        "status_overview": "\u6b63\u5728\u901a\u8fc7 Ahrefs Overview \u9a8c\u8bc1\u6570\u636e\u51c6\u786e\u6027\u2026",
        "status_rel_translate": "\u6b63\u5728\u7ffb\u8bd1\u5173\u952e\u8bcd\u4ee5\u8ba1\u7b97\u8bed\u4e49\u76f8\u5173\u6027\u2026",
        "status_done": "\u53d1\u73b0 {n} \u4e2a\u76ee\u6807\u8bed\u79cd\u5019\u9009\u5173\u952e\u8bcd\uff08\u5df2\u8fc7\u6ee4\u975e\u76ee\u6807\u8bed\u79cd\u3001\u5df2\u9a8c\u8bc1\u6570\u636e\uff09\u2705",
        "status_none": "\u672a\u627e\u5230\u5019\u9009\u5173\u952e\u8bcd\uff0c\u8bf7\u5c1d\u8bd5\u5176\u4ed6\u5173\u952e\u8bcd",
        "candidates_title": "\U0001f3af \u5019\u9009\u5173\u952e\u8bcd \u2014 \u8bf7\u9009\u62e9\u4e00\u4e2a\u8fdb\u884c\u6df1\u5ea6\u5206\u6790",
        "candidates_caption": "\u901a\u8fc7\u76f4\u8bd1\u3001\u6bcd\u4e3b\u9898\u3001\u8de8\u8bed\u8a00\u5efa\u8bae\u3001\u8de8\u8bed\u8a00\u76f8\u5173\u8bcd\u7b49\u591a\u7b56\u7565\u7efc\u5408\u53d1\u73b0\u3002\u8bf7\u9009\u62e9\u641c\u7d22\u91cf\u6700\u9ad8\u3001\u6700\u7b26\u5408\u4f60\u610f\u56fe\u7684\u5173\u952e\u8bcd\u3002",
        "step2_header": "\u7b2c\u4e8c\u6b65\uff1a\u6df1\u5ea6\u5206\u6790 \u2014 \u9009\u62e9\u5173\u952e\u8bcd\u83b7\u53d6\u5b8c\u6574\u6570\u636e",
        "select_kw_label": "\u9009\u62e9\u8981\u6df1\u5ea6\u5206\u6790\u7684\u5173\u952e\u8bcd",
        "select_kw_help": "\u5efa\u8bae\u9009\u62e9\u6708\u641c\u7d22\u91cf\u6700\u9ad8\u7684\u5173\u952e\u8bcd",
        "analyze_btn": "\U0001f4ca \u6df1\u5ea6\u5206\u6790\u6b64\u5173\u952e\u8bcd",
        "status_overview2": "\u6b63\u5728\u83b7\u53d6\u5173\u952e\u8bcd\u8be6\u7ec6\u6982\u51b5\u2026",
        "status_overview2_done": "\u5173\u952e\u8bcd\u6982\u51b5\u83b7\u53d6\u5b8c\u6210 \u2705",
        "status_overview2_err": "\u672a\u627e\u5230\u6982\u51b5\u6570\u636e",
        "overview_title": "\U0001f4cc \u300c{kw}\u300d({meaning}) \u5728 {country} \u7684\u641c\u7d22\u6982\u51b5",
        "metric_vol": "\u6708\u641c\u7d22\u91cf",
        "metric_gvol": "\u5168\u7403\u641c\u7d22\u91cf",
        "metric_kd": "\u96be\u5ea6 ({label})",
        "metric_tp": "\u6d41\u91cf\u6f5c\u529b",
        "metric_cpc": "CPC",
        "label_intent": "\u641c\u7d22\u610f\u56fe",
        "label_parent": "\u6bcd\u4e3b\u9898",
        "status_related2": "\u6b63\u5728\u83b7\u53d6\u76f8\u5173\u5173\u952e\u8bcd\u2026",
        "status_related2_done": "\u627e\u5230 {n} \u4e2a\u76f8\u5173\u5173\u952e\u8bcd \u2705",
        "status_related2_err": "\u672a\u627e\u5230\u76f8\u5173\u5173\u952e\u8bcd",
        "related_title": "\U0001f517 \u300c{kw}\u300d\u7684\u76f8\u5173\u5173\u952e\u8bcd",
        "translating_meanings": "\u6b63\u5728\u7ffb\u8bd1\u5173\u952e\u8bcd\u542b\u4e49\u2026",
        "filter_title": "\U0001f3af \u7b5b\u9009",
        "filter_min_vol": "\u6700\u4f4e\u6708\u641c\u7d22\u91cf",
        "filter_max_kd": "\u6700\u9ad8 KD",
        "filter_intent": "\u641c\u7d22\u610f\u56fe\u7b5b\u9009",
        "filter_showing": "\u663e\u793a **{shown}** / {total} \u4e2a\u5173\u952e\u8bcd",
        "download_csv": "\U0001f4e5 \u4e0b\u8f7d CSV",
        "col_keyword": "\u76ee\u6807\u8bed\u79cd\u5173\u952e\u8bcd",
        "col_meaning": "\u542b\u4e49\uff08{lang}\uff09",
        "col_volume": "\u6708\u641c\u7d22\u91cf",
        "col_gvolume": "\u5168\u7403\u641c\u7d22\u91cf",
        "col_kd": "KD",
        "col_kd_level": "KD \u7b49\u7ea7",
        "col_cpc": "CPC ($)",
        "col_tp": "\u6d41\u91cf\u6f5c\u529b",
        "col_intent": "\u641c\u7d22\u610f\u56fe",
        "col_parent": "\u6bcd\u4e3b\u9898",
        "kd_super_easy": "\u6781\u6613",
        "kd_easy": "\u5bb9\u6613",
        "kd_medium": "\u4e2d\u7b49",
        "kd_hard": "\u8f83\u96be",
        "kd_super_hard": "\u6781\u96be",
        "intent_info": "\U0001f50d \u4fe1\u606f\u578b",
        "intent_nav": "\U0001f9ed \u5bfc\u822a\u578b",
        "intent_comm": "\U0001f4b0 \u5546\u4e1a\u578b",
        "intent_trans": "\U0001f6d2 \u4ea4\u6613\u578b",
        "intent_brand": "\U0001f3f7\ufe0f \u54c1\u724c\u578b",
        "intent_local": "\U0001f4cd \u672c\u5730\u578b",
        "landing_title": "\U0001f4a1 \u4f7f\u7528\u8bf4\u660e",
        "landing_body": """**\u7b2c\u4e00\u6b65 \u2014 \u5173\u952e\u8bcd\u53d1\u73b0**
1. \u5728\u5de6\u4fa7\u8fb9\u680f\u8f93\u5165 Ahrefs API Token
2. \u9009\u62e9\u6e90\u8bed\u8a00\u548c\u76ee\u6807\u56fd\u5bb6/\u5e02\u573a
3. \u8f93\u5165\u5173\u952e\u8bcd\uff0c\u70b9\u51fb\u300c\u53d1\u73b0\u5173\u952e\u8bcd\u300d
4. \u5de5\u5177\u4f1a\u7ffb\u8bd1\u4f60\u7684\u5173\u952e\u8bcd\uff0c\u5e76\u901a\u8fc7 Ahrefs \u641c\u7d22\u5efa\u8bae\u627e\u5230**\u76ee\u6807\u5e02\u573a\u7528\u6237\u771f\u6b63\u5728\u641c\u7d22\u7684\u8bcd**

**\u7b2c\u4e8c\u6b65 \u2014 \u6df1\u5ea6\u5206\u6790**
1. \u4ece\u5019\u9009\u5217\u8868\u4e2d\u9009\u62e9\u641c\u7d22\u91cf\u6700\u9ad8\u3001\u6700\u7b26\u5408\u4f60\u610f\u56fe\u7684\u5173\u952e\u8bcd
2. \u70b9\u51fb\u300c\u6df1\u5ea6\u5206\u6790\u300d\u83b7\u53d6\u5b8c\u6574\u6570\u636e + \u6240\u6709\u76f8\u5173\u8bcd

### \U0001f3af \u4e3a\u4ec0\u4e48\u8981\u4e24\u6b65\u8d70\uff1f
> \u76f4\u63a5\u7ffb\u8bd1\u7684\u5173\u952e\u8bcd\u5f80\u5f80**\u4e0d\u662f**\u76ee\u6807\u5e02\u573a\u7528\u6237\u771f\u6b63\u4f7f\u7528\u7684\u641c\u7d22\u8bcd\u3002
> \u4f8b\u5982 \u201cRobot Lawn Mower\u201d \u76f4\u8bd1\u4e3a\u5fb7\u8bed \u201cRoboter-Rasenm\u00e4her\u201d\uff08\u6708\u641c\u91cf\u4ec5 70\uff09\uff0c
> \u4f46\u5fb7\u56fd\u7528\u6237\u771f\u6b63\u641c\u7d22\u7684\u662f \u201c**m\u00e4hroboter**\u201d\uff08\u6708\u641c\u91cf\u53ef\u80fd\u4e0a\u4e07\uff09\u3002
> \u901a\u8fc7 Ahrefs \u641c\u7d22\u5efa\u8bae\uff0c\u6211\u4eec\u80fd\u627e\u5230\u771f\u6b63\u7684\u9ad8\u6d41\u91cf\u5173\u952e\u8bcd\u3002""",
        "root_found": "\u63d0\u53d6\u5230 {n} \u4e2a\u5019\u9009\u6838\u5fc3\u8bcd: {terms}",
    },
}

def T(key: str, **kwargs) -> str:
    """Return UI text in the current interface language."""
    lang = st.session_state.get("ui_lang", "en")
    text = UI.get(lang, UI["en"]).get(key, UI["en"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

# #region agent log
_DBG_LOG = "/Users/issuser/Developer/micro-saas-apps/.cursor/debug-36927c.log"
def _dbg(location, message, data=None, hypothesis_id="?"):
    entry = {"sessionId": "36927c", "timestamp": int(time.time()*1000), "location": location, "message": message, "data": data or {}, "hypothesisId": hypothesis_id}
    with open(_DBG_LOG, "a") as f: f.write(json.dumps(entry, ensure_ascii=False, default=str) + "\n")
# #endregion

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------

AHREFS_BASE = "https://api.ahrefs.com/v3/keywords-explorer"

COUNTRY_OPTIONS = {
    "United States": "us",
    "United Kingdom": "gb",
    "Canada": "ca",
    "Australia": "au",
    "Germany / Deutschland": "de",
    "France": "fr",
    "Spain / España": "es",
    "Italy / Italia": "it",
    "Brazil / Brasil": "br",
    "Japan / 日本": "jp",
    "South Korea / 한국": "kr",
    "China / 中国": "cn",
    "India": "in",
    "Mexico / México": "mx",
    "Netherlands": "nl",
    "Sweden / Sverige": "se",
    "Poland / Polska": "pl",
    "Turkey / Türkiye": "tr",
    "Russia / Россия": "ru",
    "Indonesia": "id",
    "Thailand / ไทย": "th",
    "Vietnam / Việt Nam": "vn",
    "Argentina": "ar",
    "Taiwan / 台灣": "tw",
    "Hong Kong / 香港": "hk",
    "Singapore": "sg",
    "Malaysia": "my",
    "Philippines": "ph",
    "Saudi Arabia": "sa",
    "UAE": "ae",
}

COUNTRY_TO_LANG = {
    "us": "en", "gb": "en", "ca": "en", "au": "en", "in": "en",
    "sg": "en", "ph": "en",
    "de": "de", "fr": "fr", "es": "es", "it": "it", "br": "pt",
    "jp": "ja", "kr": "ko", "cn": "zh-CN", "tw": "zh-TW", "hk": "zh-TW",
    "mx": "es", "nl": "nl", "se": "sv", "pl": "pl", "tr": "tr",
    "ru": "ru", "id": "id", "th": "th", "vn": "vi", "ar": "es",
    "my": "ms", "sa": "ar", "ae": "ar",
}

SOURCE_LANG_OPTIONS = {
    "中文": "zh-CN",
    "English": "en",
    "日本語": "ja",
    "한국어": "ko",
    "Español": "es",
    "Français": "fr",
    "Deutsch": "de",
    "Português": "pt",
    "Русский": "ru",
    "العربية": "ar",
    "Italiano": "it",
    "Nederlands": "nl",
    "Svenska": "sv",
    "Polski": "pl",
    "Türkçe": "tr",
    "Bahasa Indonesia": "id",
    "ไทย": "th",
    "Tiếng Việt": "vi",
    "Bahasa Melayu": "ms",
}

def _intent_labels():
    return {
        "informational": T("intent_info"),
        "navigational": T("intent_nav"),
        "commercial": T("intent_comm"),
        "transactional": T("intent_trans"),
        "branded": T("intent_brand"),
        "local": T("intent_local"),
    }

# ---------------------------------------------------------------------------
# Helper Functions
# ---------------------------------------------------------------------------


def translate_keyword(keyword: str, source_lang: str, target_lang: str) -> str:
    if source_lang == target_lang:
        return keyword
    try:
        return GoogleTranslator(source=source_lang, target=target_lang).translate(keyword)
    except Exception:
        return keyword


def batch_translate(keywords: list[str], from_lang: str, to_lang: str) -> dict[str, str]:
    """Translate a list of keywords, returning {original: translated}."""
    if from_lang == to_lang:
        return {kw: "" for kw in keywords}
    result = {}
    for kw in keywords:
        try:
            result[kw] = GoogleTranslator(source=from_lang, target=to_lang).translate(kw)
        except Exception:
            result[kw] = "—"
    return result


def translation_relevance(translation: str, source_kw: str) -> float:
    """Score how closely a keyword's back-translation matches the source keyword.
    Returns 0.0–1.0.  Higher = closer match."""
    if not translation or translation == "—" or not source_kw:
        return 0.0

    src = source_kw.lower().split()
    trans = translation.lower().split()
    if not src or not trans:
        return 0.0

    stop = {"the", "a", "an", "of", "for", "and", "or", "in", "on", "to",
            "with", "without", "by", "is", "are", "was", "were", "be", "at"}
    src_content = [w for w in src if w not in stop] or src
    trans_content = [w for w in trans if w not in stop] or trans

    def _stem_match(w1, w2):
        if w1 == w2:
            return True
        prefix = min(len(w1), len(w2), 4)
        if prefix >= 4 and w1[:prefix] == w2[:prefix]:
            return True
        return False

    matched = 0
    for sw in src_content:
        for tw in trans_content:
            if _stem_match(sw, tw):
                matched += 1
                break

    coverage = matched / len(src_content)

    extra = max(0, len(trans_content) - len(src_content))
    penalty = extra / (len(trans_content) + len(src_content)) if (len(trans_content) + len(src_content)) > 0 else 0
    return round(coverage * (1 - penalty * 0.3), 4)


def format_intents(intents: dict | None) -> str:
    if not intents:
        return "—"
    labels = _intent_labels()
    active = [labels.get(k, k) for k, v in intents.items() if v]
    return ", ".join(active) if active else "—"


def difficulty_color(val: int | None) -> str:
    if val is None:
        return "gray"
    if val <= 30:
        return "#22c55e"
    if val <= 60:
        return "#eab308"
    return "#ef4444"


def difficulty_label(val: int | None) -> str:
    if val is None:
        return "—"
    if val <= 10:
        return T("kd_super_easy")
    if val <= 30:
        return T("kd_easy")
    if val <= 50:
        return T("kd_medium")
    if val <= 70:
        return T("kd_hard")
    return T("kd_super_hard")


def fmt_number(val) -> str:
    if val is None:
        return "—"
    return f"{val:,}"


ENGLISH_STOPWORDS = {
    "a", "an", "the", "is", "it", "to", "of", "in", "on", "at", "by", "for",
    "or", "and", "but", "not", "no", "so", "if", "as", "do", "am", "be", "he",
    "me", "my", "we", "us", "up", "go", "i", "you", "all", "how", "what",
    "when", "where", "who", "why", "can", "has", "had", "was", "are", "been",
    "will", "with", "that", "this", "from", "they", "them", "then", "than",
    "into", "over", "also", "just", "more", "some", "very", "much", "many",
    "such", "only", "own", "same", "too", "any", "each", "out", "off", "here",
    "there", "about", "which", "their", "would", "could", "should", "does",
    "did", "its", "your", "our", "his", "her", "him", "she", "may", "get",
    "got", "new", "old", "one", "two", "big", "top", "best", "most", "free",
    "app", "online", "near", "now",
}

COMMON_ENGLISH_WORDS = {
    "price", "prices", "review", "reviews", "buy", "buying", "sale", "sales",
    "shop", "shopping", "store", "stores", "compare", "comparison", "cheap",
    "cheapest", "deal", "deals", "offer", "offers", "cost", "costs",
    "affordable", "discount", "order", "purchase", "shipping", "delivery",
    "list", "guide", "tips", "ideas", "video", "videos", "image", "images",
    "photo", "photos", "map", "news", "blog", "forum", "help", "home", "page",
    "site", "website", "download", "login", "sign", "email", "phone",
    "address", "name", "names", "date", "time", "year", "day", "week", "month",
    "number", "size", "type", "types", "part", "parts", "area", "country",
    "city", "world", "test", "testing", "model", "models", "brand", "brands",
    "product", "products", "work", "works", "working", "use", "used", "using",
    "installation", "install", "setup", "set", "find", "found", "look",
    "garden", "yard", "lawn", "grass", "acre", "acres", "field", "outdoor",
    "indoor", "house", "near", "half", "full", "long", "short", "wide",
    "large", "small", "big", "tiny", "heavy", "light", "fast", "slow",
    "electric", "cordless", "wireless", "automatic", "manual", "smart",
    "professional", "commercial", "industrial", "residential", "portable",
    "app", "online", "digital", "robotic", "battery", "power", "powered",
    "gps", "sensor", "camera", "display", "screen", "system", "machine",
    "tool", "tools", "equipment", "device", "devices", "maker", "made",
    "ireland", "germany", "france", "spain", "italy", "usa", "canada",
    "australia", "europe", "china", "japan", "india", "mexico", "brazil",
    "without", "wire", "wires", "cable", "cables", "perimeter",
    "self", "auto", "how", "what", "where", "which", "when", "who", "why",
    "robot", "robots", "mower", "mowers", "mowing", "cutting", "trimmer",
    "mini", "maxi", "pro", "plus", "max", "ultra", "lite", "super", "mega",
    "nano", "micro", "premium", "basic", "standard", "classic", "zero",
    "next", "edge", "core", "flex", "tech", "smart", "hub", "link", "sync",
    "drive", "track", "click", "scan", "mode", "line", "live", "play",
    "open", "data", "code", "wifi", "blue", "green", "red", "black", "white",
    "gold", "silver", "dark", "air", "star", "fire", "sun", "moon", "rain",
    "high", "low", "flat", "deep", "thin", "soft", "hard", "easy", "real",
    "true", "safe", "cool", "warm", "cold", "hot", "wet", "dry", "clean",
    "fresh", "quiet", "silent", "loud", "good", "great", "nice", "fine",
    "best", "worst", "cheap", "rich", "poor", "simple", "double", "single",
    "extra", "multi", "dual", "triple", "total", "prime", "first", "last",
    "only", "just", "very", "much", "many", "more", "less", "same", "other",
    "each", "every", "some", "any", "back", "side", "front", "rear", "under",
    "over", "cross", "round", "square", "turn", "push", "pull", "keep",
    "care", "home", "land", "yard", "acre", "spot", "zone", "farm",
}

# Brand names and product line names (used to filter navigational/branded queries)
KNOWN_BRANDS = {
    # Outdoor power equipment / lawn mowers / robot mowers
    "husqvarna", "gardena", "bosch", "worx", "stihl", "honda", "toro",
    "makita", "ryobi", "ego", "greenworks", "kobalt", "craftsman",
    "dewalt", "milwaukee", "poulan", "ariens", "snapper", "briggs",
    "stratton", "kohler", "karcher", "kärcher", "einhell", "stiga",
    "mountfield", "flymo", "robomow", "ambrogio", "mammotion", "ecovacs",
    "dreame", "irobot", "navimow", "segway", "positec", "mcculloch",
    "alko", "al-ko", "viking", "wolf-garten", "ferrex", "grizzly",
    "yard force", "lawnmaster", "powerworks", "cub cadet", "john deere",
    "black+decker", "decker", "troy-bilt", "dixon", "simplicity", "scag",
    "exmark", "gravely", "ferris", "wright", "dixie", "chopper",
    "shibaura", "zucchetti", "wiper", "belrobotics", "kress",
    # Product line names (robot mowers / outdoor)
    "automower", "landroid", "sileno", "indego", "luba", "yuka", "goat",
    "ceora", "nera", "terra", "miimo", "robolinho", "bigmow", "parcmow",
    "novabot", "lymow", "switchbot",
    # General tech brands
    "samsung", "apple", "google", "amazon", "microsoft", "sony", "lg",
    "philips", "dyson", "miele", "siemens", "braun", "xiaomi", "huawei",
    "lenovo", "asus", "dell", "intel", "nvidia", "amd", "logitech",
    "anker", "bose", "jbl", "harman", "garmin", "fitbit", "gopro",
    "tesla", "bmw", "audi", "mercedes", "volkswagen", "porsche", "volvo",
    "toyota", "hyundai", "kia", "ford", "chevrolet", "nissan", "subaru",
    "ikea", "leroy", "merlin", "obi", "bauhaus", "hornbach",
}


def filter_candidates(candidates: list, target_lang: str, source_kw: str) -> list:
    """Remove English keywords when targeting non-English markets.
    Core rule: if ALL words in a keyword are known English words → reject."""
    if target_lang == "en":
        return candidates

    # Build combined English word set: stopwords + common + source keyword words
    english_set = set(ENGLISH_STOPWORDS) | set(COMMON_ENGLISH_WORDS)
    for w in source_kw.lower().split():
        english_set.add(w)
        if w.endswith("s"):
            english_set.add(w[:-1])
        else:
            english_set.add(w + "s")
        if w.endswith("er"):
            english_set.add(w[:-2])
            english_set.add(w[:-2] + "ing")

    filtered = []
    rejected = []
    for c in candidates:
        kw_lower = c["keyword"].strip().lower()
        words = kw_lower.split()

        # Reject if ALL words are known English words
        if all(w in english_set for w in words):
            rejected.append(kw_lower)
            continue

        # Single-word: reject if it's a short generic word (≤3 chars)
        # unless it's clearly non-English (contains non-ASCII like ä, é, ñ)
        if len(words) == 1 and len(kw_lower) <= 3:
            if kw_lower.isascii():
                rejected.append(kw_lower)
                continue

        filtered.append(c)

    _dbg("filter_candidates", "English filter results", {
        "rejected_count": len(rejected),
        "rejected_sample": rejected[:30],
        "kept_count": len(filtered),
    }, "FILTER")
    return filtered


def filter_brand_keywords(candidates: list) -> list:
    """Remove keywords containing brand names, product lines, or flagged as
    branded by Ahrefs intents. Returns only generic/conceptual keywords."""
    kept = []
    rejected = []
    for c in candidates:
        kw_lower = c["keyword"].strip().lower()
        words = kw_lower.replace("-", " ").split()

        # Signal 1: Ahrefs explicitly flags keyword as branded
        intents = c.get("intents") or {}
        if intents.get("branded"):
            rejected.append((kw_lower, "ahrefs_branded"))
            continue

        # Signal 2: any word in the keyword matches a known brand/product name
        brand_hit = None
        for w in words:
            if w in KNOWN_BRANDS:
                brand_hit = w
                break
        if brand_hit:
            rejected.append((kw_lower, f"known_brand:{brand_hit}"))
            continue

        # Signal 3: keyword contains model-number patterns (e.g. "xs 300", "m600")
        has_model = False
        for w in words:
            if any(ch.isdigit() for ch in w) and len(w) >= 2:
                has_model = True
                break
        if has_model:
            rejected.append((kw_lower, "model_number"))
            continue

        kept.append(c)

    _dbg("filter_brand_keywords", "Brand filter results", {
        "rejected_count": len(rejected),
        "rejected_sample": rejected[:30],
        "kept_count": len(kept),
    }, "BRAND_FILTER")
    return kept


# ---------------------------------------------------------------------------
# Ahrefs API Functions
# ---------------------------------------------------------------------------


def fetch_search_suggestions(api_token: str, keywords: str, country: str, limit: int = 20) -> dict | None:
    """Ahrefs search-suggestions: find what real users actually search for."""
    params = {
        "select": "keyword,volume,difficulty,global_volume,cpc,traffic_potential,intents,parent_topic",
        "country": country,
        "keywords": keywords,
        "limit": limit,
    }
    headers = {"Authorization": f"Bearer {api_token}"}
    # #region agent log
    _dbg("app.py:suggestions:pre", "Suggestions request", {"params": params}, "DISCOVER")
    # #endregion
    try:
        resp = requests.get(f"{AHREFS_BASE}/search-suggestions", params=params, headers=headers, timeout=30)
        # #region agent log
        _dbg("app.py:suggestions:resp", "Suggestions response", {"status": resp.status_code, "body_500": resp.text[:500]}, "DISCOVER")
        # #endregion
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        # #region agent log
        _dbg("app.py:suggestions:err", "Suggestions HTTP error", {"status": e.response.status_code, "body": e.response.text[:300]}, "DISCOVER")
        # #endregion
        if st.session_state.get("ui_lang", "en") == "zh":
            st.error(f"Ahrefs API 错误: {e.response.status_code} — {e.response.text[:300]}")
        else:
            st.error(f"Ahrefs API error: {e.response.status_code} — {e.response.text[:300]}")
        return None
    except Exception as e:
        if st.session_state.get("ui_lang", "en") == "zh":
            st.error(f"请求失败: {e}")
        else:
            st.error(f"Request failed: {e}")
        return None


def fetch_ahrefs_overview(api_token: str, keywords: str, country: str) -> dict | None:
    params = {
        "select": "keyword,volume,difficulty,global_volume,cpc,traffic_potential,intents,parent_topic",
        "country": country,
        "keywords": keywords,
    }
    headers = {"Authorization": f"Bearer {api_token}"}
    # #region agent log
    _dbg("app.py:overview:pre", "Overview request", {"params": params}, "DEEP")
    # #endregion
    try:
        resp = requests.get(f"{AHREFS_BASE}/overview", params=params, headers=headers, timeout=30)
        # #region agent log
        _dbg("app.py:overview:resp", "Overview response", {"status": resp.status_code, "body_500": resp.text[:500]}, "DEEP")
        # #endregion
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if st.session_state.get("ui_lang", "en") == "zh":
            st.error(f"Ahrefs API 错误: {e.response.status_code} — {e.response.text[:300]}")
        else:
            st.error(f"Ahrefs API error: {e.response.status_code} — {e.response.text[:300]}")
        return None
    except Exception as e:
        if st.session_state.get("ui_lang", "en") == "zh":
            st.error(f"请求失败: {e}")
        else:
            st.error(f"Request failed: {e}")
        return None


def fetch_ahrefs_related(api_token: str, keywords: str, country: str, limit: int = 50) -> dict | None:
    params = {
        "select": "keyword,volume,difficulty,global_volume,cpc,traffic_potential,intents",
        "country": country,
        "keywords": keywords,
        "terms": "all",
        "limit": limit,
        "order_by": "volume:desc",
    }
    headers = {"Authorization": f"Bearer {api_token}"}
    # #region agent log
    _dbg("app.py:related:pre", "Related request", {"params": params}, "DEEP")
    # #endregion
    try:
        resp = requests.get(f"{AHREFS_BASE}/related-terms", params=params, headers=headers, timeout=30)
        # #region agent log
        _dbg("app.py:related:resp", "Related response", {"status": resp.status_code, "body_500": resp.text[:500]}, "DEEP")
        # #endregion
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.HTTPError as e:
        if st.session_state.get("ui_lang", "en") == "zh":
            st.error(f"Ahrefs API 错误: {e.response.status_code} — {e.response.text[:300]}")
        else:
            st.error(f"Ahrefs API error: {e.response.status_code} — {e.response.text[:300]}")
        return None
    except Exception as e:
        if st.session_state.get("ui_lang", "en") == "zh":
            st.error(f"请求失败: {e}")
        else:
            st.error(f"Request failed: {e}")
        return None


# ---------------------------------------------------------------------------
# UI
# ---------------------------------------------------------------------------

st.set_page_config(page_title="Cross-Language SEO Intent Tool", page_icon="🌍", layout="wide")

st.markdown(
    """
    <style>
    .main-title {font-size:2.4rem; font-weight:800; background:linear-gradient(90deg,#818cf8,#6366f1,#4f46e5);
        -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin-bottom:0.2rem;}
    .sub-title {font-size:1.05rem; color:#94a3b8; margin-bottom:1.5rem;}
    .metric-card {background:#1e293b; border-radius:12px; padding:1.2rem; text-align:center;
        border:1px solid #334155;}
    .metric-val {font-size:1.8rem; font-weight:700; color:#e2e8f0;}
    .metric-label {font-size:0.85rem; color:#94a3b8; margin-top:0.3rem;}
    div[data-testid="stDataFrame"] table {font-size:0.9rem;}
    .step-header {font-size:1.1rem; font-weight:700; color:#818cf8; margin:1rem 0 0.5rem 0;
        padding:0.5rem 1rem; background:#1e293b; border-radius:8px; border-left:4px solid #6366f1;}
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Session State Init ---
init_db()
ensure_auth_state()

if "discovery_done" not in st.session_state:
    st.session_state.discovery_done = False
if "candidates_df" not in st.session_state:
    st.session_state.candidates_df = None
if "selected_keyword" not in st.session_state:
    st.session_state.selected_keyword = None
if "deep_results" not in st.session_state:
    st.session_state.deep_results = None
if "ui_lang" not in st.session_state:
    st.session_state.ui_lang = "en"
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "allow_guest_mode" not in st.session_state:
    st.session_state.allow_guest_mode = False

user = current_user()
is_logged_in = user is not None

# --- Sidebar ---
with st.sidebar:
    st.markdown(f"### {T('settings')}")

    ui_lang_choice = st.selectbox(
        T("ui_lang_label"),
        ["English", "中文"],
        index=0 if st.session_state.ui_lang == "en" else 1,
    )
    new_lang = "en" if ui_lang_choice == "English" else "zh"
    if new_lang != st.session_state.ui_lang:
        st.session_state.ui_lang = new_lang
        st.rerun()

    if is_logged_in:
        st.success(f"Logged in: {user['email']}")
        st.caption(f"Credits: {user['credits']}")
        if st.button("Logout"):
            logout()
            st.rerun()
        user_api_key = user["api_key"] or ""
        api_token_input = st.text_input(
            "Your Ahrefs API Token (optional)",
            type="password",
            value=user_api_key,
            help="If provided, your own API key is used and credits are not consumed.",
        )
        if api_token_input != user_api_key:
            update_user_api_key(int(user["id"]), api_token_input)
            st.rerun()
    else:
        st.info("Guest mode: 1 free query, 5 rows only.")
        api_token_input = st.text_input(
            "Your Ahrefs API Token (optional)",
            type="password",
            value="",
            help="Guests can also use their own API key.",
        )

    platform_api_key = os.getenv("PLATFORM_AHREFS_KEY", "").strip()
    effective_api_token = (api_token_input or "").strip() or platform_api_key

    st.divider()
    st.markdown(f"### {T('lang_settings')}")
    source_lang_name = st.selectbox(T("source_lang_label"), list(SOURCE_LANG_OPTIONS.keys()), index=1)
    source_lang = SOURCE_LANG_OPTIONS[source_lang_name]

    target_country_name = st.selectbox(T("target_country_label"), list(COUNTRY_OPTIONS.keys()), index=0)
    target_country = COUNTRY_OPTIONS[target_country_name]
    target_lang = COUNTRY_TO_LANG.get(target_country, "en")

    st.divider()
    st.markdown(f"### {T('result_settings')}")
    result_limit = st.slider(T("result_limit_label"), min_value=10, max_value=200, value=50, step=10)

    st.divider()
    st.markdown(
        "<small style='color:#64748b'>Powered by Ahrefs API & Google Translate</small>",
        unsafe_allow_html=True,
    )

# --- Page Header (after sidebar so T() works with selected language) ---
st.markdown(f'<div class="main-title">🌍 {T("main_title")}</div>', unsafe_allow_html=True)
st.markdown(
    f'<div class="sub-title">{T("subtitle")}</div>',
    unsafe_allow_html=True,
)

if not is_logged_in and not st.session_state.allow_guest_mode:
    if not render_auth_gate():
        st.stop()

# ========================================================================
# STEP 1 — Keyword Discovery
# ========================================================================
st.markdown(f'<div class="step-header">{T("step1_header")}</div>', unsafe_allow_html=True)

col_input, col_btn = st.columns([4, 1])
with col_input:
    keyword_input = st.text_input(
        T("step1_header"),
        placeholder=T("input_placeholder"),
        label_visibility="collapsed",
    )
with col_btn:
    discover_clicked = st.button(T("discover_btn"), use_container_width=True, type="primary")

if discover_clicked:
    if not effective_api_token:
        st.warning(T("warn_no_token"))
        st.stop()
    if not keyword_input.strip():
        st.warning(T("warn_no_kw"))
        st.stop()

    credits_used = 0
    if is_logged_in:
        using_own_key = bool((api_token_input or "").strip())
        if not using_own_key:
            if not deduct_credit_if_possible(int(user["id"])):
                st.error("Credits exhausted. Please contact admin to top up.")
                st.stop()
            credits_used = 1
    else:
        if st.session_state.guest_used_free_query:
            st.error("Guest free query already used. Please register/login.")
            st.stop()
        st.session_state.guest_used_free_query = True

    st.session_state.discovery_done = False
    st.session_state.candidates_df = None
    st.session_state.selected_keyword = None
    st.session_state.deep_results = None

    raw_kw = keyword_input.strip()

    # 1a — Translate
    with st.status(T("status_translating"), expanded=True) as status:
        translated = translate_keyword(raw_kw, source_lang, target_lang)
        st.write(f"**{raw_kw}** → **{translated}** ({target_country_name})")
        status.update(label=f"{T('status_translating')} ✅", state="complete")

    # 1b — Multi-strategy keyword discovery
    with st.status(T("status_related_orig"), expanded=True) as status:
        all_candidates = []
        seen = set()

        st.write("1/4 …")
        sug_translated = fetch_search_suggestions(effective_api_token, translated, target_country, limit=20)
        sug_translated_kws = sug_translated.get("keywords", []) if sug_translated else []

        st.write("2/4 …")
        ov_translated = fetch_ahrefs_overview(effective_api_token, translated, target_country)
        direct_kw = None
        if ov_translated and ov_translated.get("keywords"):
            direct_kw = ov_translated["keywords"][0]

        st.write("3/4 …")
        rel_original = fetch_ahrefs_related(effective_api_token, raw_kw, target_country, limit=result_limit)
        rel_original_kws = rel_original.get("keywords", []) if rel_original else []

        st.write("4/4 …")
        rel_translated = fetch_ahrefs_related(effective_api_token, translated, target_country, limit=result_limit)
        rel_translated_kws = rel_translated.get("keywords", []) if rel_translated else []

        parent_topic_kw = None
        if direct_kw and direct_kw.get("parent_topic"):
            pt = direct_kw["parent_topic"]
            ov_parent = fetch_ahrefs_overview(effective_api_token, pt, target_country)
            if ov_parent and ov_parent.get("keywords"):
                parent_topic_kw = ov_parent["keywords"][0]

        def _add(item, source_label):
            kw = item.get("keyword", "").strip()
            if kw and kw not in seen:
                all_candidates.append({**item, "_source": source_label})
                seen.add(kw)

        for item in rel_original_kws:
            _add(item, "related-original")
        for item in rel_translated_kws:
            _add(item, "related-translated")
        if parent_topic_kw:
            _add(parent_topic_kw, "parent-topic")
        if direct_kw:
            _add(direct_kw, "direct")
        for item in sug_translated_kws:
            _add(item, "suggestion")

        st.write(T("status_roots"))
        word_counter = Counter()
        bigram_counter = Counter()
        for c in all_candidates:
            words = c["keyword"].lower().split()
            for w in words:
                if len(w) >= 3 and w not in ENGLISH_STOPWORDS and w not in KNOWN_BRANDS:
                    word_counter[w] += 1
            for i in range(len(words) - 1):
                bg = f"{words[i]} {words[i+1]}"
                bg_set = set(bg.split())
                if not all(w in ENGLISH_STOPWORDS for w in bg.split()) and not (bg_set & KNOWN_BRANDS):
                    bigram_counter[bg] += 1
            pt = c.get("parent_topic")
            if pt:
                pt_words = pt.lower().split()
                for w in pt_words:
                    if len(w) >= 3 and w not in ENGLISH_STOPWORDS and w not in KNOWN_BRANDS:
                        word_counter[w] += 1
                for i in range(len(pt_words) - 1):
                    bg = f"{pt_words[i]} {pt_words[i+1]}"
                    bg_set = set(bg.split())
                    if not (bg_set & KNOWN_BRANDS):
                        bigram_counter[bg] += 1

        # Top frequent unigrams and bigrams (appear in 3+ keywords)
        # Filter out source-language words to only extract target-language roots
        source_words = set(raw_kw.lower().split()) | ENGLISH_STOPWORDS | COMMON_ENGLISH_WORDS
        root_terms = []
        for bg, cnt in bigram_counter.most_common(10):
            bg_words = set(bg.split())
            if cnt >= 2 and bg not in seen and not bg_words.issubset(source_words) and not (bg_words & KNOWN_BRANDS):
                root_terms.append(bg)
            if len(root_terms) >= 5:
                break
        for w, cnt in word_counter.most_common(20):
            if cnt >= 3 and w not in seen and w not in source_words and len(w) >= 4 and w not in KNOWN_BRANDS:
                root_terms.append(w)
            if len(root_terms) >= 12:
                break

        # Build initial topic_words BEFORE root extraction (for validation)
        initial_topic = set()
        for w in translated.lower().split():
            if len(w) >= 2 and w not in KNOWN_BRANDS:
                initial_topic.add(w)
        if direct_kw and direct_kw.get("parent_topic"):
            for w in direct_kw["parent_topic"].lower().split():
                if len(w) >= 2 and w not in KNOWN_BRANDS:
                    initial_topic.add(w)
        for w, cnt in word_counter.most_common(10):
            if cnt >= 3 and w not in source_words and w not in KNOWN_BRANDS:
                initial_topic.add(w)

        if root_terms:
            st.write(T("root_found", n=len(root_terms), terms=", ".join(root_terms[:5])))
            root_csv = ",".join(root_terms)
            root_data = fetch_ahrefs_overview(effective_api_token, root_csv, target_country)
            if root_data and root_data.get("keywords"):
                for item in root_data["keywords"]:
                    if not (item.get("volume") and item["volume"] > 0):
                        continue
                    kw = item.get("keyword", "")
                    pt = (item.get("parent_topic") or "").lower()
                    # Only add if the keyword itself or its parent_topic
                    # overlaps with initial topic words (prevents "mini" → "e mini cooper")
                    kw_words = set(kw.lower().split())
                    pt_words = set(pt.split())
                    if (kw_words & initial_topic) or (pt_words & initial_topic):
                        _add(item, "root-extraction")

        # #region agent log
        _dbg("app.py:discovery:roots", "Root word extraction", {
            "top_words": word_counter.most_common(10),
            "top_bigrams": bigram_counter.most_common(5),
            "root_terms_queried": root_terms,
            "candidates_after_roots": len(all_candidates),
        }, "ROOTS")
        # #endregion

        pre_filter_count = len(all_candidates)

        st.write(T("status_filter"))
        all_candidates = filter_candidates(all_candidates, target_lang, raw_kw)

        st.write(T("status_brand"))
        pre_brand_count = len(all_candidates)
        all_candidates = filter_brand_keywords(all_candidates)

        # #region agent log
        _dbg("app.py:discovery:merged", "Candidates after language + brand filter", {
            "before_filter": pre_filter_count,
            "after_lang_filter": pre_brand_count,
            "after_brand_filter": len(all_candidates),
            "rel_original": len(rel_original_kws),
            "rel_translated": len(rel_translated_kws),
            "top5_kws": [c["keyword"] for c in sorted(all_candidates, key=lambda x: x.get("volume") or 0, reverse=True)[:5]],
        }, "MULTI")
        # #endregion

        # --- Re-query through overview for accurate data ---
        if all_candidates:
            st.write(T("status_overview"))
            kw_csv = ",".join(c["keyword"] for c in all_candidates[:result_limit])
            accurate_data = fetch_ahrefs_overview(effective_api_token, kw_csv, target_country)
            if accurate_data and accurate_data.get("keywords"):
                accurate_map = {item["keyword"]: item for item in accurate_data["keywords"]}
                for c in all_candidates:
                    acc = accurate_map.get(c["keyword"])
                    if acc:
                        for field in ("volume", "difficulty", "global_volume", "cpc",
                                      "traffic_potential", "intents", "parent_topic"):
                            if acc.get(field) is not None:
                                c[field] = acc[field]

        # --- Translation-based relevance scoring ---
        # Translate candidate keywords back to source language, then compare
        # with source keyword to determine true semantic relevance.
        if all_candidates:
            st.write(T("status_rel_translate"))
            kw_list_for_rel = [c["keyword"] for c in all_candidates]
            back_translations = batch_translate(kw_list_for_rel, target_lang, source_lang)

            for c in all_candidates:
                bt = back_translations.get(c["keyword"], "")
                c["_back_translation"] = bt
                c["_rel_score"] = translation_relevance(bt, raw_kw)

        # #region agent log
        _dbg("app.py:discovery:translations", "Back-translations for relevance", {
            "sample": [(c["keyword"], c.get("_back_translation", ""), c.get("_rel_score", 0))
                       for c in sorted(all_candidates, key=lambda x: x.get("_rel_score", 0), reverse=True)[:10]],
        }, "TRANSLATION")
        # #endregion

        # REMOVE keywords with zero relevance to source keyword
        all_candidates = [c for c in all_candidates if c.get("_rel_score", 0) > 0]

        # Sort: PRIMARY = translation relevance DESC, SECONDARY = volume DESC
        all_candidates.sort(
            key=lambda x: (x.get("_rel_score", 0), x.get("volume") or 0),
            reverse=True,
        )

        # #region agent log
        _dbg("app.py:discovery:relevance", "After relevance filter + sort", {
            "remaining": len(all_candidates),
            "top5": [(c["keyword"], c.get("_rel_score", 0), c.get("_back_translation", ""), c.get("volume")) for c in all_candidates[:5]],
            "bottom5": [(c["keyword"], c.get("_rel_score", 0), c.get("_back_translation", ""), c.get("volume")) for c in all_candidates[-5:]],
        }, "RELEVANCE")
        # #endregion

        # --- Apply result limit ---
        all_candidates = all_candidates[:result_limit]

        total_found = len(all_candidates)
        if not is_logged_in and total_found > 5:
            all_candidates = all_candidates[:5]
            st.info(f"Guest preview: showing 5/{total_found}. Register/login to unlock full table.")
        log_query(
            int(user["id"]) if is_logged_in else None,
            st.session_state.session_id,
            raw_kw,
            target_country,
            credits_used=credits_used,
        )
        if total_found > 0:
            status.update(label=T("status_done", n=total_found), state="complete")
        else:
            status.update(label=T("status_none"), state="error")

    if all_candidates:
        meanings = {c["keyword"]: c.get("_back_translation", "—") for c in all_candidates}

        rows = []
        for c in all_candidates:
            kw = c["keyword"]
            rows.append({
                "keyword": kw,
                "meaning": meanings.get(kw, "—"),
                "volume": c.get("volume"),
                "global_volume": c.get("global_volume"),
                "kd": c.get("difficulty"),
                "kd_level": difficulty_label(c.get("difficulty")),
                "cpc": round(c["cpc"] / 100, 2) if c.get("cpc") is not None else None,
                "traffic_potential": c.get("traffic_potential"),
                "intent": format_intents(c.get("intents")),
                "parent_topic": c.get("parent_topic") or "—",
            })

        df = pd.DataFrame(rows)
        st.session_state.candidates_df = df
        st.session_state.discovery_done = True

# --- Display candidates if available ---
if st.session_state.discovery_done and st.session_state.candidates_df is not None:
    df = st.session_state.candidates_df

    st.markdown("---")
    st.markdown(f"### {T('candidates_title')}")
    st.caption(T("candidates_caption"))

    st.dataframe(
        df,
        use_container_width=True,
        height=min(400, 50 + len(df) * 35),
        column_config={
            "keyword": st.column_config.TextColumn(label=T("col_keyword")),
            "meaning": st.column_config.TextColumn(label=T("col_meaning", lang=source_lang_name)),
            "volume": st.column_config.NumberColumn(label=T("col_volume"), format="%d"),
            "global_volume": st.column_config.NumberColumn(label=T("col_gvolume"), format="%d"),
            "kd": st.column_config.ProgressColumn(label=T("col_kd"), min_value=0, max_value=100, format="%d"),
            "kd_level": st.column_config.TextColumn(label=T("col_kd_level")),
            "cpc": st.column_config.NumberColumn(label=T("col_cpc"), format="$%.2f"),
            "traffic_potential": st.column_config.NumberColumn(label=T("col_tp"), format="%d"),
            "intent": st.column_config.TextColumn(label=T("col_intent")),
            "parent_topic": st.column_config.TextColumn(label=T("col_parent")),
        },
    )

    if is_logged_in:
        # ========================================================================
        # STEP 2 — Deep Analysis on selected keyword
        # ========================================================================
        st.markdown(f'<div class="step-header">{T("step2_header")}</div>', unsafe_allow_html=True)

        kw_options = df["keyword"].tolist()

        vol_col = df["volume"].fillna(0)
        best_idx = int(vol_col.idxmax()) if len(vol_col) > 0 else 0

        selected = st.selectbox(
            T("select_kw_label"),
            kw_options,
            index=best_idx,
            help=T("select_kw_help"),
        )

        analyze_clicked = st.button(T("analyze_btn"), use_container_width=True, type="primary")

        if analyze_clicked and selected:
            if not effective_api_token:
                st.warning(T("warn_no_token"))
                st.stop()

        # 2a — Overview
            with st.status(T("status_overview2"), expanded=True) as status:
                overview_data = fetch_ahrefs_overview(effective_api_token, selected, target_country)
            if overview_data and overview_data.get("keywords"):
                kw_info = overview_data["keywords"][0]
                status.update(label=T("status_overview2_done"), state="complete")
            else:
                kw_info = None
                status.update(label=T("status_overview2_err"), state="error")

            if kw_info:
                selected_meaning = batch_translate([selected], target_lang, source_lang).get(selected, "—")

            st.markdown("---")
            st.markdown(f"### {T('overview_title', kw=selected, meaning=selected_meaning, country=target_country_name)}")

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                vol = kw_info.get("volume")
                st.markdown(
                    f'<div class="metric-card"><div class="metric-val">{fmt_number(vol)}</div>'
                    f'<div class="metric-label">{T("metric_vol")}</div></div>',
                    unsafe_allow_html=True,
                )
            with c2:
                gv = kw_info.get("global_volume")
                st.markdown(
                    f'<div class="metric-card"><div class="metric-val">{fmt_number(gv)}</div>'
                    f'<div class="metric-label">{T("metric_gvol")}</div></div>',
                    unsafe_allow_html=True,
                )
            with c3:
                diff = kw_info.get("difficulty")
                color = difficulty_color(diff)
                label = difficulty_label(diff)
                st.markdown(
                    f'<div class="metric-card"><div class="metric-val" style="color:{color}">'
                    f'{diff if diff is not None else "—"}</div>'
                    f'<div class="metric-label">{T("metric_kd", label=label)}</div></div>',
                    unsafe_allow_html=True,
                )
            with c4:
                tp = kw_info.get("traffic_potential")
                st.markdown(
                    f'<div class="metric-card"><div class="metric-val">{fmt_number(tp)}</div>'
                    f'<div class="metric-label">{T("metric_tp")}</div></div>',
                    unsafe_allow_html=True,
                )
            with c5:
                cpc_val = kw_info.get("cpc")
                cpc_display = f"${cpc_val / 100:.2f}" if cpc_val is not None else "—"
                st.markdown(
                    f'<div class="metric-card"><div class="metric-val">{cpc_display}</div>'
                    f'<div class="metric-label">{T("metric_cpc")}</div></div>',
                    unsafe_allow_html=True,
                )

            intent_str = format_intents(kw_info.get("intents"))
            parent = kw_info.get("parent_topic") or "—"
            st.markdown(f"**{T('label_intent')}:** {intent_str} &nbsp;&nbsp;|&nbsp;&nbsp; **{T('label_parent')}:** {parent}")

        # 2b — Related Terms
            with st.status(T("status_related2"), expanded=True) as status:
                related_data = fetch_ahrefs_related(effective_api_token, selected, target_country, limit=result_limit)
            if related_data and related_data.get("keywords"):
                related_kws = related_data["keywords"]
                status.update(label=T("status_related2_done", n=len(related_kws)), state="complete")
            else:
                related_kws = []
                status.update(label=T("status_related2_err"), state="error")

            if related_kws:
                st.markdown("---")
                st.markdown(f"### {T('related_title', kw=selected)}")

            with st.spinner(T("translating_meanings")):
                rel_kw_list = [item["keyword"] for item in related_kws]
                rel_meanings = batch_translate(rel_kw_list, target_lang, source_lang)

            labels = _intent_labels()
            rows = []
            for item in related_kws:
                kw = item.get("keyword", "")
                intents = item.get("intents")
                active_intents = []
                if intents:
                    for k, v in intents.items():
                        if v:
                            active_intents.append(labels.get(k, k))
                rows.append({
                    "keyword": kw,
                    "meaning": rel_meanings.get(kw, "—"),
                    "volume": item.get("volume"),
                    "global_volume": item.get("global_volume"),
                    "kd": item.get("difficulty"),
                    "kd_level": difficulty_label(item.get("difficulty")),
                    "cpc": round(item["cpc"] / 100, 2) if item.get("cpc") is not None else None,
                    "traffic_potential": item.get("traffic_potential"),
                    "intent": ", ".join(active_intents) if active_intents else "—",
                })

            rel_df = pd.DataFrame(rows)

            st.markdown(f"#### {T('filter_title')}")
            fcol1, fcol2, fcol3 = st.columns(3)
            with fcol1:
                min_vol = st.number_input(T("filter_min_vol"), min_value=0, value=0, step=10)
            with fcol2:
                max_diff = st.number_input(T("filter_max_kd"), min_value=0, max_value=100, value=100, step=5)
            with fcol3:
                intent_filter = st.multiselect(T("filter_intent"), list(_intent_labels().values()))

            filtered = rel_df.copy()
            if min_vol > 0:
                filtered = filtered[filtered["volume"].fillna(0) >= min_vol]
            if max_diff < 100:
                filtered = filtered[filtered["kd"].fillna(0) <= max_diff]
            if intent_filter:
                mask = filtered["intent"].apply(
                    lambda x: any(intent in x for intent in intent_filter)
                )
                filtered = filtered[mask]

            st.markdown(T("filter_showing", shown=len(filtered), total=len(rel_df)))

            st.dataframe(
                filtered,
                use_container_width=True,
                height=500,
                column_config={
                    "keyword": st.column_config.TextColumn(label=T("col_keyword")),
                    "meaning": st.column_config.TextColumn(label=T("col_meaning", lang=source_lang_name)),
                    "volume": st.column_config.NumberColumn(label=T("col_volume"), format="%d"),
                    "global_volume": st.column_config.NumberColumn(label=T("col_gvolume"), format="%d"),
                    "kd": st.column_config.ProgressColumn(label=T("col_kd"), min_value=0, max_value=100, format="%d"),
                    "kd_level": st.column_config.TextColumn(label=T("col_kd_level")),
                    "cpc": st.column_config.NumberColumn(label=T("col_cpc"), format="$%.2f"),
                    "traffic_potential": st.column_config.NumberColumn(label=T("col_tp"), format="%d"),
                    "intent": st.column_config.TextColumn(label=T("col_intent")),
                },
            )

            csv_data = filtered.to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                label=T("download_csv"),
                data=csv_data,
                file_name=f"seo_keywords_{selected}_{target_country}.csv",
                mime="text/csv",
            )
    else:
        st.info("Register/login to unlock deep analysis and CSV download.")

# --- Landing page ---
if not st.session_state.discovery_done:
    st.markdown("---")
    st.markdown(f"### {T('landing_title')}")
    st.markdown(T("landing_body"))
