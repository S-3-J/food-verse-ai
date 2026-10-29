"""Food Verse AI - Configuration & Constants."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - python-dotenv is optional
    pass

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

# Presentation metadata for navigation and landing cards
TAB_META: Dict[str, Dict[str, str]] = {
    "tab1": {
        "icon": "🍽️",
        "title": "Food Recognition",
        "blurb": "Identify a dish from a photo and audit macros, health score and allergens.",
        "persona": "Nutritionist Nova",
    },
    "tab2": {
        "icon": "🧪",
        "title": "Freshness Check",
        "blurb": "Stage the freshness of perishables with safety verdicts and storage tips.",
        "persona": "Safety Inspector Rex",
    },
    "tab3": {
        "icon": "🧼",
        "title": "Kitchen Hygiene",
        "blurb": "Score hygiene compliance and log itemized violations with corrective actions.",
        "persona": "Safety Inspector Rex",
    },
    "tab4": {
        "icon": "👨‍🍳",
        "title": "Recipe Assistant",
        "blurb": "Turn pantry ingredients into a practical recipe with swaps and chef tips.",
        "persona": "Chef Verse",
    },
    "tab5": {
        "icon": "📅",
        "title": "Meal Planner",
        "blurb": "Compute BMR/TDEE targets and generate a 7-day plan with a grocery list.",
        "persona": "Nutritionist Nova",
    },
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
    api_key: str = field(default="", repr=False)
    model_name: str = ""
    temperature: float = 0.3
    persona_name: str = DEFAULT_PERSONA_NAME
    persona_role: str = DEFAULT_PERSONA_ROLE
    enable_fallback: bool = True
    demo_mode: bool = True
    allow_user_api_key: bool = False
    max_runs_per_session: int = 25

    @property
    def is_ai_enabled(self) -> bool:
        return self.provider != "Demo / Fallback Mode" and bool(self.api_key)

    @property
    def effective_provider(self) -> str:
        return "demo" if not self.is_ai_enabled else self.provider


def get_gemini_model_name() -> str:
    """Model id for Gemini, taken from the ``GEMINI_MODEL`` secret.

    Empty means "not configured" - the app then uses heuristic results instead
    of guessing a model id that a provider may have retired.
    """
    return _secret("GEMINI_MODEL", "")


def get_groq_model_name() -> str:
    """Model id for Groq, taken from the ``GROQ_MODEL`` secret (empty = unset)."""
    return _secret("GROQ_MODEL", "")


def default_model_for(provider: str) -> str:
    """Resolve the model for a provider from its secret.

    The model always follows the selected provider; there is no free-text
    override. An empty result means the provider has no model configured and
    the app falls back to heuristic (demo) output.
    """
    if provider.startswith("Gemini"):
        return get_gemini_model_name()
    if provider == "Groq":
        return get_groq_model_name()
    return ""


def _secret(name: str, default: str = "") -> str:
    """Read a secret from the Streamlit secrets store, falling back to the env.

    On Streamlit Community Cloud the values entered in "Advanced settings → Secrets"
    are exposed through ``st.secrets`` and as environment variables. Locally the
    same values can live in ``.streamlit/secrets.toml`` or a ``.env`` file.
    """
    try:
        import streamlit as st

        value = st.secrets.get(name)
        if value:
            return str(value)
    except Exception:
        pass
    return os.getenv(name, default) or default


def _env_bool(name: str, default: bool = False) -> bool:
    raw = _secret(name, "").strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return default


def _env_int(name: str, default: int) -> int:
    try:
        return int(_secret(name, "").strip() or default)
    except (TypeError, ValueError):
        return default


def _env_temperature(default: float = 0.3) -> float:
    """Read TEMPERATURE from the environment, clamped to the valid range."""
    try:
        value = float(_secret("TEMPERATURE", "") or default)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, value))


def provider_api_key(provider: str) -> str:
    """Return the server-managed key for a provider (never exposed to the UI)."""
    if provider.startswith("Gemini"):
        return _secret("GOOGLE_API_KEY")
    if provider == "Groq":
        return _secret("GROQ_API_KEY")
    return ""


def load_env_config() -> AppConfig:
    """Build config from environment variables and secrets with safe defaults."""
    provider = _secret("FOOD_VERSE_PROVIDER", "Demo / Fallback Mode")
    api_key = provider_api_key(provider)
    if not api_key:
        api_key = _secret("GOOGLE_API_KEY") or _secret("GROQ_API_KEY")
    model_name = default_model_for(provider)
    return AppConfig(
        provider=provider,
        api_key=api_key,
        model_name=model_name,
        temperature=_env_temperature(),
        demo_mode=(provider == "Demo / Fallback Mode" or not api_key or not model_name),
        allow_user_api_key=_env_bool("ALLOW_USER_API_KEY", False),
        max_runs_per_session=max(0, _env_int("MAX_RUNS_PER_SESSION", 25)),
    )
