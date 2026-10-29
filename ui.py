"""Food Verse AI - Shared UI primitives (brand, headers, chips, cards, empty states)."""
from __future__ import annotations

import json
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple

import streamlit as st

from config import TAB_META


def brand_mark(subtitle: str = "Multimodal Food Intelligence") -> None:
    """Sidebar brand lockup."""
    st.markdown(
        '<div class="fv-brand">'
        '<div class="fv-brand-mark">🍽️</div>'
        '<div>'
        '<div class="fv-brand-name">Food Verse AI</div>'
        f'<div class="fv-brand-sub">{subtitle}</div>'
        '</div></div>',
        unsafe_allow_html=True,
    )


def status_chip(label: str, tone: str = "neutral") -> None:
    """Small pill used for provider status, personas and metadata."""
    st.markdown(f'<span class="fv-chip {tone}">{label}</span>', unsafe_allow_html=True)


def page_header(
    icon: str,
    title: str,
    subtitle: str,
    right: Optional[str] = None,
    right_tone: str = "info",
) -> None:
    """Consistent page title block with an optional right-hand chip."""
    with st.container(key="fv_page_head"):
        left, right_col = st.columns([4, 1], vertical_alignment="center")
        with left:
            st.markdown(
                f'<div class="fv-page-title"><span class="fv-page-icon">{icon}</span>{title}</div>'
                f'<div class="fv-page-sub">{subtitle}</div>',
                unsafe_allow_html=True,
            )
        with right_col:
            if right:
                status_chip(right, right_tone)


def topbar(current: str, crumb: str = "Overview") -> None:
    """Breadcrumb strip shown above a workflow."""
    with st.container(key="fv_topbar"):
        left, right = st.columns([3, 1], vertical_alignment="center")
        with left:
            st.markdown(
                f'<div class="fv-breadcrumb">{crumb} &nbsp;›&nbsp; <span class="cur">{current}</span></div>',
                unsafe_allow_html=True,
            )
        with right:
            st.markdown("", unsafe_allow_html=True)


def section_title(icon: str, title: str) -> None:
    st.markdown(f'<div class="fv-section-title">{icon} {title}</div>', unsafe_allow_html=True)


def quota_used() -> int:
    """Number of live-provider analyses already run in this session."""
    try:
        return int(st.session_state.get("fv_runs_used", 0))
    except (TypeError, ValueError):
        return 0


def quota_limit(config) -> int:
    """Maximum live-provider analyses allowed per session (0 disables the cap)."""
    try:
        return max(0, int(getattr(config, "max_runs_per_session", 0) or 0))
    except (TypeError, ValueError):
        return 0


def quota_remaining(config) -> int:
    """Remaining analyses in this session; 0 means the limit is reached."""
    limit = quota_limit(config)
    if limit <= 0:
        return -1
    return max(0, limit - quota_used())


def quota_exhausted(config) -> bool:
    """True when this session has used up its analysis allowance."""
    limit = quota_limit(config)
    return limit > 0 and quota_used() >= limit


def consume_quota(config) -> bool:
    """Reserve one live-provider analysis. Returns False when the cap is reached."""
    if quota_exhausted(config):
        return False
    st.session_state["fv_runs_used"] = quota_used() + 1
    return True


def quota_notice(config) -> None:
    """Render the friendly 'limit reached' message."""
    st.markdown(
        '<div class="fv-alert warn"><strong>Session analysis limit reached.</strong> '
        f'{quota_used()}/{quota_limit(config)} analyses used in this session. '
        'Reload the page to start a new session.</div>',
        unsafe_allow_html=True,
    )


def quota_chip(config) -> None:
    """Small quota indicator for the sidebar model card."""
    limit = quota_limit(config)
    if limit <= 0:
        return
    remaining = quota_remaining(config)
    tone = "success" if remaining > 0 else "danger"
    st.markdown(
        f'<div class="fv-quota"><span class="fv-chip {tone}">Quota {quota_used()}/{limit}</span>'
        f'<span class="fv-quota-note">{remaining} left</span></div>',
        unsafe_allow_html=True,
    )


