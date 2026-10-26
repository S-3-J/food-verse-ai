"""Tab 2 - Food Freshness & Spoilage Diagnostic (Epic 3)."""
from __future__ import annotations

from typing import Any, Dict

import streamlit as st

from ai_client import AIClient
from config import AppConfig, FRESHNESS_STAGES
from personas import build_system_prompt, get_persona
from utils import (
    dominant_color_analysis,
    freshness_to_pill,
    image_bytes,
    load_image,
    parse_json_safe,
    safety_to_pill,
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


def _demo_freshness_analysis(image) -> Dict[str, Any]:
    from utils import estimate_portion_from_image  # noqa

    analysis = dominant_color_analysis(image)
    # Heuristic: brown dominance + low brightness => spoiled-ish; green => fresh
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


def _run_vision(ai_client: AIClient, config: AppConfig, image) -> Dict[str, Any]:
    img_bytes = image_bytes(image)
    if config.demo_mode or not ai_client.is_available():
        return _demo_freshness_analysis(image)
    try:
        text = ai_client.generate_vision(SYSTEM_PROMPT, VISION_PROMPT, img_bytes)
        return parse_json_safe(text, fallback=_demo_freshness_analysis(image))
    except Exception as exc:  # pragma: no cover
        st.warning(f"AI vision unavailable, using demo fallback: {exc}")
        return _demo_freshness_analysis(image)


def render(config: AppConfig, ai_client: AIClient) -> None:
    st.header("🧪 Food Freshness & Spoilage Diagnostic")
    st.caption("Epic 3 — Perishable freshness staging with food-safety advice and preservation tips.")

    col_up, col_ctrl = st.columns([3, 1])
    with col_up:
        uploaded = st.file_uploader("Upload a perishable item photo (fruit, vegetable, meat, dairy)",
                                    type=["jpg", "jpeg", "png", "webp"])
    with col_ctrl:
        run_btn = st.button("Inspect Freshness", key="tab2_run")

    if not uploaded:
        st.info("Upload a photo of a raw perishable item. Demo mode runs without an API key.")
        return

    image = load_image(uploaded)
    if image is None:
        st.error("Failed to load image.")
        return

    st.image(image, caption="Uploaded perishable item", use_container_width=True)

    if run_btn or "tab2_result" not in st.session_state:
        with st.spinner("Inspecting freshness indicators..."):
            result = _run_vision(ai_client, config, image)
        st.session_state["tab2_result"] = result

    result = st.session_state.get("tab2_result", {})

    stage = result.get("freshness_stage", "Moderately Fresh")
    advice = result.get("safety_advice", "Consume within 24h")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Item", result.get("item", "Unknown"))
    with c2:
        pill_class = freshness_to_pill(stage)
        st.markdown(f'<span class="fv-pill {pill_class}">{stage}</span>', unsafe_allow_html=True)
    with c3:
        st.metric("Confidence", f"{result.get('confidence', 0)}%")

    st.divider()

    # Safety advice banner
    advice_class = safety_to_pill(advice)
    alert_type = "success" if advice_class == "safe" else ("danger" if advice_class == "discard" else "warn")
    st.markdown(
        f'<div class="fv-alert {alert_type}">'
        f'<strong>Food Safety Verdict:</strong> {advice}</div>', unsafe_allow_html=True,
    )

    # Indicators
    st.subheader("🔍 Visual Indicators")
    indicators = result.get("indicators", {})
    ind_cols = st.columns(2)
    indicator_items = [
        ("Surface Texture", indicators.get("surface_texture", "—")),
        ("Discoloration", indicators.get("discoloration", "—")),
        ("Wrinkling", indicators.get("wrinkling", "—")),
        ("Mold", indicators.get("mold", "—")),
    ]
    for i, (k, v) in enumerate(indicator_items):
        with ind_cols[i % 2]:
            st.markdown(
                f'<div class="fv-card" style="padding:0.8rem 1rem;">'
                f'<div style="font-weight:700;color:#22d3ee">{k}</div>'
                f'<div style="color:#cbd5e1;font-size:0.95rem">{v}</div>'
                f'</div>', unsafe_allow_html=True,
            )

    # Preservation tips
    st.divider()
    st.subheader("📦 Preservation & Storage Tips")
    tips = result.get("preservation_tips", [])
    if tips:
        for tip in tips:
            st.markdown(f"• {tip}")
    else:
        st.caption("No specific tips available.")

    if result.get("notes"):
        st.caption(f"🔎 {result['notes']}")

    st.divider()
    st.caption("Demo mode: freshness staging is heuristic. When safety is uncertain, discard the item.")
