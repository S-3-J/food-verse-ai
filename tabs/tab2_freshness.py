"""Tab 2 - Food Freshness & Spoilage Diagnostic (Epic 3)."""
from __future__ import annotations

from typing import Any, Dict
from datetime import datetime

import streamlit as st

from ai_client import AIClient
from config import AppConfig, FRESHNESS_STAGES
from personas import build_system_prompt, get_persona
from ui import copy_button, data_table, download_button, empty_state, metric_strip, reserve_analysis
from utils import (
    dominant_color_analysis,
    esc,
    freshness_to_pill,
    image_bytes,
    load_image,
    parse_json_safe,
    safety_to_pill,
    upload_fingerprint,
)


SYSTEM_PROMPT = build_system_prompt(
    get_persona("Safety Inspector Rex"),
    "Food freshness and spoilage diagnostic. Evaluate surface texture, discoloration, wrinkling, mold "
    "and classify freshness stage with safety advice and preservation tips.",
)

VISION_PROMPT = """Analyze this perishable food image and return ONLY a JSON object with these exact keys:
- "item": string (food item name, e.g., "banana", "chicken breast", "milk")
- "freshness_stage": one of ["Fresh", "Moderately Fresh", "Spoiled"]
- "indicators": object with keys "surface_texture", "discoloration", "wrinkling", "mold" (each string observation)
- "confidence": number 0-100
- "safety_advice": one of ["Safe to consume", "Consume within 24h", "Discard immediately"]
- "preservation_tips": array of strings (storage tips)
- "notes": string (brief observation)

Be conservative on safety. When in doubt, recommend discard."""


STORAGE_METHODS = ["Ambient / pantry", "Refrigerated", "Frozen", "Unknown"]
STORAGE_DAYS = {
    "Ambient / pantry": 7,
    "Refrigerated": 10,
    "Frozen": 90,
    "Unknown": 7,
}
STAGE_SCORE = {"Fresh": 95, "Moderately Fresh": 60, "Spoiled": 15}


def _demo_freshness_analysis(image) -> Dict[str, Any]:
    analysis = dominant_color_analysis(image)

    if analysis["brown_dominance"] and analysis["brightness"] < 90:
        stage = "Spoiled"
        advice = "Discard immediately"
        tips = ["Do not consume", "Seal and dispose in outdoor trash", "Clean storage area with sanitizer"]
        indicators = {
            "surface_texture": "Soft / mushy or slimy texture observed",
            "discoloration": "Dark brown / black discoloration present",
            "wrinkling": "Significant wrinkling / shriveling",
            "mold": "Possible fuzzy mold growth",
        }
    elif analysis["green_dominance"] and analysis["brightness"] > 100:
        stage = "Fresh"
        advice = "Safe to consume"
        tips = ["Store in refrigerator crisper drawer", "Keep dry; wash only before use",
                "Use within 5-7 days"]
        indicators = {
            "surface_texture": "Firm, taut surface",
            "discoloration": "Minimal to none",
            "wrinkling": "Little to no wrinkling",
            "mold": "No visible mold",
        }
    else:
        stage = "Moderately Fresh"
        advice = "Consume within 24h"
        tips = ["Consume promptly", "Store airtight in refrigerator", "Cook thoroughly before eating"]
        indicators = {
            "surface_texture": "Slightly soft; acceptable",
            "discoloration": "Minor spotting / dulling",
            "wrinkling": "Light wrinkling",
            "mold": "No visible mold",
        }

    return {
        "item": "Perishable item (visual estimate)",
        "freshness_stage": stage,
        "indicators": indicators,
        "confidence": 58,
        "safety_advice": advice,
        "preservation_tips": tips,
        "notes": "Demo mode: AI provider not configured. Visual heuristic estimate only.",
    }


def _run_vision(ai_client: AIClient, config: AppConfig, image, context: str = "") -> Dict[str, Any]:
    img_bytes = image_bytes(image)
    if config.demo_mode or not ai_client.is_available():
        return _demo_freshness_analysis(image)
    try:
        prompt = VISION_PROMPT
        if context:
            prompt = f"{VISION_PROMPT}\n\nStorage context: {context}"
        text = ai_client.generate_vision(SYSTEM_PROMPT, prompt, img_bytes)
        return parse_json_safe(text, fallback=_demo_freshness_analysis(image))
    except Exception as exc:  # pragma: no cover
        st.warning(f"AI vision unavailable, using demo fallback: {exc}")
        return _demo_freshness_analysis(image)


