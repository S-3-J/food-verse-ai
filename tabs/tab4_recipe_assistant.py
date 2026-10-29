"""Tab 4 - Smart Kitchen Recipe Assistant (Epic 4)."""
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from ai_client import AIClient
from config import AppConfig
from personas import build_system_prompt, get_persona
from ui import (
    chip_input,
    copy_button,
    data_table,
    download_button,
    empty_state,
    metric_strip,
    reserve_analysis,
)
from utils import esc, parse_json_safe, text_fingerprint


PANTRY_OPTIONS = [
    "Chicken breast", "Ground beef", "Salmon", "Eggs", "Tofu", "Shrimp",
    "Spinach", "Kale", "Broccoli", "Bell pepper", "Onion", "Garlic",
    "Cherry tomatoes", "Carrots", "Potatoes", "Sweet potato", "Avocado",
    "Lemon", "Olive oil", "Butter", "Rice", "Pasta", "Quinoa", "Oats",
    "Greek yogurt", "Cheddar cheese", "Feta", "Almonds", "Chickpeas", "Lentils",
]

COOK_MODES = {
    "Quick & easy": "Keep total cooking time under 30 minutes and favour few steps.",
    "Balanced weeknight": "Aim for a balanced macro split with about 35-45 minutes of cooking.",
    "Slow cook": "Prefer slow-cooker or oven methods with longer, unattended cooking time.",
    "Batch cook": "Optimise for 4-6 servings that keep well for several days.",
}

SYSTEM_PROMPT = build_system_prompt(
    get_persona("Chef Verse"),
    "Smart kitchen recipe assistant. Generate creative, nutritious recipes from pantry ingredients "
    "with cooking time, difficulty, step-by-step instructions, and ingredient substitutions.",
)

