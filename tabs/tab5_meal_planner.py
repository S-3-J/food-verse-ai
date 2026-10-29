"""Tab 5 - Personalized Meal Planner (Epic 5)."""
from __future__ import annotations

from typing import Any, Dict, List

import streamlit as st

from ai_client import AIClient
from config import (
    ACTIVITY_LEVELS,
    DIETARY_CONSTRAINTS,
    FITNESS_GOALS,
    GENDERS,
)
from personas import build_system_prompt, get_persona
from ui import copy_button, data_table, download_button, metric_strip, reserve_analysis
from utils import esc, parse_json_safe, text_fingerprint


GROCERY_CATEGORIES = {
    "Produce": [
        "Avocado", "Apple", "Apples", "Almonds", "Asparagus", "Bell pepper", "Berries", "Carrots",
        "Cherry tomatoes", "Fresh herbs", "Garlic", "Kale", "Lemon", "Lettuce", "Mushrooms",
        "Onion", "Potatoes", "Spinach", "Sweet potato", "Tomatoes", "Banana", "Broccoli",
    ],
    "Protein": [
        "Chicken", "Chicken breast", "Beef", "Lean beef", "Turkey", "Salmon", "Tofu", "Shrimp",
        "Eggs", "Egg", "Lentils", "Chickpeas", "Tuna", "Pork",
    ],
    "Dairy & Chilled": [
        "Greek yogurt", "Yogurt", "Milk", "Cheddar cheese", "Feta", "Cottage cheese", "Butter",
        "Cheese", "Cream cheese", "Hummus",
    ],
    "Pantry": [
        "Oats", "Rice", "Pasta", "Quinoa", "Olive oil", "Avocado oil", "Salt", "Pepper",
        "Sugar", "Flour", "Garlic powder", "Soy sauce", "Coconut milk", "Tomato paste",
        "Stock", "Vinegar", "Cinnamon", "Honey",
    ],
    "Other": ["Protein powder", "Protein shake", "Nuts", "Seeds", "Chocolate", "Coffee", "Tea"],
}


SYSTEM_PROMPT = build_system_prompt(
    get_persona("Nutritionist Nova"),
    "Personalized meal planner. Compute BMR/TDEE using Mifflin-St Jeor, generate a 7-day adaptive meal "
    "schedule respecting dietary constraints and fitness goals, plus an automated grocery list.",
)

TEXT_PROMPT_TEMPLATE = """User profile:
- Age: {age}, Gender: {gender}, Weight: {weight} kg, Height: {height} cm
- Activity level: {activity} (multiplier {activity_mult})
- Dietary constraints: {diet}
- Fitness goal: {goal}
- Daily calorie target (TDEE adjusted): {target} kcal

Generate a 7-day meal plan (Breakfast, Lunch, Dinner, Snack per day) respecting the dietary constraints
and goal. Return ONLY a JSON object with keys:
- "bmr": number
- "tdee": number
- "daily_target": number
- "plan": object keyed "Day 1".."Day 7", each value an object with "breakfast","lunch","dinner","snack" (strings)
- "grocery_list": array of strings (consolidated shopping list)
- "notes": array of strings (adherence tips)

Use Mifflin-St Jeor for BMR. Apply goal adjustment: Fat Loss -500 kcal, Muscle Gain +300 kcal, Maintenance 0."""


def compute_bmr(weight: float, height: float, age: int, gender: str) -> float:
    """Mifflin-St Jeor equation."""
    if gender.lower() == "male":
        return 10 * weight + 6.25 * height - 5 * age + 5
    return 10 * weight + 6.25 * height - 5 * age - 161


def goal_adjustment(goal: str) -> int:
    return {"Fat Loss": -500, "Muscle Gain": 300, "Maintenance": 0, "General Health": 0}.get(goal, 0)


