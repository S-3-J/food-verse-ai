"""Tab 1 - Food Recognition & Nutrition Audit (Epic 2)."""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

import streamlit as st
import plotly.graph_objects as go

from ai_client import AIClient
from config import AppConfig
from personas import build_system_prompt, get_persona
from utils import (
    detect_allergens,
    estimate_portion_from_image,
    format_macros,
    fallback_nutrition,
    compute_health_score,
    image_bytes,
    load_image,
    parse_json_safe,
    score_to_badge,
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
        # Ensure all required keys exist, fall back to heuristics for missing ones
        demo = _demo_vision_analysis(image)
        for key in [
            "dish_name", "cuisine", "ingredients", "portion_size",
            "calories", "protein", "carbs", "fat", "fiber",
            "health_score", "confidence", "notes",
        ]:
            if key not in result or result[key] is None or result[key] == "":
                result[key] = demo.get(key)
        # Coerce numeric types
        for num_key in ["calories", "protein", "carbs", "fat", "fiber", "health_score", "confidence"]:
            try:
                result[num_key] = float(result.get(num_key, demo.get(num_key, 0)))
            except (TypeError, ValueError):
                result[num_key] = float(demo.get(num_key, 0))
        return result
    except Exception as exc:  # pragma: no cover - defensive UI
        st.warning(f"AI vision unavailable, using demo fallback: {exc}")
        return _demo_vision_analysis(image)


def _render_macro_chart(macros: Dict[str, float]) -> go.Figure:
    labels = ["Protein (g)", "Carbs (g)", "Fat (g)", "Fiber (g)"]
    values = [macros.get("protein", 0), macros.get("carbs", 0),
              macros.get("fat", 0), macros.get("fiber", 0)]
    colors = ["#06b6d4", "#10b981", "#f59e0b", "#8b5cf6"]
    fig = go.Figure(data=[go.Pie(
        labels=labels, values=values, hole=0.45, marker=dict(colors=colors),
        textinfo="label+percent", hoverinfo="label+value",
    )])
    fig.update_layout(
        showlegend=True, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f1f5f9", size=12), margin=dict(t=20, b=20, l=20, r=20),
        legend=dict(font=dict(color="#f1f5f9")),
    )
    return fig


def _render_calorie_gauge(calories: float) -> go.Figure:
    fig = go.Figure(go.Indicator(
        mode="gauge+number", value=calories,
        domain={"x": [0, 1], "y": [0, 1]},
        title={"text": "Estimated Calories (kcal)", "font": {"color": "#f1f5f9", "size": 14}},
        number={"font": {"color": "#06b6d4", "size": 32}},
        gauge={
            "axis": {"range": [0, 1200], "tickcolor": "#94a3b8"},
            "bar": {"color": "#06b6d4"},
            "bgcolor": "rgba(0,0,0,0)",
            "bordercolor": "#334155",
            "steps": [
                {"range": [0, 400], "color": "rgba(16,185,129,0.15)"},
                {"range": [400, 800], "color": "rgba(245,158,11,0.15)"},
                {"range": [800, 1200], "color": "rgba(239,68,68,0.15)"},
            ],
        },
    ))
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="#f1f5f9"), margin=dict(t=40, b=10, l=10, r=10),
                      height=220)
    return fig