TEXT_PROMPT_TEMPLATE = """Create a nutritious recipe using these pantry ingredients: {ingredients}.
Cook mode: {cook_mode}
{cook_hint}

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


def _run_recipe(
    ai_client: AIClient,
    config: AppConfig,
    ingredients: List[str],
    cook_mode: str = "Balanced weeknight",
) -> Dict[str, Any]:
    if config.demo_mode or not ai_client.is_available():
        return _demo_recipe(ingredients)
    try:
        system = SYSTEM_PROMPT
        user = TEXT_PROMPT_TEMPLATE.format(
            ingredients=", ".join(ingredients),
            cook_mode=cook_mode,
            cook_hint=COOK_MODES.get(cook_mode, ""),
        )
        text = ai_client.generate_text(system, user)
        return parse_json_safe(text, fallback=_demo_recipe(ingredients))
    except Exception as exc:  # pragma: no cover
        st.warning(f"AI recipe generation unavailable, using demo fallback: {exc}")
        return _demo_recipe(ingredients)


def render(config: AppConfig, ai_client: AIClient) -> None:
    st.markdown('<div class="fv-section-title">📦 Pantry Inventory</div>', unsafe_allow_html=True)
    cook_mode = st.selectbox(
        "Cook mode",
        list(COOK_MODES.keys()),
        index=1,
        key="tab4_cook_mode",
        help=COOK_MODES.get("Balanced weeknight", ""),
    )
    ingredients = chip_input(
        PANTRY_OPTIONS,
        key="tab4_pantry",
        label="Available ingredients",
        placeholder="e.g., cherry tomatoes, feta",
    )
    if ingredients:
        st.markdown(
            '<div class="fv-chip-row">'
            + "".join(f'<span class="fv-tag">{esc(i)}</span>' for i in ingredients)
            + "</div>",
            unsafe_allow_html=True,
        )

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        run_btn = st.button("Generate Recipe", key="tab4_run", type="primary")

    if not ingredients:
        empty_state(
            "👨‍🍳",
            "Your pantry is empty",
            "Pick ingredients from the list or type your own — the assistant will build a recipe "
            "around them. Demo mode runs without an API key.",
        )
        return

    fingerprint = text_fingerprint(",".join(sorted(ingredients)), cook_mode)
    stored_fp = st.session_state.get("tab4_fp")
    if run_btn or "tab4_result" not in st.session_state or stored_fp != fingerprint:
        if not reserve_analysis(config, ai_client):
            return
        with st.spinner("Crafting recipe from your pantry..."):
            result = _run_recipe(ai_client, config, ingredients, cook_mode)
        st.session_state["tab4_result"] = result
        st.session_state["tab4_fp"] = fingerprint
    else:
        result = st.session_state["tab4_result"]

    st.divider()
    st.markdown(f"### {esc(result.get('title', 'Pantry Recipe'))}")
    st.caption(esc(result.get("description", "")))

    nut = result.get("nutrition_estimate", {})
    diff = result.get("difficulty", "Easy")
    diff_color = {"Easy": "#10b981", "Medium": "#f59e0b", "Hard": "#ef4444"}.get(diff, "#94a3b8")
    metric_strip([
        ("Cooking Time", str(result.get("cooking_time", "—")), "", "#0ea5e9"),
        ("Difficulty", diff, "", diff_color),
        ("Servings", str(result.get("servings", "—")), "", "#10b981"),
        ("Est. Calories", str(nut.get("calories", "—")), "kcal", "#f59e0b"),
    ])

    st.markdown('<div class="fv-section-title">🛒 Ingredients Used</div>', unsafe_allow_html=True)
    used = result.get("ingredients_used", [])
    st.markdown(
        '<div class="fv-chip-row">'
        + "".join(f'<span class="fv-tag">{esc(u)}</span>' for u in used)
        + "</div>" if used else '<span class="fv-card-body">None listed.</span>',
        unsafe_allow_html=True,
    )

    add = result.get("additional_ingredients", [])
    if add:
        st.markdown('<div class="fv-section-title">➕ Suggested Additions</div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="fv-chip-row">'
            + "".join(f'<span class="fv-tag">{esc(a)}</span>' for a in add)
            + "</div>",
            unsafe_allow_html=True,
        )

    st.markdown('<div class="fv-section-title">👩‍🍳 Step-by-Step Instructions</div>', unsafe_allow_html=True)
    instructions = result.get("instructions", [])
    if instructions:
        st.markdown(
            '<ol style="color:var(--fv-text-soft);line-height:1.75;margin-top:0.2rem;">'
            + "".join(f"<li>{esc(s)}</li>" for s in instructions)
            + "</ol>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("No instructions available.")

    st.markdown('<div class="fv-section-title">🔄 Ingredient Substitutions</div>', unsafe_allow_html=True)
    subs = result.get("substitutions", {})
    if subs:
        data_table(["Ingredient", "Substitute"], [[esc(k), esc(v)] for k, v in subs.items()])
    else:
        st.caption("No substitutions listed.")

    st.markdown('<div class="fv-section-title">💡 Chef Tips</div>', unsafe_allow_html=True)
    tips = result.get("tips", [])
    if tips:
        st.markdown(
            '<ul style="color:var(--fv-text-soft);line-height:1.7;margin-top:0.2rem;">'
            + "".join(f"<li>{esc(t)}</li>" for t in tips)
            + "</ul>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("No tips listed.")

    # Nutrition estimate mini chart
    if nut:
        st.divider()
        st.markdown('<div class="fv-section-title">📊 Estimated Nutrition (per serving)</div>', unsafe_allow_html=True)
        metric_strip([
            ("Calories", str(nut.get("calories", 0)), "kcal", "#0ea5e9"),
            ("Protein", str(nut.get("protein_g", 0)), "g", "#10b981"),
            ("Carbs", str(nut.get("carbs_g", 0)), "g", "#f59e0b"),
            ("Fat", str(nut.get("fat_g", 0)), "g", "#ef4444"),
        ])

    recipe_text = "\n".join([
        result.get("title", "Pantry Recipe"),
        result.get("description", ""),
        f"Cooking time: {result.get('cooking_time', '')} · Difficulty: {result.get('difficulty', '')} · "
        f"Servings: {result.get('servings', '')}",
        "",
        "Ingredients used: " + ", ".join(used),
        "Suggested additions: " + ", ".join(add),
        "",
        "Instructions:",
        *[f"{i}. {s}" for i, s in enumerate(instructions, 1)],
        "",
        "Substitutions:",
        *[f"- {k} → {v}" for k, v in subs.items()],
        "",
        "Tips:",
        *[f"- {t}" for t in tips],
    ])
    d_col, c_col = st.columns([1, 1])
    with d_col:
        download_button(recipe_text, "foodverse-recipe.txt", label="Download recipe")
    with c_col:
        copy_button(recipe_text, "Copy recipe", key="tab4_copy")

    if result.get("notes"):
        st.caption(f"🔎 {esc(result['notes'])}")