def render(config: AppConfig, ai_client: AIClient) -> None:
    ctx1, ctx2, ctx3 = st.columns([1, 1, 1])
    with ctx1:
        purchased_on = st.date_input(
            "Purchased on",
            value=None,
            key="tab2_purchased",
            help="Optional — improves the storage-age estimate.",
        )
    with ctx2:
        storage = st.selectbox("Storage method", STORAGE_METHODS, key="tab2_storage")
    with ctx3:
        st.markdown("", unsafe_allow_html=True)

    col_up, col_ctrl = st.columns([3, 1])
    with col_up:
        uploaded = st.file_uploader("Upload a perishable item photo (fruit, vegetable, meat, dairy)",
                                    type=["jpg", "jpeg", "png", "webp"])
    with col_ctrl:
        run_btn = st.button("Inspect Freshness", key="tab2_run", type="primary", width="stretch")

    if not uploaded:
        empty_state(
            "🧪",
            "No perishable photo yet",
            "Upload a photo of a raw perishable item — fruit, vegetable, meat or dairy — to stage "
            "its freshness and get a safety verdict. Demo mode runs without an API key.",
        )
        return

    image = load_image(uploaded)
    if image is None:
        st.error("Failed to load image.")
        return

    age_days = None
    if purchased_on is not None:
        age_days = max(0, (datetime.now().date() - purchased_on).days)
    context = f"{storage}, purchased {age_days} days ago" if age_days is not None else storage

    fingerprint = upload_fingerprint(uploaded) + f"|{context}"
    stored_fp = st.session_state.get("tab2_fp")
    if run_btn or "tab2_result" not in st.session_state or stored_fp != fingerprint:
        if not reserve_analysis(config, ai_client):
            return
        with st.spinner("Inspecting freshness indicators..."):
            result = _run_vision(ai_client, config, image, context)
        st.session_state["tab2_result"] = result
        st.session_state["tab2_fp"] = fingerprint
    else:
        result = st.session_state["tab2_result"]

    stage = result.get("freshness_stage", "Moderately Fresh")
    advice = result.get("safety_advice", "Consume within 24h")
    freshness_score = STAGE_SCORE.get(stage, 60)

    # ---- Image Left / Content Right ----
    img_col, info_col = st.columns([1, 1])
    with img_col:
        st.image(image, caption="Uploaded perishable item", width="stretch")
    with info_col:
        st.markdown(f"### {esc(result.get('item', 'Unknown'))}")
        pill_class = freshness_to_pill(stage)
        st.markdown(f'<span class="fv-pill {pill_class}">{esc(stage)}</span>', unsafe_allow_html=True)

        score_color = "#10b981" if freshness_score >= 80 else ("#f59e0b" if freshness_score >= 45 else "#ef4444")
        st.markdown(
            f'<div class="fv-card" style="margin-top:0.7rem;">'
            f'<div style="display:flex;align-items:baseline;gap:0.6rem;">'
            f'<span style="font-size:2rem;font-weight:900;color:{score_color}">{freshness_score}</span>'
            f'<span style="font-size:0.8rem;color:var(--fv-text-muted);font-weight:600;">Freshness index / 100</span>'
            f'</div>'
            f'<span class="fv-meter" style="display:block;margin-top:0.5rem;">'
            f'<span class="fv-meter-fill" style="width:{freshness_score}%;background:{score_color}"></span></span>'
            f'</div>', unsafe_allow_html=True,
        )

        metric_strip([
            ("Confidence", f'{result.get("confidence", 0)}%', "", "#0ea5e9"),
            ("Stored for", f"{age_days}" if age_days is not None else "—", "days", "#8b5cf6"),
            ("Shelf life", f"{STORAGE_DAYS.get(storage, 7)}", "days", "#f59e0b"),
        ])

    # Safety advice banner
    advice_class = safety_to_pill(advice)
    alert_type = "success" if advice_class == "safe" else ("danger" if advice_class == "discard" else "warn")
    st.markdown(
        f'<div class="fv-alert {alert_type}">'
        f'<strong>Food Safety Verdict:</strong> {esc(advice)}</div>', unsafe_allow_html=True,
    )

    st.divider()

    # ---- Visual Indicators below ----
    st.markdown('<div class="fv-section-title">🔍 Visual Indicators</div>', unsafe_allow_html=True)
    indicators = result.get("indicators", {})
    indicator_items = [
        ("Surface Texture", indicators.get("surface_texture", "—")),
        ("Discoloration", indicators.get("discoloration", "—")),
        ("Wrinkling", indicators.get("wrinkling", "—")),
        ("Mold", indicators.get("mold", "—")),
    ]
    data_table(["Indicator", "Observation"], [[k, esc(v)] for k, v in indicator_items])

    # Preservation tips
    st.divider()
    st.markdown('<div class="fv-section-title">📦 Preservation & Storage Tips</div>', unsafe_allow_html=True)
    tips = result.get("preservation_tips", [])
    if tips:
        st.markdown(
            '<ul style="color:var(--fv-text-soft);line-height:1.7;margin-top:0.2rem;">'
            + "".join(f"<li>{esc(t)}</li>" for t in tips)
            + "</ul>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("No specific tips available.")

    if result.get("notes"):
        st.caption(f"🔎 {esc(result['notes'])}")

    export_text = "\n".join([
        f"Item: {result.get('item', '')}",
        f"Freshness stage: {stage}",
        f"Freshness index: {freshness_score}/100",
        f"Safety advice: {advice}",
        f"Storage: {storage}" + (f" ({age_days} days since purchase)" if age_days is not None else ""),
        f"Confidence: {result.get('confidence', 0)}%",
        "Indicators:",
        *[f"- {k}: {v}" for k, v in indicator_items],
        "Tips:",
        *[f"- {t}" for t in tips],
    ])
    d_col, c_col = st.columns([1, 1])
    with d_col:
        download_button(export_text, "foodverse-freshness.txt", label="Download report")
    with c_col:
        copy_button(export_text, "Copy summary", key="tab2_copy")

    st.caption("Freshness staging is heuristic. When safety is uncertain, discard the item.")
