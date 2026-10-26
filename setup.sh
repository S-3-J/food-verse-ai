#!/usr/bin/env bash
# Food Verse AI - One-command setup
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$PROJECT_DIR/.venv"

echo "==> Food Verse AI setup"
echo "Project dir: $PROJECT_DIR"

if [ ! -d "$VENV_DIR" ]; then
  echo "==> Creating virtual environment..."
  python3 -m venv "$VENV_DIR"
fi

echo "==> Installing dependencies..."
"$VENV_DIR/bin/pip install --upgrade pip"
"$VENV_DIR/bin/pip install -r "$PROJECT_DIR/requirements.txt""

echo "==> Setup complete."
echo ""
echo "Run the Streamlit app:"
echo "  $VENV_DIR/bin/streamlit run $PROJECT_DIR/app.py"
echo ""
echo "Or run the FastAPI/uvicorn API:"
echo "  $VENV_DIR/bin/uvicorn main:app --reload --port 8000   (from $PROJECT_DIR)"
echo ""
echo "Optional: set API keys"
echo "  export GOOGLE_API_KEY=your_gemini_key"
echo "  export GROQ_API_KEY=your_groq_key"
