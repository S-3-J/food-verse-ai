"""Tab 4 - Smart Kitchen Recipe Assistant (Epic 4)."""
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from ai_client import AIClient
from config import AppConfig
from personas import build_system_prompt, get_persona
from utils import parse_json_safe


SYSTEM_PROMPT = build_system_prompt(
    get_persona("Chef Verse"),
    "Smart kitchen recipe assistant. Generate creative, nutritious recipes from pantry ingredients "
    "with cooking time, difficulty, step-by-step instructions, and ingredient substitutions.",
)

TEXT_PROMPT_TEMPLATE = """Create a nutritious recipe using these pantry ingredients: {ingredients}.

Return ONLY a JSON object with these exact keys:
- "title": string
- "description": string (one sentence)
- "cooking_time": string (e.g., "30 mins")
- "difficulty": one of ["Easy", "Medium", "Hard"]
- "servings": number
- "ingredients_used": array of strings (from pantry)
- "additional_ingredients": array of strings (optional pantry-staple additions)
- "instructions": array of strings (numbered step-by-step)
- "substitutions": object mapping ingredient -> substitute (for dietary flexibility)
- "nutrition_estimate": object with calories, protein_g, carbs_g, fat_g (estimates)
- "tips": array of strings (chef tips)

Keep it creative, nutritious, and practical."""


def _demo_recipe(ingredients: List[str]) -> Dict[str, Any]:
    ing_str = ", ".join(ingredients) if ingredients else "basic pantry staples"
    return {
        "title": f"Pantry {ing_str.title()} Creation",
        "description": "A creative demo recipe built from your available ingredients.",
        "cooking_time": "30 mins",
        "difficulty": "Easy",
        "servings": 2,
        "ingredients_used": ingredients if ingredients else ["Olive oil", "Salt", "Pepper"],
        "additional_ingredients": ["Garlic", "Lemon", "Fresh herbs"],
        "instructions": [
            "Prep and wash all pantry ingredients.",
            "Heat a pan with olive oil over medium heat.",
            "Sauté aromatics until fragrant.",
            "Add main ingredients and cook until done.",
            "Season to taste and serve warm.",
        ],
        "substitutions": {"Olive oil": "Avocado oil or butter", "Garlic": "Garlic powder or shallot"},
        "nutrition_estimate": {"calories": 320, "protein_g": 18, "carbs_g": 30, "fat_g": 14},
        "tips": ["Taste as you go", "Don't overcrowd the pan"],
        "notes": "Demo mode: AI provider not configured. Heuristic recipe only.",
    }


def _run_recipe(ai_client: AIClient, config: AppConfig, ingredients: List[str]) -> Dict[str, Any]:
    if config.demo_mode or not ai_client.is_available():
        return _demo_recipe(ingredients)
    try:
        system = SYSTEM_PROMPT
        user = TEXT_PROMPT_TEMPLATE.format(ingredients=", ".join(ingredients))
        text = ai_client.generate_text(system, user)
        return parse_json_safe(text, fallback=_demo_recipe(ingredients))
    except Exception as exc:  # pragma: no cover
        st.warning(f"AI recipe generation unavailable, using demo fallback: {exc}")
        return _demo_recipe(ingredients)


def render(config: AppConfig, ai_client: AIClient) -> None:
    st.header("👨‍🍳 Smart Kitchen Recipe Assistant")
    st.caption("Epic 4 — Generate creative, nutritious recipes from your pantry inventory.")

    st.subheader("📦 Pantry Inventory")
    pantry_input = st.text_area(
        "List available ingredients (comma-separated)",
        placeholder="e.g., chicken breast, spinach, garlic, cherry tomatoes, feta, olive oil",
        key="tab4_pantry",
    )
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        run_btn = st.button("Generate Recipe", key="tab4_run")

    ingredients = [i.strip() for i in pantry_input.split(",") if i.strip()] if pantry_input else []

    if not ingredients:
        st.info("Add pantry ingredients to generate a recipe. Demo mode runs without an API key.")
        return

    if run_btn or "tab4_result" not in st.session_state:
        with st.spinner("Crafting recipe from your pantry..."):
            result = _run_recipe(ai_client, config, ingredients)
        st.session_state["tab4_result"] = result

    result = st.session_state.get("tab4_result", {})

    st.divider()
    st.subheader(result.get("title", "Pantry Recipe"))
    st.caption(result.get("description", ""))

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.markdown(
            f'<div class="fv-metric"><span class="val">{result.get("cooking_time","—")}</span>'
            f'<span class="lab">Cooking Time</span></div>', unsafe_allow_html=True,
        )
    with m2:
        diff = result.get("difficulty", "Easy")
        diff_color = {"Easy": "#10b981", "Medium": "#f59e0b", "Hard": "#ef4444"}.get(diff, "#94a3b8")
        st.markdown(
            f'<div class="fv-metric"><span class="val" style="color:{diff_color}">{diff}</span>'
            f'<span class="lab">Difficulty</span></div>', unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="fv-metric"><span class="val">{result.get("servings","—")}</span>'
            f'<span class="lab">Servings</span></div>', unsafe_allow_html=True,
        )
    with m4:
        nut = result.get("nutrition_estimate", {})
        st.markdown(
            f'<div class="fv-metric"><span class="val">{nut.get("calories","—")}</span>'
            f'<span class="lab">Est. Calories/serving</span></div>', unsafe_allow_html=True,
        )

    st.markdown("### 🛒 Ingredients Used")
    used = result.get("ingredients_used", [])
    st.write(", ".join(used) if used else "—")

    add = result.get("additional_ingredients", [])
    if add:
        st.markdown("### ➕ Suggested Additions")
        st.write(", ".join(add))

    st.markdown("### 👩‍🍳 Step-by-Step Instructions")
    instructions = result.get("instructions", [])
    if instructions:
        for idx, step in enumerate(instructions, 1):
            st.markdown(f"{idx}. {step}")
    else:
        st.caption("No instructions available.")

    st.markdown("### 🔄 Ingredient Substitutions")
    subs = result.get("substitutions", {})
    if subs:
        for k, v in subs.items():
            st.markdown(f"• **{k}** → {v}")
    else:
        st.caption("No substitutions listed.")

    st.markdown("### 💡 Chef Tips")
    for tip in result.get("tips", []):
        st.markdown(f"• {tip}")

    # Nutrition estimate mini chart
    if nut:
        st.divider()
        st.subheader("📊 Estimated Nutrition (per serving)")
        cn1, cn2, cn3, cn4 = st.columns(4)
        for col, (label_m, val, unit) in zip(
            [cn1, cn2, cn3, cn4],
            [("Calories", nut.get("calories", 0), "kcal"),
             ("Protein", nut.get("protein_g", 0), "g"),
             ("Carbs", nut.get("carbs_g", 0), "g"),
             ("Fat", nut.get("fat_g", 0), "g")],
        ):
            with col:
                st.markdown(
                    f'<div class="fv-metric"><span class="val">{val}</span>'
                    f'<span class="lab">{label_m} ({unit})</span></div>', unsafe_allow_html=True,
                )

    if result.get("notes"):
        st.caption(f"🔎 {result['notes']}")
