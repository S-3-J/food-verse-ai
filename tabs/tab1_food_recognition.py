"""Tab 1 - Food Recognition & Nutrition Audit (Epic 2)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import plotly.graph_objects as go

from ai_client import AIClient
from config import AppConfig
from personas import build_system_prompt, get_persona
from ui import (
    bar_chart,
    copy_button,
    data_table,
    download_button,
    empty_state,
    metric_strip,
    reserve_analysis,
)
from utils import (
    detect_allergens,
    estimate_portion_from_image,
    format_macros,
    fallback_nutrition,
    compute_health_score,
    esc,
    image_bytes,
    load_image,
    parse_json_safe,
    score_to_badge,
    upload_fingerprint,
)


SYSTEM_PROMPT = build_system_prompt(
    get_persona("Nutritionist Nova"),
    "Food image recognition and nutrition audit. Identify the dish, cuisine, ingredients, portion, "
    "macros, allergens, and compute a health score.",
)

VISION_PROMPT = """Analyze this food image and return ONLY a JSON object with these exact keys:
- "dish_name": string (best guess dish name)
- "cuisine": string (cuisine type)
- "ingredients": array of strings (visible/likely ingredients)
- "portion_size": string (e.g., "Small (~1 serving)", "Medium (~1-2 servings)", "Large (~2+ servings)")
- "calories": number (estimated kcal)
- "protein": number (grams)
- "carbs": number (grams)
- "fat": number (grams)
- "fiber": number (grams)
- "health_score": number 0-100 (composite nutrition health score)
- "confidence": number 0-100 (visual recognition confidence)
- "notes": string (brief observation)

