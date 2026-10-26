"""Food Verse AI - Main Streamlit application."""
from __future__ import annotations

import streamlit as st

from config import AppConfig, load_env_config, TABS
from styles import CSS
from ai_client import AIClient

from tabs.tab1_food_recognition import render as tab1_render
from tabs.tab2_freshness import render as tab2_render
from tabs.tab3_kitchen_hygiene import render as tab3_render
from tabs.tab4_recipe_assistant import render as tab4_render
from tabs.tab5_meal_planner import render as tab5_render

TAB_RENDERERS = {
    "tab1": tab1_render,
    "tab2": tab2_render,
    "tab3": tab3_render,
    "tab4": tab4_render,
    "tab5": tab5_render,
}

PLATFORM_ID = "6ac4ca021dcde6d7857c169a"

_TAB_ICONS = {
    "tab1": "🍽️",
    "tab2": "🧪",
    "tab3": "🧼",
    "tab4": "👨‍🍳",
    "tab5": "📅",
}


def _init_session_state(config: AppConfig) -> None:
    if "config" not in st.session_state:
        st.session_state["config"] = config
    if "active_tab" not in st.session_state:
        st.session_state["active_tab"] = "tab1"
    if "ai_client" not in st.session_state:
        st.session_state["ai_client"] = AIClient(config)


def _config_form(active_cfg: AppConfig, key_prefix: str = "cfg") -> None:
    provider = st.selectbox(
        "AI Provider",
        ["Demo / Fallback Mode", "Gemini (Google)", "Groq"],
        index=["Demo / Fallback Mode", "Gemini (Google)", "Groq"].index(active_cfg.provider)
        if active_cfg.provider in ["Demo / Fallback Mode", "Gemini (Google)", "Groq"]
        else 0,
        key=f"{key_prefix}_provider",
    )
    api_key = st.text_input(
        "API Key",
        type="password",
        value=st.session_state.get(f"{key_prefix}_api_key", active_cfg.api_key or ""),
        placeholder="sk-...",
        help="GOOGLE_API_KEY for Gemini, GROQ_API_KEY for Groq",
        key=f"{key_prefix}_api_key_input",
    )
    model_name = st.text_input(
        "Model (optional)",
        value=st.session_state.get(f"{key_prefix}_model", active_cfg.model_name or ""),
        placeholder="e.g. gemini-1.5-flash / llama-3.1-8b-instant",
        key=f"{key_prefix}_model",
    )
    temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        float(active_cfg.temperature),
        0.1,
        key=f"{key_prefix}_temp",
    )
    enable_fallback = st.checkbox(
        "Enable demo fallback",
        value=active_cfg.enable_fallback,
        key=f"{key_prefix}_fallback",
    )

    if st.button("Apply Configuration", key=f"{key_prefix}_apply", use_container_width=True):
        st.session_state["config"] = AppConfig(
            provider=provider,
            api_key=api_key,
            model_name=(st.session_state.get(f"{key_prefix}_model") or None) or None,
            temperature=temperature,
            enable_fallback=enable_fallback,
            demo_mode=(provider == "Demo / Fallback Mode" or not api_key),
        )
        st.session_state["ai_client"] = AIClient(st.session_state["config"])
        st.success("Configuration applied.")
        st.rerun()


@st.dialog("Response Configuration")
def _config_dialog(config: AppConfig) -> None:
    active_cfg: AppConfig = st.session_state.get("config", config)
    _config_form(active_cfg, key_prefix="dialog")
    if st.button("Close", key="dialog_close", use_container_width=True):
        st.rerun()


def _render_top_nav() -> str:
    """Dark top navigation bar with hover-expanding tabs. No sidebar."""
    active_tab = st.session_state.get("active_tab", "tab1")

    # Sync from query params (e.g. direct link or programmatic nav)
    query_tab = st.query_params.get("tab")
    if query_tab and query_tab in TABS and query_tab != active_tab:
        st.session_state["active_tab"] = query_tab
        active_tab = query_tab

    items_html = []
    for i, (key, label) in enumerate(TABS.items()):
        is_active = "active" if active_tab == key else ""
        items_html.append(
            f'<a href="?tab={key}" class="fv-nav-item {is_active}" '
            f'title="{label}">'
            f'<span class="fv-nav-marker">{_TAB_ICONS.get(key, "•")}</span>'
            f'<span class="fv-nav-short">Tab {i + 1}</span>'
            f'<span class="fv-nav-full">{label}</span>'
            f'</a>'
        )
    nav_html = (
        '<div class="fv-topnav">' + "".join(items_html) + "</div>"
    )
    st.markdown(nav_html, unsafe_allow_html=True)

    return st.session_state.get("active_tab", "tab1")


def main() -> None:
    st.set_page_config(
        page_title="Food Verse AI - Multimodal Food Intelligence Agent",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    base_config = load_env_config()
    _init_session_state(base_config)
    config: AppConfig = st.session_state.get("config", base_config)
    ai_client: AIClient = st.session_state.get("ai_client", AIClient(config))

    active_tab = _render_top_nav()

    # Top-right "Response Config" button in the main area
    config_cols = st.columns([6, 1])
    with config_cols[1]:
        if st.button("⚙️ Response Config", key="open_response_config",
                     help="Configure AI provider, model and temperature"):
            _config_dialog(config)

    # Header
    st.markdown(
        '<div class="fv-app-title">Food Verse AI</div>'
        '<div class="fv-subtitle">Multimodal Food Intelligence Agent • '
        'Recognition • Freshness • Hygiene • Recipes • Meal Planning</div>',
        unsafe_allow_html=True,
    )

    # Demo-mode notice
    if config.demo_mode:
        st.markdown(
            '<div class="fv-alert info">'
            '<strong>Demo / Fallback Mode active.</strong> No AI provider configured. '
            'Heuristic estimates are used. Click <b>Response Config</b> to add a Gemini or Groq API key.'
            '</div>', unsafe_allow_html=True,
        )

    renderer = TAB_RENDERERS.get(active_tab, tab1_render)
    try:
        renderer(config, ai_client)
    except Exception as exc:  # pragma: no cover - defensive UI boundary
        st.error(f"Tab rendering error: {exc}")
        st.exception(exc)

    st.markdown("---")
    st.markdown(
        '<div style="color:#64748b;font-size:0.75rem;text-align:center;">'
        'Food Verse AI — Multimodal Food Intelligence Agent • Platform ID: '
        f'{PLATFORM_ID} • Streamlit Community Cloud ready</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
