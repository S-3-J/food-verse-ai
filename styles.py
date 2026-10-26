"""Food Verse AI - Modern vibrant CSS styling."""
from __future__ import annotations

CSS = """
<style>
:root{
  --fv-primary:#06b6d4;
  --fv-primary-dark:#0891b2;
  --fv-secondary:#10b981;
  --fv-accent:#f59e0b;
  --fv-danger:#ef4444;
  --fv-warning:#f97316;
  --fv-bg:#0f172a;
  --fv-card:#1e293b;
  --fv-card-hover:#334155;
  --fv-text:#f1f5f9;
  --fv-muted:#94a3b8;
  --fv-border:#334155;
  --fv-shadow:0 10px 30px -10px rgba(2,6,23,0.6);
  --radius:14px;
}

html, body, [data-testid="stAppViewContainer"]{
  background: radial-gradient(1200px 800px at 20% -10%, #1e3a8a 0%, #0f172a 55%, #020617 100%) !important;
  color: var(--fv-text) !important;
  font-family: 'Inter', system-ui, -apple-system, Segoe UI, Roboto, sans-serif;
}

[data-testid="stHeader"]{background: transparent !important;}
[data-testid="stToolbar"]{visibility: hidden;}
#MainMenu{visibility: hidden;}
footer{visibility: hidden;}

h1, h2, h3, h4, h5, h6{color: var(--fv-text) !important; letter-spacing:-0.02em;}

.fv-app-title{
  background: linear-gradient(135deg,#22d3ee,#10b981);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 2.25rem;
  font-weight: 800;
  margin: 0;
}
.fv-subtitle{
  color: var(--fv-muted);
  font-size: 1.05rem;
  margin: 0.25rem 0 1rem 0;
}
.fv-badge{
  display:inline-block;
  padding:0.2rem 0.75rem;
  border-radius:999px;
  font-size:0.8rem;
  font-weight:700;
  color:#fff;
  background:var(--fv-primary);
  margin-right:0.5rem;
}

/* Cards */
.fv-card{
  background:var(--fv-card);
  border:1px solid var(--fv-border);
  border-radius:var(--radius);
  padding:1.25rem 1.5rem;
  margin:1rem 0;
  box-shadow:var(--fv-shadow);
  transition: transform .2s ease, border-color .2s ease;
}
.fv-card:hover{border-color:var(--fv-primary);transform:translateY(-2px);}

/* Metric strip */
.fv-metric-row{display:flex; gap:0.75rem; flex-wrap:wrap; margin:1rem 0;}
.fv-metric{
  flex:1; min-width:110px;
  background:var(--fv-card); border:1px solid var(--fv-border);
  border-radius:12px; padding:0.9rem 1rem; text-align:center;
}
.fv-metric .val{font-size:1.5rem; font-weight:800; color:var(--fv-primary); display:block;}
.fv-metric .lab{font-size:0.75rem; color:var(--fv-muted); text-transform:uppercase; letter-spacing:0.05em; margin-top:0.25rem;}

/* Badges / pills */
.fv-pill{display:inline-block;padding:0.35rem 0.9rem;border-radius:999px;font-weight:700;font-size:0.85rem;color:#fff;margin:0.25rem 0.4rem 0.25rem 0;}
.fv-pill.fresh{background:var(--fv-secondary);}
.fv-pill.moderate{background:var(--fv-accent);}
.fv-pill.spoiled{background:var(--fv-danger);}
.fv-pill.safe{background:var(--fv-secondary);}
.fv-pill.caution{background:var(--fv-warning);color:#000;}
.fv-pill.discard{background:var(--fv-danger);}

/* Tabs override */
[data-baseui="tab"], button[data-baseweb="tab"]{
  color:var(--fv-muted) !important;
}
button[data-baseweb="tab"][aria-selected="true"]{
  color:var(--fv-primary) !important;
  border-bottom:2px solid var(--fv-primary) !important;
}

/* Buttons */
.stButton>button{
  background:linear-gradient(135deg,var(--fv-primary),var(--fv-primary-dark)) !important;
  color:#fff !important; border:none !important; border-radius:10px !important;
  font-weight:700 !important; padding:0.6rem 1.4rem !important;
  width:100%;
}
.stButton>button:hover{filter:brightness(1.1);}

/* Sidebar navigation buttons */
section[data-testid="stSidebar"] .stButton>button{
  justify-content:flex-start !important;
  text-align:left !important;
  background:var(--fv-card) !important;
  color:var(--fv-muted) !important;
  border:1px solid var(--fv-border) !important;
  border-radius:10px !important;
  margin:0.35rem 0 !important;
  padding:0.75rem 1rem !important;
  font-weight:600 !important;
  font-size:0.95rem !important;
  transition: all 0.2s ease !important;
}
section[data-testid="stSidebar"] .stButton>button:hover{
  background:var(--fv-card-hover) !important;
  color:var(--fv-text) !important;
  border-color:var(--fv-primary) !important;
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"]{
  background:linear-gradient(135deg,var(--fv-primary),var(--fv-primary-dark)) !important;
  color:#fff !important;
  border-color:var(--fv-primary) !important;
  box-shadow:0 4px 12px -2px rgba(6,182,212,0.4) !important;
}

/* Top navigation bar (dark, horizontal, hover-expanding) */
.fv-topnav{
  display:flex;
  align-items:center;
  gap:0.35rem;
  background:var(--fv-bg);
  border:1px solid var(--fv-border);
  border-radius:var(--radius);
  padding:0.4rem 0.75rem;
  margin:0.5rem 0 1rem 0;
  box-shadow:var(--fv-shadow);
}
.fv-nav-item{
  display:flex;
  align-items:center;
  gap:0.4rem;
  padding:0.5rem 0.7rem;
  border-radius:8px;
  color:var(--fv-muted);
  text-decoration:none;
  font-weight:600;
  font-size:0.85rem;
  transition: all 0.2s ease;
  white-space: nowrap;
  border:1px solid transparent;
}
.fv-nav-item:hover{
  background:var(--fv-card);
  color:var(--fv-text);
  border-color:var(--fv-primary);
}
.fv-nav-item:hover .fv-nav-full{
  display:inline;
}
.fv-nav-item.active{
  background:var(--fv-primary);
  color:var(--fv-bg);
  border-color:var(--fv-primary);
}
.fv-nav-item.active .fv-nav-full{
  display:inline;
}
.fv-nav-marker{
  font-size:1.1rem;
  line-height:1;
}
.fv-nav-short{
  display:inline;
  font-weight:700;
}
.fv-nav-full{
  display:none;
  margin-left:0.2rem;
  font-weight:500;
}

/* Hide sidebar entirely (using top nav instead) */
[data-testid="stSidebar"]{display:none !important;}
[data-testid="stSidebarCollapsedControl"]{display:none !important;}

/* File uploader */
[data-testid="stFileUploader"] section{border:2px dashed var(--fv-border) !important; border-radius:var(--radius) !important; background:var(--fv-card) !important;}

/* Sidebar */
[data-testid="stSidebar"]{background:var(--fv-card) !important; border-right:1px solid var(--fv-border) !important;}
[data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3{color:var(--fv-text) !important;}

/* Alerts */
.fv-alert{padding:1rem 1.25rem;border-radius:10px;margin:1rem 0;color:#fff;font-weight:600;}
.fv-alert.info{background:rgba(6,182,212,0.15);border-left:4px solid var(--fv-primary);}
.fv-alert.warn{background:rgba(249,115,22,0.15);border-left:4px solid var(--fv-warning);}
.fv-alert.danger{background:rgba(239,68,68,0.15);border-left:4px solid var(--fv-danger);}
.fv-alert.success{background:rgba(16,185,129,0.15);border-left:4px solid var(--fv-secondary);}

/* Health score gauge text */
.fv-score-badge{font-size:2.5rem;font-weight:900;color:var(--fv-primary);}
.fv-score-label{color:var(--fv-muted);font-size:0.9rem;}

/* Violation log */
.violation{background:#1e1b4b;border-left:4px solid var(--fv-danger);padding:0.75rem 1rem;border-radius:0 8px 8px 0;margin:0.5rem 0;color:#e2e8f0;}
.violation .v-title{font-weight:700;color:var(--fv-danger);}

/* Responsive */
@media (max-width:640px){.fv-metric-row{flex-direction:column;}}
</style>
"""