def render(config: AppConfig, ai_client: AIClient) -> None:
    st.header("🍽️ Food Recognition & Nutrition Audit")
    st.caption("Epic 2 — Multimodal dish identification with macro breakdown and health scoring.")

    col_up, col_ctrl = st.columns([3, 1])
    with col_up:
        uploaded = st.file_uploader("Upload a meal or dish photo", type=["jpg", "jpeg", "png", "webp"])
    with col_ctrl:
        run_btn = st.button("Analyze Image", key="tab1_run")

    if not uploaded:
        st.info("Upload a dish photo to begin. Demo mode runs without an API key.")
        return

    image = load_image(uploaded)
    if image is None:
        st.error("Failed to load image.")
        return

    st.image(image, caption="Uploaded dish", use_container_width=True)

    if run_btn or "tab1_result" not in st.session_state:
        with st.spinner("Analyzing dish with vision model..."):
            vision = _run_vision(ai_client, config, image)
        st.session_state["tab1_result"] = vision

    vision = st.session_state.get("tab1_result", {})

    # Use model-provided macros when available (already merged with fallback in _run_vision)
    macros = {
        "calories": float(vision.get("calories", 0)),
        "protein": float(vision.get("protein", 0)),
        "carbs": float(vision.get("carbs", 0)),
        "fat": float(vision.get("fat", 0)),
        "fiber": float(vision.get("fiber", 0)),
    }
    health_score = float(vision.get("health_score", compute_health_score(macros, vision.get("dish_name", ""))))
    label, _ = score_to_badge(health_score)

    # Results header
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Dish", vision.get("dish_name", "Unknown"))
    with c2:
        st.metric("Cuisine", vision.get("cuisine", "Unknown"))
    with c3:
        conf = vision.get("confidence", 0)
        st.metric("Confidence", f"{conf}%")

    st.markdown(f"**Portion:** {vision.get('portion_size', 'Not estimated')}")
    st.markdown(f"**Ingredients:** {', '.join(vision.get('ingredients', []))}")
    if vision.get("notes"):
        st.caption(f"🔎 {vision['notes']}")

    st.divider()

    # Nutrition macros
    st.subheader("📊 Nutritional Breakdown")

    g1, g2, g3, g4, g5 = st.columns(5)
    metrics = [
        ("Calories", f"{macros.get('calories', 0):.0f}", "kcal", "#06b6d4"),
        ("Protein", f"{macros.get('protein', 0):.1f}", "g", "#10b981"),
        ("Carbs", f"{macros.get('carbs', 0):.1f}", "g", "#f59e0b"),
        ("Fat", f"{macros.get('fat', 0):.1f}", "g", "#ef4444"),
        ("Fiber", f"{macros.get('fiber', 0):.1f}", "g", "#8b5cf6"),
    ]
    for col, (label_m, val, unit, color) in zip([g1, g2, g3, g4, g5], metrics):
        with col:
            st.markdown(
                f'<div class="fv-metric">'
                f'<span class="val" style="color:{color}">{val}</span>'
                f'<span class="lab">{label_m} <small style="opacity:0.7">{unit}</small></span>'
                f'</div>', unsafe_allow_html=True,
            )

    # Health score badge
    badge_color = "#10b981" if health_score >= 80 else ("#f59e0b" if health_score >= 60 else "#ef4444")
    st.markdown(
        f'<div class="fv-card" style="margin-top:1rem;">'
        f'<div style="display:flex;align-items:center;gap:1rem;">'
        f'<div style="font-size:3rem;font-weight:900;color:{badge_color}">{health_score:.0f}</div>'
        f'<div><div style="font-size:1.1rem;font-weight:700;">Health Score</div>'
        f'<div style="color:#94a3b8;font-size:0.9rem">{label} (1-100) • Composite macro/fiber/calorie heuristic</div></div>'
        f'</div></div>', unsafe_allow_html=True,
    )

    # Charts
    ch1, ch2 = st.columns(2)
    with ch1:
        st.plotly_chart(_render_macro_chart(macros), use_container_width=True)
    with ch2:
        st.plotly_chart(_render_calorie_gauge(macros.get("calories", 0)), use_container_width=True)

    # Allergens
    st.divider()
    st.subheader("⚠️ Allergen Alerts")
    ingredients = vision.get("ingredients", [])
    dish_name = vision.get("dish_name", "")
    allergens = detect_allergens(dish_name, ingredients)
    if allergens:
        st.error("Potential allergens detected: " + ", ".join(allergens))
        st.caption("Cross-contamination possible. Verify with restaurant/packaging.")
    else:
        st.success("No common allergens detected from visual ingredients.")

    st.divider()
    st.subheader("📝 Vision Notes")
    st.write(vision.get("notes", "No notes available."))
    st.caption("Macros and health score are AI-estimated when a provider is configured; "
               "otherwise they come from visual heuristics. For clinical accuracy, log ingredients precisely.")
