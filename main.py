"""Food Verse AI - FastAPI + uvicorn wrapper.

Streamlit remains the primary UI (run: streamlit run app.py).
This FastAPI app exposes a small health/metadata API and can be served with uvicorn
for sidecar/API deployments alongside the Streamlit frontend.
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from config import (
    APP_TITLE, APP_SUBTITLE, APP_VERSION, PLATFORM_ID, CATEGORY, TABS,
)

app = FastAPI(title=APP_TITLE, version=APP_VERSION)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {
        "app": APP_TITLE,
        "subtitle": APP_SUBTITLE,
        "version": APP_VERSION,
        "platform_id": PLATFORM_ID,
        "category": CATEGORY,
        "tabs": TABS,
        "ui": "Streamlit (streamlit run app.py)",
        "api": "uvicorn main:app",
    }


@app.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "app": APP_TITLE, "version": APP_VERSION}


@app.get("/tabs", tags=["meta"])
def list_tabs() -> dict:
    return {"tabs": TABS}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