def _demo_meal_plan(profile: Dict[str, Any]) -> Dict[str, Any]:
    bmr = compute_bmr(profile["weight"], profile["height"], profile["age"], profile["gender"])
    mult = dict(ACTIVITY_LEVELS)[profile["activity"]]
    tdee = bmr * mult
    target = tdee + goal_adjustment(profile["goal"])

    days = [f"Day {i}" for i in range(1, 8)]
    meals = ["breakfast", "lunch", "dinner", "snack"]
    meal_pool = {
        "breakfast": ["Oatmeal with berries", "Greek yogurt parfait", "Avocado toast", "Veggie omelet"],
        "lunch": ["Grilled chicken salad", "Quinoa bowl", "Lentil soup", "Turkey wrap"],
        "dinner": ["Salmon with asparagus", "Tofu stir-fry", "Lean beef tacos", "Chicken pasta"],
        "snack": ["Apple & almonds", "Protein shake", "Hummus & carrots", "Cottage cheese"],
    }
    plan = {}
    for i, day in enumerate(days):
        plan[day] = {m: meal_pool[m][i % len(meal_pool[m])] for m in meals}

    grocery = ["Oats", "Berries", "Greek yogurt", "Avocado", "Eggs", "Spinach", "Chicken breast",
               "Quinoa", "Lentils", "Turkey", "Salmon", "Asparagus", "Tofu", "Lean beef",
               "Apples", "Almonds", "Protein powder", "Carrots", "Hummus", "Cottage cheese"]

    return {
        "bmr": round(bmr, 1),
        "tdee": round(tdee, 1),
        "daily_target": round(target, 1),
        "plan": plan,
        "grocery_list": grocery,
        "notes": ["Demo mode: AI provider not configured. Heuristic plan only.",
                  "Adjust portions to hit your daily calorie target.",
                  "Hydrate: aim for 2-3 L water daily."],
    }


def _run_plan(ai_client: AIClient, config: AppConfig, profile: Dict[str, Any]) -> Dict[str, Any]:
    if config.demo_mode or not ai_client.is_available():
        return _demo_meal_plan(profile)
    try:
        system = SYSTEM_PROMPT
        mult = dict(ACTIVITY_LEVELS)[profile["activity"]]
        bmr = compute_bmr(profile["weight"], profile["height"], profile["age"], profile["gender"])
        tdee = bmr * mult
        target = tdee + goal_adjustment(profile["goal"])
        user = TEXT_PROMPT_TEMPLATE.format(
            age=profile["age"], gender=profile["gender"], weight=profile["weight"],
            height=profile["height"], activity=profile["activity"], activity_mult=mult,
            diet=", ".join(profile["diet"]), goal=profile["goal"], target=round(target, 1),
        )
        text = ai_client.generate_text(system, user)
        data = parse_json_safe(text, fallback={})
        if not data:
            return _demo_meal_plan(profile)
        # Ensure computed baseline fields present
        data.setdefault("bmr", round(bmr, 1))
        data.setdefault("tdee", round(tdee, 1))
        data.setdefault("daily_target", round(target, 1))
        return data
    except Exception as exc:  # pragma: no cover
        st.warning(f"AI meal planning unavailable, using demo fallback: {exc}")
        return _demo_meal_plan(profile)


def group_grocery(items: List[str]) -> Dict[str, List[str]]:
    """Sort grocery items into aisles, keeping unknown items in Other."""
    grouped: Dict[str, List[str]] = {}
    for item in items:
        text = str(item).strip()
        if not text:
            continue
        lowered = text.lower()
        placed = False
        for category, keywords in GROCERY_CATEGORIES.items():
            if any(k.lower() in lowered or lowered in k.lower() for k in keywords):
                grouped.setdefault(category, []).append(text)
                placed = True
                break
        if not placed:
            grouped.setdefault("Other", []).append(text)
    return grouped


