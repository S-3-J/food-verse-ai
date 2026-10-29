"""Food Verse AI - Utility helpers (image analysis, formatting, fallback data)."""
from __future__ import annotations

import hashlib
import html
import io
import json
import re
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

import numpy as np
from PIL import Image


def load_image(uploaded_file) -> Optional[Image.Image]:
    """Load an uploaded file object into a PIL Image (RGB)."""
    if uploaded_file is None:
        return None
    try:
        uploaded_file.seek(0)
        return Image.open(io.BytesIO(uploaded_file.read())).convert("RGB")
    except Exception as exc:  # pragma: no cover - defensive
        raise ValueError(f"Unable to load image: {exc}") from exc


def image_bytes(image: Image.Image, fmt: str = "PNG") -> bytes:
    buf = io.BytesIO()
    image.save(buf, format=fmt)
    return buf.getvalue()


def dominant_color_analysis(image: Image.Image) -> Dict[str, Any]:
    """Lightweight color/dominance heuristics used in demo fallback mode."""
    small = image.convert("RGB").resize((60, 60))
    arr = np.array(small).reshape(-1, 3).astype(float)
    # Simple k-means-ish: sample dominant via quantized bins
    q = (arr // 32) * 32
    colors, counts = np.unique(q, axis=0, return_counts=True)
    order = np.argsort(-counts)[:5]
    palette = [
        {"color": tuple(int(c) for c in colors[i]), "pct": float(counts[i] / counts.sum())}
        for i in order
    ]
    # Average hue-ish proxy: mean R/G/B
    mean_rgb = arr.mean(axis=0)
    r, g, b = mean_rgb
    return {
        "mean_rgb": {"r": float(r), "g": float(g), "b": float(b)},
        "brightness": float((r + g + b) / 3),
        "dominant_palette": palette,
        "green_dominance": float(g) > max(r, b) + 12,
        "red_dominance": float(r) > max(g, b) + 12,
        "brown_dominance": float(r) > 90 and float(g) > 50 and float(b) < 60 and float(r) > float(g),
    }


def estimate_portion_from_image(image: Image.Image) -> str:
    w, h = image.size
    area = w * h
    if area < 150_000:
        return "Small (~1 serving)"
    if area < 500_000:
        return "Medium (~1-2 servings)"
    return "Large (~2+ servings)"


def score_to_badge(score: float) -> Tuple[str, str]:
    if score >= 80:
        return ("Excellent", "success")
    if score >= 60:
        return ("Good", "info")
    if score >= 40:
        return ("Fair", "warn")
    return ("Poor", "danger")


def freshness_to_pill(stage: str) -> str:
    key = stage.lower()
    return {
        "fresh": "fresh",
        "moderately fresh": "moderate",
        "spoiled": "spoiled",
    }.get(key, "moderate")


def safety_to_pill(advice: str) -> str:
    a = advice.lower()
    if "discard" in a:
        return "discard"
    if "24h" in a or "within 24" in a:
        return "caution"
    if "safe" in a:
        return "safe"
    return "caution"


def format_macros(macros: Dict[str, float]) -> str:
    parts = [
        f"Calories {macros.get('calories', 0):.0f} kcal",
        f"Protein {macros.get('protein', 0):.1f} g",
        f"Carbs {macros.get('carbs', 0):.1f} g",
        f"Fat {macros.get('fat', 0):.1f} g",
        f"Fiber {macros.get('fiber', 0):.1f} g",
    ]
    return "  |  ".join(parts)


def parse_json_safe(text: str, fallback: Any = None) -> Any:
    """Extract JSON object from model output safely."""
    if fallback is None:
        fallback = {}
    try:
        return json.loads(text)
    except Exception:
        pass
    # Try to find a JSON block
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            return fallback
    return fallback


def now_iso() -> str:
    return datetime.utcnow().isoformat() + "Z"


def esc(value: Any) -> str:
    """HTML-escape any value so model output can be embedded safely."""
    return html.escape(str(value if value is not None else ""), quote=True)


def upload_fingerprint(uploaded_file) -> str:
    """Stable hash of an uploaded file so stale results can be invalidated."""
    if uploaded_file is None:
        return ""
    try:
        uploaded_file.seek(0)
        data = uploaded_file.read()
        uploaded_file.seek(0)
    except Exception:
        return ""
    return hashlib.sha256(data).hexdigest()[:16]


def text_fingerprint(*parts: Any) -> str:
    """Stable hash of arbitrary inputs used as a cache key."""
    payload = "|".join("" if p is None else str(p) for p in parts)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]