def reserve_analysis(config, ai_client) -> bool:
    """Reserve one analysis credit before a live-provider call.

    Demo mode never consumes quota. Returns False (and renders the limit
    notice) when the session allowance has been used up.
    """
    if config.demo_mode or not ai_client.is_available():
        return True
    if not consume_quota(config):
        quota_notice(config)
        return False
    return True


def metric_strip(items: Sequence[Tuple[str, str, str, str]]) -> None:
    """Render a responsive strip of metric cards: (label, value, unit, color)."""
    cols = st.columns(len(items))
    for col, (label, value, unit, color) in zip(cols, items):
        with col:
            st.markdown(
                f'<div class="fv-metric">'
                f'<span class="val" style="color:{color}">{value}</span>'
                f'<span class="lab">{label} <small style="opacity:0.7">{unit}</small></span>'
                f'</div>',
                unsafe_allow_html=True,
            )


def bar_chart(rows: Sequence[Tuple[str, float, str]], max_value: Optional[float] = None) -> None:
    """Horizontal HTML bars: (label, value, color)."""
    if not rows:
        return
    peak = max_value or max((v for _, v, _ in rows), default=1) or 1
    parts = []
    for label, value, color in rows:
        pct = max(0.0, min(100.0, (float(value) / peak) * 100.0))
        parts.append(
            f'<div class="fv-bar-row">'
            f'<span class="fv-bar-label">{label}</span>'
            f'<span class="fv-bar-track"><span class="fv-bar-fill" style="width:{pct:.1f}%;background:{color}"></span></span>'
            f'<span class="fv-bar-value">{value:g}</span>'
            f'</div>'
        )
    st.markdown(f'<div class="fv-bars">{"".join(parts)}</div>', unsafe_allow_html=True)


def data_table(headers: Sequence[str], rows: Sequence[Sequence[str]], empty: str = "No rows.") -> None:
    """Render a lightweight HTML table with escaping-friendly values."""
    if not rows:
        st.caption(empty)
        return
    head = "".join(f"<th>{h}</th>" for h in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>" for row in rows
    )
    st.markdown(
        f'<div class="fv-table-wrap"><table class="fv-table"><thead><tr>{head}</tr></thead>'
        f'<tbody>{body}</tbody></table></div>',
        unsafe_allow_html=True,
    )


def copy_button(text: str, label: str = "Copy", key: str = "copy") -> None:
    """Small button that copies plain text to the clipboard."""
    payload = json.dumps(text).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")
    st.iframe(
        f"""
        <button id="{key}_btn" style="
          font-family:inherit;font-size:0.8rem;font-weight:600;cursor:pointer;
          border:1px solid #cbd5e1;background:#ffffff;color:#334155;
          border-radius:8px;padding:0.4rem 0.8rem;">{label}</button>
        <span id="{key}_msg" role="status" aria-live="polite" style="font-size:0.75rem;color:#059669;margin-left:0.5rem;"></span>
        <script>
          const btn = document.getElementById("{key}_btn");
          const msg = document.getElementById("{key}_msg");
          btn.addEventListener("click", async () => {{
            const text = {payload};
            try {{
              await navigator.clipboard.writeText(text);
            }} catch (e) {{
              const ta = document.createElement("textarea");
              ta.value = text; document.body.appendChild(ta); ta.select();
              document.execCommand("copy"); ta.remove();
            }}
            msg.textContent = "Copied";
            setTimeout(() => {{ msg.textContent = ""; }}, 1600);
          }});
        </script>
        """,
        height=42,
        width="content",
        alt=f"{label} button",
    )


def download_button(data: str, filename: str, mime: str = "text/plain", label: str = "Download") -> None:
    st.download_button(label, data=data, file_name=filename, mime=mime)