Be accurate and conservative. Label estimates clearly. If you cannot estimate a value precisely, provide a reasonable estimate and note it."""


def _demo_vision_analysis(image) -> Dict[str, Any]:
    """Heuristic fallback vision analysis when no AI provider is configured."""
    from utils import dominant_color_analysis

    analysis = dominant_color_analysis(image)
    portion = estimate_portion_from_image(image)

    guess = "Mixed dish / Bowl"
    if analysis["green_dominance"]:
        guess = "Vegetable salad / Green bowl"
    elif analysis["red_dominance"]:
        guess = "Tomato-based dish / Pasta or curry"
    elif analysis["brown_dominance"]:
        guess = "Grilled / roasted protein dish"
    else:
        guess = "Plated meal"

    macros = fallback_nutrition(guess)
    return {
        "dish_name": guess,
        "cuisine": "International",
        "ingredients": ["Mixed ingredients (visual estimate)"],
        "portion_size": portion,
        "calories": macros.get("calories", 350),
        "protein": macros.get("protein", 15),
        "carbs": macros.get("carbs", 45),
        "fat": macros.get("fat", 12),
        "fiber": macros.get("fiber", 4),
        "health_score": compute_health_score(macros, guess),
        "confidence": 55,
        "notes": "Demo mode: AI provider not configured. Visual heuristic estimate only.",
    }


def _run_vision(ai_client: AIClient, config: AppConfig, image) -> Dict[str, Any]:
    img_bytes = image_bytes(image)
    if config.demo_mode or not ai_client.is_available():
        return _demo_vision_analysis(image)
    try:
        text = ai_client.generate_vision(SYSTEM_PROMPT, VISION_PROMPT, img_bytes)
        result = parse_json_safe(text, fallback={})
        if not result:
            return _demo_vision_analysis(image)
        demo = _demo_vision_analysis(image)
        for key in [
            "dish_name", "cuisine", "ingredients", "portion_size",
            "calories", "protein", "carbs", "fat", "fiber",
            "health_score", "confidence", "notes",
        ]:
            if key not in result or result[key] is None or result[key] == "":
                result[key] = demo.get(key)
        for num_key in ["calories", "protein", "carbs", "fat", "fiber", "health_score", "confidence"]:
            try:
                result[num_key] = float(result.get(num_key, demo.get(num_key, 0)))
            except (TypeError, ValueError):
                result[num_key] = float(demo.get(num_key, 0))
        return result
    except Exception as exc:  # pragma: no cover - defensive UI
        st.warning(f"AI vision unavailable, using demo fallback: {exc}")
        return _demo_vision_analysis(image)


def _calorie_contribution(macros: Dict[str, float]) -> List[Tuple[str, float, str]]:
    """Split estimated calories by macronutrient energy contribution."""
    protein_kcal = macros.get("protein", 0) * 4
    carbs_kcal = macros.get("carbs", 0) * 4
    fat_kcal = macros.get("fat", 0) * 9
    return [
        ("Protein", round(protein_kcal, 1), "#0ea5e9"),
        ("Carbs", round(carbs_kcal, 1), "#10b981"),
        ("Fat", round(fat_kcal, 1), "#f59e0b"),
    ]


def _render_calorie_gauge(calories: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=calories,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Estimated Calories (kcal)", "font": {"color": "#0f172a", "size": 14}},
        number={"font": {"color": "#0ea5e9", "size": 32}},
        gauge={
            "axis": {"range": [0, 1200], "tickcolor": "#64748b"},
            "bar": {"color": "#0ea5e9"},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "#e2e8f0",
            "steps": [
                {"range": [0, 400], "color": "rgba(16,185,129,0.12)"},
                {"range": [400, 800], "color": "rgba(245,158,11,0.12)"},
                {"range": [800, 1200], "color": "rgba(239,68,68,0.12)"},
            ],
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#0f172a"), margin=dict(t=40, b=10, l=10, r=10),
                      height=220)
    return fig


def render(config: AppConfig, ai_client: AIClient) -> None:
    col_up, col_ctrl = st.columns([3, 1])
    with col_up:
        uploaded = st.file_uploader(
            "Upload a meal or dish photo",
            type=["jpg", "jpeg", "png", "webp"],
            help="A clear, well-lit photo of a single dish gives the best estimate.",
        )
    with col_ctrl:
        run_btn = st.button("Analyze Image", key="tab1_run", type="primary", width="stretch")

    if not uploaded:
        empty_state(
            "🍽️",
            "No dish photo yet",
            "Upload a clear, well-lit photo of a single dish to identify it and audit its macros. "
            "Demo mode runs without an API key.",
        )
        return

    image = load_image(uploaded)
    if image is None:
        st.error("Failed to load image.")
        return

    fingerprint = upload_fingerprint(uploaded)
    stored_fp = st.session_state.get("tab1_fp")
    if run_btn or "tab1_result" not in st.session_state or stored_fp != fingerprint:
        if not reserve_analysis(config, ai_client):
            return
        with st.spinner("Analyzing dish with vision model..."):
            vision = _run_vision(ai_client, config, image)
        st.session_state["tab1_result"] = vision
        st.session_state["tab1_fp"] = fingerprint
    else:
        vision = st.session_state["tab1_result"]

    macros = {
        "calories": float(vision.get("calories", 0)),
        "protein": float(vision.get("protein", 0)),
        "carbs": float(vision.get("carbs", 0)),
        "fat": float(vision.get("fat", 0)),
        "fiber": float(vision.get("fiber", 0)),
    }
    health_score = float(vision.get("health_score", compute_health_score(macros, vision.get("dish_name", ""))))
    label, _ = score_to_badge(health_score)

    # ---- Image Left / Content Right ----
    img_col, info_col = st.columns([1, 1])
    with img_col:
        st.image(image, caption="Uploaded dish", width="stretch")
    with info_col:
        st.markdown(f"### {esc(vision.get('dish_name', 'Unknown'))}")
        st.markdown('<div class="fv-card-title">Dish details</div>', unsafe_allow_html=True)
        data_table(
            ["Attribute", "Value"],
            [
                ["Cuisine", esc(vision.get("cuisine", "Unknown"))],
                ["Portion", esc(vision.get("portion_size", "Not estimated"))],
                ["Confidence", f'{vision.get("confidence", 0)}%'],
                ["Ingredients", esc(", ".join(vision.get("ingredients", [])) or "—")],
            ],
        )
        if vision.get("notes"):
            st.caption(f"🔎 {esc(vision['notes'])}")

    st.divider()

    # ---- Macros below as unified section ----
    st.markdown('<div class="fv-section-title">📊 Nutritional Breakdown</div>', unsafe_allow_html=True)

    metric_strip([
        ("Calories", f"{macros.get('calories', 0):.0f}", "kcal", "#0ea5e9"),
        ("Protein", f"{macros.get('protein', 0):.1f}", "g", "#10b981"),
        ("Carbs", f"{macros.get('carbs', 0):.1f}", "g", "#f59e0b"),
        ("Fat", f"{macros.get('fat', 0):.1f}", "g", "#ef4444"),
        ("Fiber", f"{macros.get('fiber', 0):.1f}", "g", "#8b5cf6"),
    ])

    st.markdown("")
    badge_color = "#10b981" if health_score >= 80 else ("#f59e0b" if health_score >= 60 else "#ef4444")
    meter_pct = max(0.0, min(100.0, health_score))
    st.markdown(
        f'<div class="fv-card">'
        f'<div style="display:flex;align-items:center;gap:1rem;flex-wrap:wrap;">'
        f'<div style="font-size:2.5rem;font-weight:900;color:{badge_color}">{health_score:.0f}</div>'
        f'<div style="flex:1 1 220px;">'
        f'<div style="font-size:1.05rem;font-weight:700;color:var(--fv-text)">Health Score — {label}</div>'
        f'<div style="color:var(--fv-text-muted);font-size:0.85rem;margin-bottom:0.45rem;">'
        f'Composite macro, fiber and calorie score (1–100)</div>'
        f'<span class="fv-meter"><span class="fv-meter-fill" style="width:{meter_pct:.1f}%;background:{badge_color}"></span></span>'
        f'</div></div></div>', unsafe_allow_html=True,
    )

    # Calorie contribution by macro (clearer than a pie of gram weights)
    st.markdown("")
    st.markdown('<div class="fv-card-title">Where the calories come from</div>', unsafe_allow_html=True)
    bar_chart(_calorie_contribution(macros))
    st.caption("Protein and carbs contribute 4 kcal/g, fat 9 kcal/g.")

    # Gauge for calories
    with st.container(key="fv_tab1_gauge"):
        st.plotly_chart(
            _render_calorie_gauge(macros.get("calories", 0)),
            width="stretch",
            config={"displayModeBar": False},
        )

    # Allergens
    st.divider()
    st.markdown('<div class="fv-section-title">⚠️ Allergen Alerts</div>', unsafe_allow_html=True)
    ingredients = vision.get("ingredients", [])
    dish_name = vision.get("dish_name", "")
    allergens = detect_allergens(dish_name, ingredients)
    if allergens:
        st.markdown(
            '<div class="fv-alert danger"><strong>Potential allergens detected</strong></div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="fv-chip-row">'
            + "".join(f'<span class="fv-tag">{esc(a)}</span>' for a in allergens)
            + "</div>",
            unsafe_allow_html=True,
        )
        st.caption("Cross-contamination possible. Verify with restaurant/packaging.")
    else:
        st.markdown(
            '<div class="fv-alert success">No common allergens detected from visual ingredients.</div>',
            unsafe_allow_html=True,
        )

    export_text = "\n".join([
        f"Dish: {vision.get('dish_name', '')}",
        f"Cuisine: {vision.get('cuisine', '')}",
        f"Portion: {vision.get('portion_size', '')}",
        f"Confidence: {vision.get('confidence', 0)}%",
        f"Macros: {format_macros(macros)}",
        f"Health score: {health_score:.0f} ({label})",
        f"Allergens: {', '.join(allergens) if allergens else 'none detected'}",
        f"Notes: {vision.get('notes', '')}",
    ])
    d_col, c_col = st.columns([1, 1])
    with d_col:
        download_button(export_text, "foodverse-nutrition.txt", label="Download report")
    with c_col:
        copy_button(export_text, "Copy summary", key="tab1_copy")

    st.caption("Macros and health score are AI-estimated when a provider is configured; "
               "otherwise they come from visual heuristics. For clinical accuracy, log ingredients precisely.")
