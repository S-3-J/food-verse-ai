"""Food Verse AI - Main Streamlit application."""
from __future__ import annotations

from typing import Optional

import streamlit as st

from config import (
    AppConfig,
    PLATFORM_ID,
    TAB_META,
    TABS,
    default_model_for,
    load_env_config,
    provider_api_key,
)
from styles import CSS
from ai_client import AIClient
from ui import (
    brand_mark,
    capability_cards,
    hero,
    how_it_works,
    page_header,
    quota_chip,
    status_chip,
    topbar,
)

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

PROVIDER_OPTIONS = ["Demo / Fallback Mode", "Gemini (Google)", "Groq"]


def _init_session_state(config: AppConfig) -> None:
    if "config" not in st.session_state:
        st.session_state["config"] = config
    if "view" not in st.session_state:
        deep_link = st.query_params.get("tab", "")
        st.session_state["view"] = deep_link if deep_link in TAB_META else "home"
    if "ai_client" not in st.session_state:
        st.session_state["ai_client"] = AIClient(config)
    for stale_key in ("cfg_model", "dialog_model"):
        st.session_state.pop(stale_key, None)


def _navigate(view: str) -> None:
    """Set the active view and keep the URL in sync for shareable links."""
    st.session_state["view"] = view
    if view == "home":
        try:
            del st.query_params["tab"]
        except Exception:
            pass
    elif st.query_params.get("tab") != view:
        st.query_params["tab"] = view


def _model_caption(provider: str) -> str:
    """Read-only description of the model that the given provider will use."""
    model = default_model_for(provider)
    if model:
        return f"Model: `{model}` — set by the provider's model secret, not editable here."
    return "Model: not configured for this provider — the app will fall back to heuristic results."


def _config_form(active_cfg: AppConfig, key_prefix: str = "cfg") -> None:
    provider = st.selectbox(
        "AI Provider",
        PROVIDER_OPTIONS,
        index=PROVIDER_OPTIONS.index(active_cfg.provider)
        if active_cfg.provider in PROVIDER_OPTIONS
        else 0,
        key=f"{key_prefix}_provider",
    )
    typed_key = ""
    if active_cfg.allow_user_api_key:
        typed_key = st.text_input(
            "Your API Key (optional)",
            type="password",
            value="",
            placeholder="Leave empty to use the server-managed key",
            help="Stored in this browser session only — never written to disk.",
            key=f"{key_prefix}_api_key_input",
        )
        st.caption("Your key is kept in this session only. Leave the field empty to use the server key.")
    else:
        st.markdown(
            '<div class="fv-alert info">🔒 <strong>Server-managed key in use.</strong> '
            'The API key stays on the server and is never displayed in the browser. '
            'Set <code>ALLOW_USER_API_KEY=true</code> to let visitors bring their own key.</div>',
            unsafe_allow_html=True,
        )
    st.caption(_model_caption(provider))
    temperature = st.slider(
        "Temperature",
        0.0,
        1.0,
        float(active_cfg.temperature),
        0.1,
        help="Lower values are more deterministic; higher values are more creative.",
        key=f"{key_prefix}_temp",
    )
    enable_fallback = st.checkbox(
        "Enable demo fallback",
        value=active_cfg.enable_fallback,
        help="Fall back to visual heuristics if the provider call fails.",
        key=f"{key_prefix}_fallback",
    )

    if st.button("Apply Configuration", key=f"{key_prefix}_apply", width="stretch"):
        typed = (typed_key or "").strip()
        if typed:
            api_key = typed
        elif provider == active_cfg.provider:
            api_key = active_cfg.api_key or provider_api_key(provider)
        else:
            api_key = provider_api_key(provider)
        model = default_model_for(provider)
        st.session_state["config"] = AppConfig(
            provider=provider,
            api_key=api_key,
            model_name=model or "",
            temperature=temperature,
            enable_fallback=enable_fallback,
            demo_mode=(provider == "Demo / Fallback Mode" or not api_key or not model),
            allow_user_api_key=active_cfg.allow_user_api_key,
            max_runs_per_session=active_cfg.max_runs_per_session,
        )
        st.session_state["ai_client"] = AIClient(st.session_state["config"])
        st.success("Configuration applied.")
        st.rerun()


@st.dialog("Response Configuration", width="large")
def _config_dialog(config: AppConfig) -> None:
    active_cfg: AppConfig = st.session_state.get("config", config)
    _config_form(active_cfg, key_prefix="dialog")
    if st.button("Close", key="dialog_close", width="stretch"):
        st.rerun()