def chip_input(
    options: Sequence[str],
    key: str,
    label: str = "Items",
    placeholder: str = "Add your own…",
    max_tags: int = 12,
) -> List[str]:
    """Chip-based multi-select input backed by a free-text field."""
    selected: List[str] = []
    try:
        picked = st.multiselect(
            label,
            options,
            default=[],
            key=f"{key}_chips",
            placeholder="Pick from the list",
        )
        selected.extend(picked)
    except Exception:
        selected = []
    custom = st.text_input(
        "Add items",
        placeholder=placeholder,
        key=f"{key}_custom",
        help="Type comma-separated items and press Enter.",
    )
    if custom:
        for part in custom.split(","):
            cleaned = part.strip()
            if cleaned and cleaned not in selected:
                selected.append(cleaned)
    if len(selected) > max_tags:
        selected = selected[:max_tags]
    return selected


def empty_state(icon: str, title: str, body: str) -> None:
    """Friendly placeholder for workflows waiting on input."""
    st.markdown(
        f'<div class="fv-empty">'
        f'<div class="fv-empty-icon">{icon}</div>'
        f'<div class="fv-empty-title">{title}</div>'
        f'<div class="fv-empty-body">{body}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def hero(provider_label: str, mode_label: str, model_label: str = "") -> None:
    """Landing hero panel."""
    chips = [
        f'<span class="fv-hero-chip">{mode_label}</span>',
        f'<span class="fv-hero-chip">{provider_label}</span>',
    ]
    if model_label:
        chips.append(f'<span class="fv-hero-chip">{model_label}</span>')
    chips.append('<span class="fv-hero-chip">5 specialist workflows</span>')
    chips.append('<span class="fv-hero-chip">Image & text reasoning</span>')
    st.markdown(
        '<div class="fv-hero">'
        '<span class="fv-hero-eyebrow">Multimodal Food Intelligence Agent</span>'
        '<div class="fv-hero-title">Food Verse AI</div>'
        '<div class="fv-hero-sub">Recognize a dish, judge freshness, audit kitchen hygiene, '
        'craft recipes and build a meal plan — all from the images and inputs you already have.</div>'
        f'<div class="fv-hero-chips">{"".join(chips)}</div>'
        '</div>',
        unsafe_allow_html=True,
    )


def capability_cards(on_select: Callable[[str], None]) -> None:
    """Grid of workflow cards on the landing view."""
    keys = list(TAB_META.keys())
    with st.container(key="fv_home_cards"):
        row = st.columns(3)
        for col, key in zip(row, keys[:3]):
            _capability_card(col, key, on_select)
        row = st.columns([0.5, 1, 1, 0.5])
        for col, key in zip([row[1], row[2]], keys[3:]):
            _capability_card(col, key, on_select)


def _capability_card(col, key: str, on_select: Callable[[str], None]) -> None:
    meta = TAB_META[key]
    with col:
        st.markdown(
            f'<div class="fv-card-eyebrow"><span>{meta["icon"]}</span>{meta["title"]}</div>'
            f'<div class="fv-card-body">{meta["blurb"]}</div>',
            unsafe_allow_html=True,
        )
        st.caption(f'Assistant: {meta["persona"]}')
        st.button(
            "Open workflow",
            key=f"home_open_{key}",
            on_click=on_select,
            args=(key,),
            width="stretch",
        )


def how_it_works() -> None:
    """Three-step explainer on the landing view."""
    steps = [
        ("1", "Upload or describe", "Drop a photo of food or a kitchen, or type your pantry and profile."),
        ("2", "Run the specialist", "Each workflow is handled by a dedicated assistant persona with focused prompts."),
        ("3", "Act on the result", "Scores, safety verdicts, recipes and plans come with clear next steps."),
    ]
    with st.container(key="fv_home_steps"):
        cols = st.columns(3)
        for col, (num, title, body) in zip(cols, steps):
            with col:
                st.markdown(
                    f'<div class="step-num">{num}</div>'
                    f'<div class="fv-card-title">{title}</div>'
                    f'<div class="fv-card-body">{body}</div>',
                    unsafe_allow_html=True,
                )
