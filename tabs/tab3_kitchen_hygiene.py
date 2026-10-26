"""Tab 3 - Kitchen Hygiene & Food Safety Compliance (Epic 4)."""
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from ai_client import AIClient
from config import AppConfig, HYGIENE_INDICATORS
from personas import build_system_prompt, get_persona
from utils import (
    image_bytes,
    load_image,
    parse_json_safe,
)


SYSTEM_PROMPT = build_system_prompt(
    get_persona("Safety Inspector Rex"),
    "Commercial kitchen hygiene compliance inspection. Detect chef hat/hairnet compliance, glove usage, "
    "sanitization state, and cross-contamination hazards. Compute compliance score and itemized violations.",
)

VISION_PROMPT = """Inspect this kitchen image/video frame and return ONLY a JSON object with these exact keys:
- "compliance_score": number 0-100 (overall kitchen hygiene compliance %)
- "indicators": object with keys:
    "chef_hat_hairnet": "Compliant" | "Non-compliant" | "Not observed",
    "glove_usage": "Compliant" | "Non-compliant" | "Not observed",
    "sanitization_state": "Sanitized" | "Needs attention" | "Unsanitary",
    "cross_contamination": "None detected" | "Potential hazard" | "Critical hazard"
- "violations": array of objects, each with "indicator", "severity" (Low/Medium/High/Critical), "description"
- "recommendations": array of strings (corrective actions)
- "confidence": number 0-100
- "notes": string

Be strict on food safety. Flag raw poultry near produce as a critical cross-contamination hazard."""


def _demo_hygiene_analysis(image) -> Dict[str, Any]:
    from utils import dominant_color_analysis
    analysis = dominant_color_analysis(image)

    # Heuristic scoring based on brightness/colors (very naive)
    score = 78
    violations: List[Dict[str, str]] = []
    indicators = {
        "chef_hat_hairnet": "Not observed",
        "glove_usage": "Compliant",
        "sanitization_state": "Sanitized",
        "cross_contamination": "None detected",
    }

    if analysis["brightness"] < 80:
        indicators["sanitization_state"] = "Needs attention"
        score -= 12
        violations.append({
            "indicator": "Sanitization State",
            "severity": "Medium",
            "description": "Dim lighting / surfaces appear unsanitized in work zones.",
        })
    if analysis["red_dominance"]:
        indicators["cross_contamination"] = "Potential hazard"
        score -= 15
        violations.append({
            "indicator": "Cross-Contamination",
            "severity": "High",
            "description": "Raw meat/poultry color tones observed near prep areas; separate from produce.",
        })

    score = max(0, min(100, score))
    if not violations:
        violations.append({
            "indicator": "General",
            "severity": "Low",
            "description": "No critical violations detected in this frame.",
        })

    return {
        "compliance_score": score,
        "indicators": indicators,
        "violations": violations,
        "recommendations": [
            "Enforce hairnet/chef hat use at all prep stations",
            "Require single-use gloves for ready-to-eat food handling",
            "Sanitize surfaces between raw and ready-to-eat tasks",
            "Store raw poultry on lowest shelf, sealed, away from produce",
        ],
        "confidence": 60,
        "notes": "Demo mode: AI provider not configured. Visual heuristic estimate only.",
    }


def _run_vision(ai_client: AIClient, config: AppConfig, image) -> Dict[str, Any]:
    img_bytes = image_bytes(image)
    if config.demo_mode or not ai_client.is_available():
        return _demo_hygiene_analysis(image)
    try:
        text = ai_client.generate_vision(SYSTEM_PROMPT, VISION_PROMPT, img_bytes)
        return parse_json_safe(text, fallback=_demo_hygiene_analysis(image))
    except Exception as exc:  # pragma: no cover
        st.warning(f"AI vision unavailable, using demo fallback: {exc}")
        return _demo_hygiene_analysis(image)


def _score_badge_color(score: float) -> str:
    if score >= 85:
        return "#10b981"
    if score >= 65:
        return "#f59e0b"
    return "#ef4444"