DEFAULT_NUTRITION_DB: Dict[str, Dict[str, float]] = {
    "grilled chicken breast": {"calories": 165, "protein": 31, "carbs": 0, "fat": 3.6, "fiber": 0},
    "salmon fillet": {"calories": 206, "protein": 22, "carbs": 0, "fat": 13, "fiber": 0},
    "margherita pizza": {"calories": 250, "protein": 11, "carbs": 26, "fat": 10, "fiber": 2},
    "caesar salad": {"calories": 190, "protein": 6, "carbs": 14, "fat": 13, "fiber": 3},
    "beef burger": {"calories": 540, "protein": 28, "carbs": 45, "fat": 30, "fiber": 3},
    "sushi roll": {"calories": 300, "protein": 10, "carbs": 42, "fat": 7, "fiber": 3},
    "chicken curry": {"calories": 320, "protein": 24, "carbs": 18, "fat": 16, "fiber": 4},
    "tacos": {"calories": 350, "protein": 18, "carbs": 35, "fat": 14, "fiber": 5},
    "pasta carbonara": {"calories": 570, "protein": 24, "carbs": 58, "fat": 26, "fiber": 4},
    "fruit salad": {"calories": 80, "protein": 1, "carbs": 20, "fat": 0.5, "fiber": 3},
    "avocado toast": {"calories": 250, "protein": 6, "carbs": 28, "fat": 14, "fiber": 8},
    "oatmeal bowl": {"calories": 150, "protein": 5, "carbs": 27, "fat": 3, "fiber": 4},
}


def fallback_nutrition(dish_name: str) -> Dict[str, float]:
    key = dish_name.strip().lower()
    for known, macros in DEFAULT_NUTRITION_DB.items():
        if known in key or key in known:
            return dict(macros)
    # Generic balanced estimate
    return {"calories": 350, "protein": 15, "carbs": 45, "fat": 12, "fiber": 4}


def compute_health_score(macros: Dict[str, float], dish_name: str = "") -> int:
    """Composite health score 0-100 based on macros (demo heuristic)."""
    protein = macros.get("protein", 0)
    fiber = macros.get("fiber", 0)
    fat = macros.get("fat", 0)
    carbs = macros.get("carbs", 0)
    calories = macros.get("calories", 0)

    score = 50
    # Protein reward (up to +20)
    score += min(20, protein * 2)
    # Fiber reward (up to +15)
    score += min(15, fiber * 3)
    # Moderate fat penalty if very high relative to calories
    fat_cal = fat * 9
    if calories > 0 and fat_cal / calories > 0.4:
        score -= 15
    # Calorie sanity
    if calories > 800:
        score -= 10
    elif calories < 150:
        score -= 5
    # Carb balance
    if carbs > 80:
        score -= 5
    return max(0, min(100, int(score)))


ALLERGEN_HINTS: Dict[str, List[str]] = {
    "pizza": ["Wheat", "Milk"],
    "burger": ["Wheat", "Sesame", "Eggs"],
    "caesar": ["Milk", "Eggs", "Fish"],
    "sushi": ["Fish", "Shellfish", "Sesame", "Soy"],
    "curry": ["Peanuts", "Tree Nuts", "Milk"],
    "tacos": ["Wheat", "Milk"],
    "carbonara": ["Wheat", "Milk", "Eggs"],
    "avocado toast": ["Wheat", "Sesame"],
    "oatmeal": ["Gluten"],
}


def detect_allergens(dish_name: str, ingredients: List[str]) -> List[str]:
    found = set()
    text = (dish_name + " " + " ".join(ingredients)).lower()
    for key, allergens in ALLERGEN_HINTS.items():
        if key in text:
            found.update(allergens)
    # Ingredient-level hints
    for ing in ingredients:
        ing_l = ing.lower()
        if any(x in ing_l for x in ["peanut", "nut", "almond", "walnut"]):
            found.update(["Peanuts", "Tree Nuts"])
        if any(x in ing_l for x in ["milk", "cheese", "butter", "cream", "yogurt"]):
            found.add("Milk")
        if "egg" in ing_l:
            found.add("Eggs")
        if "wheat" in ing_l or "flour" in ing_l:
            found.add("Wheat")
        if "soy" in ing_l:
            found.add("Soy")
        if "fish" in ing_l:
            found.add("Fish")
        if any(x in ing_l for x in ["shrimp", "crab", "lobster", "shellfish"]):
            found.add("Shellfish")
    return sorted(found)