def _provider_card(config: AppConfig) -> None:
    mode_label = "Demo / heuristic mode" if config.demo_mode else "Live provider"
    model = config.model_name or ("heuristics (no model)" if config.demo_mode else "default model")
    st.markdown(
        '<div class="fv-model-card">'
        '<div class="m-label">Active model</div>'
        f'<div class="m-value">{config.provider}</div>'
        f'<div class="m-sub">{mode_label} · {model}</div>'
        '</div>',
        unsafe_allow_html=True,
    )
    quota_chip(config)


def _render_sidebar(config: AppConfig) -> None:
    view = st.session_state.get("view", "home")

    with st.sidebar:
        brand_mark()

        st.markdown('<div class="fv-nav-label">Workspace</div>', unsafe_allow_html=True)
        st.button(
            "🏠  Overview",
            key="nav_home",
            on_click=_navigate,
            args=("home",),
            type="primary" if view == "home" else "secondary",
            width="stretch",
        )
        for key, meta in TAB_META.items():
            st.button(
                f'{meta["icon"]}  {meta["title"]}',
                key=f"nav_{key}",
                on_click=_navigate,
                args=(key,),
                type="primary" if view == key else "secondary",
                width="stretch",
                help=meta["blurb"],
            )

        st.markdown('<div class="fv-nav-label">Model</div>', unsafe_allow_html=True)
        _provider_card(config)
        if st.button("⚙️  Response Config", key="open_response_config", width="stretch"):
            _config_dialog(config)


def _render_home(config: AppConfig) -> None:
    if config.demo_mode:
        mode_label = "Demo / heuristic mode"
        provider_label = "Visual estimates"
        model_label = "Heuristic estimates — no model configured"
    else:
        mode_label = "Live analysis"
        provider_label = config.provider
        model_label = config.model_name or "default model"
    hero(provider_label, mode_label, model_label)

    cta, spacer = st.columns([1, 3])
    with cta:
        st.button(
            "Start with Food Recognition",
            key="home_cta",
            on_click=_navigate,
            args=("tab1",),
            type="primary",
            width="stretch",
        )
    with spacer:
        st.markdown("", unsafe_allow_html=True)

    st.markdown('<div class="fv-section-title">🧭 What you can do</div>', unsafe_allow_html=True)
    capability_cards(_navigate)

    st.markdown("", unsafe_allow_html=True)
    st.markdown('<div class="fv-section-title">⚡ How it works</div>', unsafe_allow_html=True)
    how_it_works()

    st.markdown("", unsafe_allow_html=True)
    if config.demo_mode:
        st.markdown(
            '<div class="fv-alert info">'
            '<strong>Demo / Fallback Mode is active.</strong> Results come from visual heuristics. '
            'Open <b>Response Config</b> in the sidebar to add a Gemini or Groq API key.'
            '</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="fv-alert success">'
            f'<strong>{config.provider} is connected.</strong> Analysis uses live model responses. '
            'Results remain estimates and should be verified before use in clinical or safety decisions.'
            '</div>',
            unsafe_allow_html=True,
        )


def _render_workflow(view: str, config: AppConfig, ai_client: AIClient) -> None:
    meta = TAB_META[view]
    topbar(meta["title"], crumb="Overview")
    page_header(
        meta["icon"],
        meta["title"],
        TABS[view].split(". ", 1)[-1],
        right=f'Assistant: {meta["persona"]}',
    )

    if config.demo_mode:
        st.markdown(
            '<div class="fv-alert info"><strong>Demo / Fallback Mode active.</strong> '
            'Heuristic estimates are used — configure a provider in the sidebar for live analysis.'
            '</div>',
            unsafe_allow_html=True,
        )

    renderer = TAB_RENDERERS.get(view, tab1_render)
    try:
        renderer(config, ai_client)
    except Exception as exc:  # pragma: no cover - defensive UI boundary
        st.error("This workflow could not be completed. Please try again.")
        with st.expander("Technical details"):
            st.exception(exc)


def main() -> None:
    st.set_page_config(
        page_title="Food Verse AI - Multimodal Food Intelligence Agent",
        page_icon="🍽️",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(CSS, unsafe_allow_html=True)

    base_config = load_env_config()
    _init_session_state(base_config)
    config: AppConfig = st.session_state.get("config", base_config)
    ai_client: AIClient = st.session_state.get("ai_client", AIClient(config))

    _render_sidebar(config)

    view = st.session_state.get("view", "home")
    if view in TAB_META:
        _render_workflow(view, config, ai_client)
    else:
        _render_home(config)

    st.markdown(
        '<div class="fv-footer">'
        'Food Verse AI — Multimodal Food Intelligence Agent • Platform ID: '
        f'{PLATFORM_ID} • Estimates only, verify before safety-critical use.'
        '</div>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