def render(config: AppConfig, ai_client: AIClient) -> None:
    st.header("🧼 Kitchen Hygiene & Safety Compliance")
    st.caption("Epic 4 — Commercial kitchen hygiene inspection with compliance scoring and violation logs.")

    col_up, col_ctrl = st.columns([3, 1])
    with col_up:
        uploaded = st.file_uploader(
            "Upload kitchen photo or video frame",
            type=["jpg", "jpeg", "png", "webp", "mp4", "mov", "avi"],
        )
    with col_ctrl:
        run_btn = st.button("Inspect Kitchen", key="tab3_run")

    if not uploaded:
        st.info("Upload a kitchen environment image or video frame. Demo mode runs without an API key.")
        return

    image = load_image(uploaded)
    if image is None:
        st.error("Failed to load image/video frame.")
        return

    st.image(image, caption="Uploaded kitchen view", use_container_width=True)

    if run_btn or "tab3_result" not in st.session_state:
        with st.spinner("Inspecting hygiene indicators..."):
            result = _run_vision(ai_client, config, image)
        st.session_state["tab3_result"] = result

    result = st.session_state.get("tab3_result", {})
    score = float(result.get("compliance_score", 0))
    color = _score_badge_color(score)

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f'<div class="fv-metric">'
            f'<span class="val" style="color:{color}">{score:.0f}</span>'
            f'<span class="lab">Compliance Score (%)</span></div>', unsafe_allow_html=True,
        )
    with c2:
        st.metric("Confidence", f"{result.get('confidence', 0)}%")
    with c3:
        status = "Compliant" if score >= 85 else ("Needs Attention" if score >= 65 else "Non-Compliant")
        st.metric("Status", status)

    st.divider()

    # Indicators
    st.subheader("📋 Hygiene Indicators")
    indicators = result.get("indicators", {})
    ind_cols = st.columns(2)
    for i, key in enumerate(HYGIENE_INDICATORS):
        val = indicators.get(key.lower().replace(" / ", "_").replace(" ", "_"), "Not observed")
        # map friendly key to internal
        mapping = {
            "Chef Hat / Hairnet Compliance": "chef_hat_hairnet",
            "Glove Usage": "glove_usage",
            "Sanitization State": "sanitization_state",
            "Cross-Contamination Hazards": "cross_contamination",
        }
        internal = mapping.get(key, key.lower().replace(" ", "_"))
        val = indicators.get(internal, "Not observed")
        with ind_cols[i % 2]:
            badge = "fresh" if val in ("Compliant", "Sanitized", "None detected") else ("moderate" if val in ("Needs attention", "Potential hazard") else "spoiled")
            st.markdown(
                f'<div class="fv-card" style="padding:0.8rem 1rem;">'
                f'<div style="font-weight:700;color:#22d3ee">{key}</div>'
                f'<span class="fv-pill {badge}">{val}</span>'
                f'</div>', unsafe_allow_html=True,
            )

    # Violations log
    st.divider()
    st.subheader("🚨 Itemized Violation Log")
    violations = result.get("violations", [])
    if violations:
        for v in violations:
            sev = v.get("severity", "Low")
            sev_color = {"Critical": "#ef4444", "High": "#f97316", "Medium": "#f59e0b", "Low": "#10b981"}.get(sev, "#94a3b8")
            st.markdown(
                f'<div class="violation">'
                f'<span class="v-title">[{sev}]</span> {v.get("indicator", "General")} — '
                f'{v.get("description", "")}</div>', unsafe_allow_html=True,
            )
    else:
        st.success("No violations logged.")

    # Recommendations
    st.divider()
    st.subheader("✅ Corrective Recommendations")
    for rec in result.get("recommendations", []):
        st.markdown(f"• {rec}")

    if result.get("notes"):
        st.caption(f"🔎 {result['notes']}")

    st.divider()
    st.caption("Demo mode: compliance scoring is heuristic. Critical hazards require immediate correction.")
