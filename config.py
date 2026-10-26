"""Food Verse AI - Configuration & Constants."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import List

APP_TITLE = "Food Verse AI"
APP_SUBTITLE = "Multimodal Food Intelligence Agent"
APP_VERSION = "3.0.0"
PLATFORM_ID = "6ac4ca021dcde6d7857c169a"
CATEGORY = "Generative AI | Nutrition, Freshness & Kitchen Safety"

# Default persona / assistant identity
DEFAULT_PERSONA_NAME = "Chef Verse"
DEFAULT_PERSONA_ROLE = "Multimodal Food Intelligence Agent"

# Supported AI providers
AI_PROVIDERS = ["Gemini (Google)", "Groq", "Demo / Fallback Mode"]

# Tab definitions
TABS = {
    "tab1": "1. Food Recognition & Nutrition Audit",
    "tab2": "2. Food Freshness & Spoilage Diagnostic",
    "tab3": "3. Kitchen Hygiene & Safety Compliance",
    "tab4": "4. Smart Kitchen Recipe Assistant",
    "tab5": "5. Personalized Meal Planner",
}

# Nutrition macro defaults
MACRO_KEYS = ["calories", "protein", "carbs", "fat", "fiber"]

# Allergen list used for alerts
COMMON_ALLERGENS = [
    "Peanuts", "Tree Nuts", "Milk", "Eggs", "Wheat", "Soy",
    "Fish", "Shellfish", "Sesame", "Sulfites",
]

# Freshness stages
FRESHNESS_STAGES = ["Fresh", "Moderately Fresh", "Spoiled"]

# Kitchen hygiene indicators
HYGIENE_INDICATORS = [
    "Chef Hat / Hairnet Compliance",
    "Glove Usage",
    "Sanitization State",
    "Cross-Contamination Hazards",
]

# Dietary constraints and fitness goals
DIETARY_CONSTRAINTS = ["None", "Vegan", "Keto", "Diabetic-Friendly", "Gluten-Free", "Dairy-Free"]
FITNESS_GOALS = ["Fat Loss", "Muscle Gain", "Maintenance", "General Health"]
ACTIVITY_LEVELS = [
    ("Sedentary (little/no exercise)", 1.2),
    ("Lightly active (1-3 days/week)", 1.375),
    ("Moderately active (3-5 days/week)", 1.55),
    ("Very active (6-7 days/week)", 1.725),
    ("Extra active (physical job/2x training)", 1.9),
]
GENDERS = ["Male", "Female", "Other / Prefer not to say"]


@dataclass
class AppConfig:
    provider: str = "Demo / Fallback Mode"
    api_key: str = ""
    model_name: str = ""
    temperature: float = 0.3
    persona_name: str = DEFAULT_PERSONA_NAME
    persona_role: str = DEFAULT_PERSONA_ROLE
    enable_fallback: bool = True
    demo_mode: bool = True

    @property
    def is_ai_enabled(self) -> bool:
        return self.provider != "Demo / Fallback Mode" and bool(self.api_key)

    @property
    def effective_provider(self) -> str:
        return "demo" if not self.is_ai_enabled else self.provider


def get_gemini_model_name() -> str:
    return os.getenv("GEMINI_MODEL", "gemini-1.5-flash")


def get_groq_model_name() -> str:
    return os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")


def load_env_config() -> AppConfig:
    """Build config from environment variables with safe defaults."""
    provider = os.getenv("FOOD_VERSE_PROVIDER", "Demo / Fallback Mode")
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GROQ_API_KEY") or ""
    if provider == "Gemini (Google)" and not api_key:
        api_key = os.getenv("GOOGLE_API_KEY", "")
    if provider == "Groq" and not api_key:
        api_key = os.getenv("GROQ_API_KEY", "")
    return AppConfig(
        provider=provider,
        api_key=api_key,
        model_name=get_gemini_model_name() if provider.startswith("Gemini") else get_groq_model_name(),
        demo_mode=(provider == "Demo / Fallback Mode" or not api_key),
    )
