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
from utils import parse_json_safe


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


def render(config: AppConfig, ai_client: AIClient) -> None:
    st.header("📅 Personalized Meal Planner")
    st.caption("Epic 5 — BMR/TDEE targets, 7-day adaptive meal schedule, and grocery list.")

    with st.form("tab5_profile_form"):
        st.subheader("👤 User Profile")
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
        submitted = st.form_submit_button("Compute Plan", use_container_width=True)

    activity_mult = dict(ACTIVITY_LEVELS)[activity_label]
    profile = {
        "age": int(age), "gender": gender, "weight": float(weight),
        "height": float(height), "activity": activity_label, "activity_mult": activity_mult,
        "diet": diet, "goal": goal,
    }

    if submitted or "tab5_result" not in st.session_state:
        with st.spinner("Computing BMR/TDEE and generating meal plan..."):
            result = _run_plan(ai_client, config, profile)
        st.session_state["tab5_result"] = result
        st.session_state["tab5_profile"] = profile

    result = st.session_state.get("tab5_result", {})
    prof = st.session_state.get("tab5_profile", profile)

    bmr = float(result.get("bmr", compute_bmr(prof["weight"], prof["height"], prof["age"], prof["gender"])))
    tdee = float(result.get("tdee", bmr * prof["activity_mult"]))
    target = float(result.get("daily_target", tdee + goal_adjustment(prof["goal"])))

    st.divider()
    st.subheader("⚡ Energy Targets")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.markdown(
            f'<div class="fv-metric"><span class="val">{bmr:.0f}</span>'
            f'<span class="lab">BMR (kcal/day)</span></div>', unsafe_allow_html=True,
        )
    with m2:
        st.markdown(
            f'<div class="fv-metric"><span class="val">{tdee:.0f}</span>'
            f'<span class="lab">TDEE (kcal/day)</span></div>', unsafe_allow_html=True,
        )
    with m3:
        st.markdown(
            f'<div class="fv-metric"><span class="val">{target:.0f}</span>'
            f'<span class="lab">Daily Target (kcal)</span></div>', unsafe_allow_html=True,
        )
    st.caption(f"Mifflin-St Jeor BMR × {activity_mult} activity, goal adjustment: {goal_adjustment(prof['goal']):+} kcal.")

    st.divider()
    st.subheader("🗓️ 7-Day Meal Schedule")
    plan = result.get("plan", {})
    for day in [f"Day {i}" for i in range(1, 8)]:
        meals = plan.get(day, {})
        with st.expander(day, expanded=(day == "Day 1")):
            mm1, mm2 = st.columns(2)
            with mm1:
                st.markdown("**Breakfast:** " + meals.get("breakfast", "—"))
                st.markdown("**Lunch:** " + meals.get("lunch", "—"))
            with mm2:
                st.markdown("**Dinner:** " + meals.get("dinner", "—"))
                st.markdown("**Snack:** " + meals.get("snack", "—"))

    st.divider()
    st.subheader("🛒 Automated Grocery List")
    grocery = result.get("grocery_list", [])
    if grocery:
        cols = st.columns(3)
        for i, item in enumerate(grocery):
            with cols[i % 3]:
                st.checkbox(item, key=f"grocery_{i}")
    else:
        st.caption("No grocery list generated.")

    st.divider()
    st.subheader("📝 Notes")
    for note in result.get("notes", []):
        st.markdown(f"• {note}")
