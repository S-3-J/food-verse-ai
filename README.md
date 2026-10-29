# Food Verse AI

**Multimodal Food Intelligence Agent** — a Streamlit application that recognizes dishes from photos, judges
freshness and spoilage, audits kitchen hygiene, generates recipes from your pantry, and builds a personalized
meal plan with an aisle-grouped grocery list.

> All outputs are **estimates**. Verify nutrition, freshness and hygiene results before using them in
> clinical, regulatory or other safety-critical decisions.

---

## Table of Contents

- [Highlights](#highlights)
- [The Five Workflows](#the-five-workflows)
- [Screens](#screens)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Token & Secret Management on Streamlit Community Cloud](#token--secret-management-on-streamlit-community-cloud)
- [Demo Mode vs Live Mode](#demo-mode-vs-live-mode)
- [Project Structure](#project-structure)
- [Architecture](#architecture)
- [Assistant Personas](#assistant-personas)
- [Design System](#design-system)
- [Testing](#testing)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Limitations & Disclaimer](#limitations--disclaimer)

---

## Highlights

- **Runs with zero configuration** — demo/heuristic mode produces full, meaningful results without any API key.
- **Two AI providers** — Gemini (Google) and Groq, switchable at runtime without a restart.
- **Vision + text reasoning** — photo analysis for food and kitchen hygiene, text-only workflows for recipes
  and meal planning.
- **Result caching by fingerprint** — results are re-used across reruns and invalidated automatically when the
  upload or the configuration changes.
- **Export everything** — every workflow offers a plain-text download and a one-click copy button.
- **Shareable deep links** — `?tab=tab3` opens a workflow directly.
- **Safe HTML rendering** — all model- and user-supplied text is escaped before being injected into the UI.

## The Five Workflows

| # | Workflow | Assistant | Input | Key outputs |
|---|----------|-----------|-------|-------------|
| 1 | **Food Recognition & Nutrition Audit** | Nutritionist Nova | Dish photo | Dish/cuisine/portion, macro strip, health score + meter, calorie-contribution bars, calorie gauge, allergen alert |
| 2 | **Food Freshness & Spoilage Diagnostic** | Safety Inspector Rex | Perishable photo + purchase date + storage method | Freshness stage, freshness index + meter, safety verdict, indicator table, shelf life, storage tips |
| 3 | **Kitchen Hygiene & Safety Compliance** | Safety Inspector Rex | Kitchen photo | Compliance score + pill + meter, indicator table, violations ranked by severity, corrective recommendations |
| 4 | **Smart Kitchen Recipe Assistant** | Chef Verse | Pantry chips + cook mode | Title, time/difficulty/servings strip, ingredients used, suggested additions, numbered steps, substitutions table, chef tips, nutrition estimate |
| 5 | **Personalized Meal Planner** | Nutritionist Nova | Age, gender, weight, height, activity, diet, goal | BMR / TDEE / target strip, 7-day meal matrix, aisle-grouped grocery list, adherence notes |

Every workflow ends with **Download** and **Copy** actions for a plain-text summary of the result.

## Screens

| Overview | Nutrition Audit | Kitchen Hygiene |
|---|---|---|
| Hero, capability cards, provider status | Macros, health score, calorie bars, allergens | Compliance meter, violations, recommendations |

| Freshness | Recipe Assistant | Meal Planner |
|---|---|---|
| Stage, safety verdict, storage tips | Ingredients, steps, substitutions | 7-day plan, grocery aisles, targets |

## Quick Start

Requires **Python 3.10+**.

### Option A — one-command setup

```bash
cd FoodVerseAI
./setup.sh
.venv/bin/streamlit run app.py
```

The app is served at <http://localhost:8501> by default.

### Option B — manual

```bash
cd FoodVerseAI
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

### Optional: metadata/health API

```bash
uvicorn main:app --reload --port 8000
```

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | App metadata, version, platform id, workflow list |
| GET | `/health` | Liveness probe |
| GET | `/tabs` | Workflow id → title map |

## Configuration

Copy the example file and fill in what you need:

```bash
cp .env.example .env
```

| Variable | Purpose | Default |
|----------|---------|---------|
| `FOOD_VERSE_PROVIDER` | `Gemini (Google)`, `Groq` or `Demo / Fallback Mode` | `Demo / Fallback Mode` |
| `GOOGLE_API_KEY` | Gemini API key | — |
| `GROQ_API_KEY` | Groq API key | — |
| `GEMINI_MODEL` | Gemini model id (empty = heuristic results) | — |
| `GROQ_MODEL` | Groq model id (empty = heuristic results) | — |
| `TEMPERATURE` | Optional sampling temperature hint | `0.3` |

Environment variables are also read from the shell (`export GOOGLE_API_KEY=...`). A `.env` file in the project
root is loaded automatically at startup.

### Runtime configuration

Provider, temperature and fallback behaviour can also be changed **without a restart** via
**Response Config** in the sidebar. Applying the form rebuilds the AI client and reruns the app.

The **model always follows the selected provider** — it is read from the `GEMINI_MODEL` / `GROQ_MODEL`
secret and is shown read-only in the dialog; there is no free-text model field. Changing a model means
editing the matching secret (on Community Cloud this restarts the app). If a provider has no model
configured, or the model id is unreachable, the workflow falls back to heuristic results.

> The API key is **never** rendered in the browser. In the default deployment the key stays on the server
> and the dialog only reports that a server-managed key is active. See
> [Token & secret management](#token--secret-management-on-streamlit-community-cloud).

## Token & Secret Management on Streamlit Community Cloud

### Where the key lives

| | Platform secret (recommended) | Visitor-supplied key (BYOK) |
|---|---|---|
| Where it is stored | Streamlit's encrypted secret store, per **app** | The visitor's browser session only |
| Set by | You — *App settings → Advanced settings → Secrets* | The visitor, in the Response Config dialog |
| Lifetime | Until you delete it from the app settings | Until the visitor's session ends |
| Visible to the browser? | **No** | Only to the visitor who typed it |
| Shared between visitors? | Yes (all sessions use it) | No |
| Enabled by default | Yes | No (`ALLOW_USER_API_KEY=false`) |

**Answers to the two common questions:**

- *"If a user leaves, will the token be removed?"* — A **platform secret is not**: it is app-level and
  persists across sessions, reboots and redeploys until you delete it in the app's settings. A **key typed by
  a visitor is**: it lives only in that visitor's `st.session_state` and is discarded when their session ends.
- *"Can a visitor steal my key?"* — Not with the default configuration. The key is never written into any
  widget, HTML block or payload, `AppConfig.api_key` is excluded from `repr()` so it cannot leak through a
  traceback, and the Response Config dialog only reports that a server-managed key is active.

### Setting it up on Community Cloud

1. Push the project to GitHub (the repository must be accessible to your Streamlit account).
2. Deploy the app from Streamlit Community Cloud.
3. Open **App settings → Advanced settings → Secrets** and add:

   ```toml
   GOOGLE_API_KEY = "your-gemini-key"
   GEMINI_MODEL = "your-gemini-model-id"
   MAX_RUNS_PER_SESSION = "25"
   ```

   ```toml
   GROQ_API_KEY = "your-groq-key"
   GROQ_MODEL = "your-groq-model-id"
   ```

   `FOOD_VERSE_PROVIDER` is optional — leave it at `Demo / Fallback Mode` to start in demo mode and let
   visitors pick Gemini or Groq in **Response Config**. The model for each provider comes from its own
   secret, so a provider with no model id simply runs on heuristic results.

4. Save — the app restarts with the secret injected as an environment variable (also readable via
   `st.secrets`).

### Security flags

| Flag | Default | Effect |
|---|---|---|
| `ALLOW_USER_API_KEY` | `false` | `true` shows an optional "your API key" field. The key is kept in that session only and is never written to disk. |
| `MAX_RUNS_PER_SESSION` | `25` | Caps live-provider analyses per browser session (`0` = unlimited). The sidebar shows `Quota n/limit`; demo mode never consumes quota. |
| `FOOD_VERSE_PROVIDER` | `Demo / Fallback Mode` | Which provider the server key belongs to. |

### Hardening checklist

- Keep `.streamlit/secrets.toml` and `.env` out of git (both are in `.gitignore`).
- Restrict the provider key to the API only, set a spending/usage cap on the provider console, and rotate
  the key periodically.
- Prefer a cheap, fast model (set `GEMINI_MODEL` / `GROQ_MODEL` to a small, quick model id) — every visitor
  consumes your quota.
- Set `MAX_RUNS_PER_SESSION` so a single session cannot drain the quota.
- Delete the secret from the app settings to revoke access immediately (the app falls back to demo mode).
- Do not print `AppConfig` or `config.api_key` in logs, error messages or `st.write`.

## Demo Mode vs Live Mode

| | Demo / Fallback Mode | Live provider |
|---|---|---|
| Requirements | none | valid API key |
| Data source | visual heuristics + built-in nutrition database | Gemini / Groq model output |
| Vision | colour-dominance + portion heuristics | model vision analysis |
| Nutrition | `DEFAULT_NUTRITION_DB` lookup + composite health score | model-estimated macros |
| Freshness / hygiene | stage + indicator heuristics | model verdicts and violations |
| Recipes / plans | deterministic template recipes and rotating meal pools | model-generated JSON |
| Banner | "Demo / Fallback Mode active" | "provider is connected" |

If a live provider call fails, the workflow warns and falls back to demo heuristics rather than crashing.

## Project Structure

```
FoodVerseAI/
├── app.py                  # Streamlit shell: sidebar nav, routing, home, config dialog
├── config.py               # AppConfig, tab metadata, constants, env loading
├── ai_client.py            # Unified Gemini / Groq client with demo fallback
├── personas.py             # Assistant personas and system-prompt builder
├── styles.py               # Design system: CSS tokens, components, responsive rules
├── ui.py                   # Shared UI primitives (cards, metric strips, tables, chips…)
├── utils.py                # Image analysis, formatting, fingerprints, HTML escaping
├── main.py                 # FastAPI metadata/health sidecar
├── requirements.txt
├── setup.sh
├── .env.example
├── Dockerfile
├── .streamlit/config.toml  # Light theme, minimal toolbar, headless server defaults
├── .streamlit/secrets.toml  # Optional local secrets (git-ignored, never deploy it)
└── tabs/
    ├── tab1_food_recognition.py
    ├── tab2_freshness.py
    ├── tab3_kitchen_hygiene.py
    ├── tab4_recipe_assistant.py
    └── tab5_meal_planner.py
```

## Architecture

- **Single-page app, view-based routing.** `app.py` keeps the active view in `st.session_state["view"]` and
  mirrors it into the `?tab=` query parameter, so every workflow is linkable and refresh-safe.
- **Thin tab contract.** Each tab module exposes `render(config, ai_client) -> None` and owns its own inputs,
  prompt, parsing and presentation.
- **Provider abstraction.** `AIClient` hides SDK differences behind `generate_text()` and `generate_vision()`;
  `AppConfig.is_ai_enabled` decides between a real provider and the demo path.
- **Structured outputs.** Prompts request a strict JSON object; `utils.parse_json_safe` recovers JSON from
  noisy model output and falls back to a deterministic demo payload.
- **Fingerprint caching.** `utils.upload_fingerprint` (SHA-256 of the uploaded bytes) and
  `utils.text_fingerprint` (SHA-256 of the relevant inputs) key the cached result per workflow. Change the
  photo, the storage context, the pantry, the cook mode or the profile and the stale result is discarded.
- **Defensive UI boundary.** Workflow exceptions are caught in `app.py`, shown as a friendly error with the
  traceback collapsed in a "Technical details" expander.
- **Escaped rendering.** `utils.esc()` HTML-escapes any model or user text before it reaches
  `unsafe_allow_html`; the copy-button payload additionally escapes `<`, `>` and `&` in its JSON envelope.

## Assistant Personas

| Persona | Role | Used by |
|---------|------|---------|
| **Chef Verse** | Multimodal Food Intelligence Agent | Recipe Assistant |
| **Nutritionist Nova** | Clinical Nutrition & Diet Planning Specialist | Food Recognition, Meal Planner |
| **Safety Inspector Rex** | Food Safety & Kitchen Hygiene Compliance Officer | Freshness Check, Kitchen Hygiene |

System prompts are assembled by `personas.build_system_prompt(persona, task_context)`, which appends the
workflow-specific context and instructs the model to avoid fabricating measurements.

## Design System

`styles.py` defines the visual language as CSS custom properties (light theme, slate/ink neutrals, sky-blue
primary `#0ea5e9`, semantic success/warn/danger tones) plus component classes:

- Layout: `fv-hero`, `fv-page-title`, `fv-topbar`, `fv-footer`, `fv-section-title`
- Data: `fv-metric` (metric strips), `fv-bars` / `fv-bar-track` (HTML bar charts), `fv-table` (data tables),
  `fv-meter` / `fv-meter-fill` (score meters)
- Feedback: `fv-alert` (info / success / warn / danger), `fv-chip` / `fv-tag` (pills), `fv-empty` (empty states)
- Icons use the **Material Symbols Rounded** font shipped with Streamlit — the global font rule explicitly
  excludes Streamlit's icon elements so ligatures render as glyphs offline.

## Testing

The app has no automated test-suite checked in. During development it was exercised with:

- `streamlit.testing.v1.AppTest` harnesses that open each view, interact with inputs and assert zero
  exceptions (including the upload → result path).
- Headless-Chrome (CDP) screenshot and DOM evaluation scripts for visual verification and computed-style checks.

Smoke-test checklist after a change:

```bash
.venv/bin/python -m py_compile app.py config.py ai_client.py personas.py styles.py ui.py utils.py tabs/*.py
.venv/bin/streamlit run app.py          # then open each workflow and run it
```

## Deployment

### Streamlit Community Cloud / any PaaS

Point the platform at `app.py`, add the environment variables from [Configuration](#configuration), and use the
included `Dockerfile` if your platform builds from a container.

### Docker

```bash
docker build -t foodverse-ai .
docker run -p 8501:8501 --env-file .env foodverse-ai
```

The image runs the app headless on port 8501 and exposes it via uvicorn on port 8000.

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| "Demo / Fallback Mode is active" | Expected without a key — add one in **Response Config** or via `.env`. |
| Live provider call fails | Check the key, the provider's model id (`GEMINI_MODEL` / `GROQ_MODEL`) and network access; the workflow falls back to demo output with a warning. |
| Sidebar icons show as text | Do not override the font on `[data-testid="stIconMaterial"]`; `styles.py` already excludes it. |
| Upload not updating results | Results are fingerprinted — re-upload a different file or press the run button. |
| Port already in use | `streamlit run app.py --server.port 8502` |

## Limitations & Disclaimer

- Vision-based nutrition, freshness and hygiene assessment is approximate and depends on lighting, angle and
  camera quality.
- Demo-mode numbers are heuristics from a small built-in database, not measurements.
- The meal planner uses Mifflin-St Jeor for BMR and standard activity multipliers; it is not medical advice.
- Freshness and hygiene verdicts are decision-support only. Follow local food-safety guidance.

---

*Food Verse AI — Multimodal Food Intelligence Agent. Estimates only; verify before safety-critical use.*