def render(config: AppConfig, ai_client: AIClient) -> None:
    with st.form("tab5_profile_form"):
        st.markdown('<div class="fv-section-title">👤 User Profile</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            age = st.number_input("Age", 13, 90, 30, key="tab5_age")
            weight = st.number_input("Weight (kg)", 30.0, 250.0, 70.0, key="tab5_weight")
        with c2:
            gender = st.selectbox("Gender", GENDERS, index=0, key="tab5_gender")
            height = st.number_input("Height (cm)", 100, 250, 170, key="tab5_height")
        with c3:
            activity_label = st.selectbox(
                "Activity Level",
                [a[0] for a in ACTIVITY_LEVELS],
                index=2,
                key="tab5_activity",
            )
        c4, c5 = st.columns(2)
        with c4:
            diet = st.multiselect("Dietary Constraints", DIETARY_CONSTRAINTS, default=["None"], key="tab5_diet")
        with c5:
            goal = st.selectbox("Fitness Goal", FITNESS_GOALS, index=2, key="tab5_goal")
        submitted = st.form_submit_button("Compute Plan", type="primary", width="stretch")

    warnings = []
    if weight < 40 or weight > 200:
        warnings.append("Weight looks unusual — verify the value before relying on the calorie target.")
    if height < 130 or height > 220:
        warnings.append("Height looks unusual — verify the value before relying on the calorie target.")
    if age < 16:
        warnings.append("Under 16 — calorie targets need paediatric guidance rather than this estimate.")
    if diet and "None" in diet and len(diet) > 1:
        warnings.append("'None' combined with other constraints is contradictory — remove 'None'.")
    if warnings:
        st.markdown(
            '<div class="fv-alert warn"><strong>Check your inputs</strong><br/>'
            + "<br/>".join(esc(w) for w in warnings)
            + "</div>",
            unsafe_allow_html=True,
        )

    activity_mult = dict(ACTIVITY_LEVELS)[activity_label]
    profile = {
        "age": int(age), "gender": gender, "weight": float(weight),
        "height": float(height), "activity": activity_label, "activity_mult": activity_mult,
        "diet": diet, "goal": goal,
    }

    fingerprint = text_fingerprint(
        profile["age"], profile["gender"], profile["weight"], profile["height"],
        profile["activity"], ",".join(profile["diet"]), profile["goal"],
    )
    stored_fp = st.session_state.get("tab5_fp")
    if submitted or "tab5_result" not in st.session_state or stored_fp != fingerprint:
        if not reserve_analysis(config, ai_client):
            return
        with st.spinner("Computing BMR/TDEE and generating meal plan..."):
            result = _run_plan(ai_client, config, profile)
        st.session_state["tab5_result"] = result
        st.session_state["tab5_profile"] = profile
        st.session_state["tab5_fp"] = fingerprint
    else:
        result = st.session_state["tab5_result"]

    prof = st.session_state.get("tab5_profile", profile)

    bmr = float(result.get("bmr", compute_bmr(prof["weight"], prof["height"], prof["age"], prof["gender"])))
    tdee = float(result.get("tdee", bmr * prof["activity_mult"]))
    target = float(result.get("daily_target", tdee + goal_adjustment(prof["goal"])))

    st.divider()
    st.markdown('<div class="fv-section-title">⚡ Energy Targets</div>', unsafe_allow_html=True)
    metric_strip([
        ("BMR", f"{bmr:.0f}", "kcal/day", "#8b5cf6"),
        ("TDEE", f"{tdee:.0f}", "kcal/day", "#0ea5e9"),
        ("Daily Target", f"{target:.0f}", "kcal/day", "#10b981"),
        ("Adjustment", f"{goal_adjustment(prof['goal']):+}", "kcal", "#f59e0b"),
    ])
    st.caption(f"Mifflin-St Jeor BMR × {activity_mult} activity, goal adjustment: {goal_adjustment(prof['goal']):+} kcal.")

    st.divider()
    st.markdown('<div class="fv-section-title">🗓️ 7-Day Meal Schedule</div>', unsafe_allow_html=True)
    plan = result.get("plan", {})
    plan_rows = []
    for day in [f"Day {i}" for i in range(1, 8)]:
        meals = plan.get(day, {})
        plan_rows.append([
            day,
            esc(meals.get("breakfast", "—")),
            esc(meals.get("lunch", "—")),
            esc(meals.get("dinner", "—")),
            esc(meals.get("snack", "—")),
        ])
    data_table(["Day", "Breakfast", "Lunch", "Dinner", "Snack"], plan_rows, empty="No plan generated.")

    st.divider()
    st.markdown('<div class="fv-section-title">🛒 Automated Grocery List</div>', unsafe_allow_html=True)
    grocery = result.get("grocery_list", [])
    grouped = group_grocery(grocery)
    if grouped:
        gcols = st.columns(len(grouped))
        for col, (category, items) in zip(gcols, grouped.items()):
            with col:
                st.markdown(
                    f'<div class="fv-card" style="height:100%;">'
                    f'<div class="fv-card-title">{esc(category)}</div>'
                    f'<ul style="color:var(--fv-text-soft);line-height:1.7;padding-left:1.1rem;margin:0.2rem 0 0 0;">'
                    + "".join(f"<li>{esc(i)}</li>" for i in items)
                    + "</ul></div>",
                    unsafe_allow_html=True,
                )
    else:
        st.caption("No grocery list generated.")

    st.divider()
    st.markdown('<div class="fv-section-title">📝 Notes</div>', unsafe_allow_html=True)
    notes = result.get("notes", [])
    if notes:
        st.markdown(
            '<ul style="color:var(--fv-text-soft);line-height:1.7;margin-top:0.2rem;">'
            + "".join(f"<li>{esc(n)}</li>" for n in notes)
            + "</ul>",
            unsafe_allow_html=True,
        )
    else:
        st.caption("No notes available.")

    plan_text = "\n".join([
        "7-Day Meal Plan",
        f"BMR {bmr:.0f} kcal | TDEE {tdee:.0f} kcal | Target {target:.0f} kcal",
        "",
        *[" | ".join(row) for row in plan_rows],
        "",
        "Grocery list:",
        *[f"- {item}" for item in grocery],
    ])
    d_col, c_col = st.columns([1, 1])
    with d_col:
        download_button(plan_text, "foodverse-meal-plan.txt", label="Download plan")
    with c_col:
        copy_button(plan_text, "Copy plan", key="tab5_copy")
