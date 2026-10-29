"""Tab 3 - Kitchen Hygiene & Food Safety Compliance (Epic 4)."""
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from ai_client import AIClient
from config import AppConfig, HYGIENE_INDICATORS
from personas import build_system_prompt, get_persona
from ui import copy_button, data_table, download_button, empty_state, metric_strip, reserve_analysis
from utils import (
    esc,
    image_bytes,
    load_image,
    parse_json_safe,
    upload_fingerprint,
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


def _status_for(score: float) -> str:
    if score >= 85:
        return "Compliant"
    if score >= 65:
        return "Needs Attention"
    return "Non-Compliant"


def _severity_rank(severity: str) -> int:
    return {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}.get(severity, 4)


def render(config: AppConfig, ai_client: AIClient) -> None:
    col_up, col_ctrl = st.columns([3, 1])
    with col_up:
        uploaded = st.file_uploader(
            "Upload a kitchen photo",
            type=["jpg", "jpeg", "png", "webp"],
            help="Video frame extraction is not enabled yet — upload a still frame of the kitchen.",
        )
    with col_ctrl:
        run_btn = st.button("Inspect Kitchen", key="tab3_run", type="primary", width="stretch")

    if not uploaded:
        empty_state(
            "🧼",
            "No kitchen photo yet",
            "Upload a photo of the prep area to score hygiene compliance and log violations. "
            "Demo mode runs without an API key.",
        )
        return

    image = load_image(uploaded)
    if image is None:
        st.error("Failed to load image.")
        return

    fingerprint = upload_fingerprint(uploaded)
    stored_fp = st.session_state.get("tab3_fp")
    if run_btn or "tab3_result" not in st.session_state or stored_fp != fingerprint:
        if not reserve_analysis(config, ai_client):
            return
        with st.spinner("Inspecting hygiene indicators..."):
            result = _run_vision(ai_client, config, image)
        st.session_state["tab3_result"] = result
        st.session_state["tab3_fp"] = fingerprint
    else:
        result = st.session_state["tab3_result"]

    score = float(result.get("compliance_score", 0))
    color = _score_badge_color(score)
    status = _status_for(score)

    # ---- Image Left / Content Right ----
    img_col, info_col = st.columns([1, 1])
    with img_col:
        st.image(image, caption="Uploaded kitchen view", width="stretch")
    with info_col:
        st.markdown("### Compliance Score")
        st.markdown(
            f'<div style="font-size:2.4rem;font-weight:900;color:{color};line-height:1.1">{score:.0f}%</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<span class="fv-pill {"fresh" if score >= 85 else ("moderate" if score >= 65 else "spoiled")}">'
            f'{esc(status)}</span>', unsafe_allow_html=True,
        )
        st.markdown(
            f'<span class="fv-meter" style="display:block;margin:0.7rem 0;">'
            f'<span class="fv-meter-fill" style="width:{max(0.0, min(100.0, score))}%;background:{color}"></span>'
            f'</span>', unsafe_allow_html=True,
        )
        st.caption("Thresholds — compliant ≥ 85 · needs attention ≥ 65 · otherwise non-compliant.")

    st.divider()

    # ---- Hygiene Indicators below ----
    st.markdown('<div class="fv-section-title">📋 Hygiene Indicators</div>', unsafe_allow_html=True)
    indicators = result.get("indicators", {})
    mapping = {
        "Chef Hat / Hairnet Compliance": "chef_hat_hairnet",
        "Glove Usage": "glove_usage",
        "Sanitization State": "sanitization_state",
        "Cross-Contamination Hazards": "cross_contamination",
    }
    indicator_rows = []
    for key in HYGIENE_INDICATORS:
        internal = mapping.get(key, key.lower().replace(" ", "_"))
        val = indicators.get(internal, "Not observed")
        indicator_rows.append([key, esc(val)])

    sev_col, conf_col = st.columns(2)
    with sev_col:
        violations = result.get("violations", [])
        high = sum(1 for v in violations if v.get("severity") in ("Critical", "High"))
        metric_strip([
            ("Violations", f"{len(violations)}", "", "#f59e0b"),
            ("Critical / High", f"{high}", "", "#ef4444"),
        ])
    with conf_col:
        metric_strip([
            ("Confidence", f'{result.get("confidence", 0)}%', "", "#0ea5e9"),
            ("Indicators", f"{len(indicator_rows)}", "checked", "#10b981"),
        ])

    st.markdown("")
    data_table(["Indicator", "Observation"], indicator_rows)

    # Violations log
    st.divider()
    st.markdown('<div class="fv-section-title">🚨 Itemized Violation Log</div>', unsafe_allow_html=True)
    violations = sorted(
        result.get("violations", []),
        key=lambda v: _severity_rank(v.get("severity", "Low")),
    )
    if violations:
        data_table(
            ["Severity", "Indicator", "Description"],
            [
                [esc(v.get("severity", "Low")), esc(v.get("indicator", "General")), esc(v.get("description", ""))]
                for v in violations
            ],
        )
    else:
        st.markdown(
            '<div class="fv-alert success">No violations logged.</div>',
            unsafe_allow_html=True,
        )

    # Recommendations
    st.divider()
    st.markdown('<div class="fv-section-title">✅ Corrective Recommendations</div>', unsafe_allow_html=True)
    recommendations = result.get("recommendations", [])
    if recommendations:
        st.markdown(
            '<ul style="color:var(--fv-text-soft);line-height:1.7;margin-top:0.2rem;">'
            + "".join(f"<li>{esc(r)}</li>" for r in recommendations)
            + "</ul>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("No recommendations returned.")

    if result.get("notes"):
        st.caption(f"🔎 {esc(result['notes'])}")

    export_lines = [
        f"Kitchen hygiene compliance score: {score:.0f}% ({status})",
        f"Confidence: {result.get('confidence', 0)}%",
        "",
        "Indicators:",
        *[f"- {k}: {v}" for k, v in indicator_rows],
        "",
        "Violations:",
        *[
            f"- [{v.get('severity', 'Low')}] {v.get('indicator', 'General')}: {v.get('description', '')}"
            for v in violations
        ],
        "",
        "Recommendations:",
        *[f"- {r}" for r in recommendations],
    ]
    export_text = "\n".join(export_lines)
    d_col, c_col = st.columns([1, 1])
    with d_col:
        download_button(export_text, "foodverse-hygiene-report.txt", label="Download report")
    with c_col:
        copy_button(export_text, "Copy summary", key="tab3_copy")

    st.caption("Compliance scoring is heuristic. Critical hazards require immediate correction.")
