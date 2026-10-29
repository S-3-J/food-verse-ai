"""Food Verse AI - Token-based light design system."""
from __future__ import annotations

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root{
  --fv-primary:#0ea5e9;
  --fv-primary-strong:#0369a1;
  --fv-primary-soft:#e0f2fe;
  --fv-primary-border:#bae6fd;

  --fv-success:#059669;
  --fv-success-strong:#065f46;
  --fv-success-soft:#d1fae5;

  --fv-warning:#d97706;
  --fv-warning-strong:#92400e;
  --fv-warning-soft:#fef3c7;

  --fv-danger:#dc2626;
  --fv-danger-strong:#991b1b;
  --fv-danger-soft:#fee2e2;

  --fv-info:#0369a1;
  --fv-info-strong:#075985;
  --fv-info-soft:#e0f2fe;

  --fv-bg:#f6f8fb;
  --fv-surface:#ffffff;
  --fv-surface-2:#f1f5f9;
  --fv-surface-3:#e2e8f0;

  --fv-text:#0f172a;
  --fv-text-soft:#334155;
  --fv-text-muted:#64748b;

  --fv-border:#e2e8f0;
  --fv-border-strong:#cbd5e1;

  --fv-radius-sm:8px;
  --fv-radius:12px;
  --fv-radius-lg:16px;
  --fv-radius-pill:999px;

  --fv-shadow-sm:0 1px 2px rgba(15,23,42,0.06);
  --fv-shadow:0 6px 18px -8px rgba(15,23,42,0.16);
  --fv-shadow-lg:0 18px 40px -20px rgba(15,23,42,0.28);

  --fv-ease:cubic-bezier(0.4,0,0.2,1);
  --fv-font:'Inter',system-ui,-apple-system,'Segoe UI',Roboto,Helvetica,Arial,sans-serif;
}

html, body, [data-testid="stAppViewContainer"]{
  background:var(--fv-bg);
  color:var(--fv-text);
  font-family:var(--fv-font);
}
[data-testid="stAppViewContainer"] *:not([data-testid="stIconMaterial"]){
  font-family:var(--fv-font);
}
[data-testid="stIconMaterial"],
[data-testid="stIconMaterial"] *{
  font-family:'Material Symbols Rounded' !important;
  font-weight:normal !important;
  font-style:normal !important;
  line-height:1 !important;
  letter-spacing:normal !important;
  text-transform:none !important;
  white-space:nowrap !important;
  word-wrap:normal !important;
  direction:ltr !important;
  font-feature-settings:'liga' !important;
  -webkit-font-feature-settings:'liga' !important;
  -webkit-font-smoothing:antialiased;
}
[data-testid="stAppViewContainer"] .stMarkdown p{color:var(--fv-text-soft);}
[data-testid="stAppViewContainer"] .stMarkdown h1,
[data-testid="stAppViewContainer"] .stMarkdown h2,
[data-testid="stAppViewContainer"] .stMarkdown h3,
[data-testid="stAppViewContainer"] .stMarkdown h4{color:var(--fv-text);letter-spacing:-0.015em;}

#MainMenu, footer{visibility:hidden;}
[data-testid="stHeader"]{background:transparent;}

/* ---------- Buttons ---------- */
button[data-testid^="stBaseButton"]{
  border-radius:10px !important;
  font-weight:600 !important;
  font-size:0.9rem !important;
  box-shadow:var(--fv-shadow-sm) !important;
  transition:background 0.18s var(--fv-ease), border-color 0.18s var(--fv-ease),
             color 0.18s var(--fv-ease), transform 0.18s var(--fv-ease),
             box-shadow 0.18s var(--fv-ease) !important;
}
button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(135deg,var(--fv-primary),var(--fv-primary-strong)) !important;
  color:#ffffff !important;
  border:1px solid transparent !important;
  padding:0.5rem 1.05rem !important;
}
button[data-testid="stBaseButton-primary"]:hover{
  filter:brightness(1.06);
  transform:translateY(-1px);
  box-shadow:var(--fv-shadow) !important;
}
button[data-testid="stBaseButton-secondary"]{
  background:var(--fv-surface) !important;
  color:var(--fv-text-soft) !important;
  border:1px solid var(--fv-border-strong) !important;
  padding:0.5rem 1.05rem !important;
}
button[data-testid="stBaseButton-secondary"]:hover{
  background:var(--fv-primary-soft) !important;
  border-color:var(--fv-primary) !important;
  color:var(--fv-primary-strong) !important;
}
button[data-testid="stBaseButton-tertiary"]{
  background:transparent !important;
  color:var(--fv-primary-strong) !important;
  border:1px solid transparent !important;
}
button[data-testid^="stBaseButton"] p,
button[data-testid^="stBaseButton"] span,
button[data-testid^="stBaseButton"] div{color:inherit !important;}
button[data-testid^="stBaseButton"]:focus-visible{
  outline:2px solid var(--fv-primary) !important;
  outline-offset:2px !important;
}

/* ---------- Sidebar ---------- */
[data-testid="stSidebar"]{
  background:var(--fv-surface);
  border-right:1px solid var(--fv-border);
}
[data-testid="stSidebarUserContent"]{
  padding:1.35rem 1rem 2.5rem !important;
}
.fv-brand,.fv-model-card,.fv-card,.fv-metric,.fv-empty,.fv-hero,.fv-alert,.violation{box-sizing:border-box;}
[data-testid="stSidebar"] button[data-testid^="stBaseButton"]{
  width:100%;
  justify-content:flex-start;
  text-align:left;
  background:transparent !important;
  color:var(--fv-text-soft) !important;
  border:1px solid transparent !important;
  border-radius:var(--fv-radius-sm) !important;
  padding:0.5rem 0.7rem !important;
  font-size:0.9rem !important;
  box-shadow:none !important;
}
[data-testid="stSidebar"] button[data-testid^="stBaseButton"] > div{justify-content:flex-start !important;}
[data-testid="stSidebar"] button[data-testid^="stBaseButton"]:hover{
  background:var(--fv-surface-2) !important;
  color:var(--fv-text) !important;
}
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]{
  background:var(--fv-primary-soft) !important;
  color:var(--fv-primary-strong) !important;
  border-color:var(--fv-primary-border) !important;
  box-shadow:none !important;
}
[data-testid="stSidebar"] button[data-testid="stBaseButton-primary"]:hover{
  background:#cdeafd !important;
}

/* ---------- Brand ---------- */
.fv-brand{display:flex;align-items:center;gap:0.7rem;margin-bottom:1.1rem;}
.fv-brand-mark{
  width:40px;height:40px;flex:0 0 40px;border-radius:12px;
  background:linear-gradient(135deg,var(--fv-primary),var(--fv-success));
  display:flex;align-items:center;justify-content:center;font-size:1.25rem;
  box-shadow:var(--fv-shadow);
}
.fv-brand-name{font-size:1.05rem;font-weight:800;color:var(--fv-text);line-height:1.15;}
.fv-brand-sub{font-size:0.72rem;color:var(--fv-text-muted);letter-spacing:0.04em;text-transform:uppercase;}

.fv-nav-label{
  font-size:0.68rem;font-weight:700;letter-spacing:0.12em;text-transform:uppercase;
  color:var(--fv-text-muted);margin:1.1rem 0 0.45rem 0.2rem;
}
.fv-model-card{
  background:var(--fv-surface-2);border:1px solid var(--fv-border);border-radius:var(--fv-radius-sm);
  padding:0.7rem 0.8rem;margin-bottom:0.6rem;
}
.fv-model-card .m-label{font-size:0.68rem;text-transform:uppercase;letter-spacing:0.08em;color:var(--fv-text-muted);}
.fv-model-card .m-value{font-size:0.88rem;font-weight:700;color:var(--fv-text);margin-top:0.15rem;word-break:break-word;}
.fv-model-card .m-sub{font-size:0.75rem;color:var(--fv-text-muted);margin-top:0.1rem;word-break:break-word;}

/* ---------- Chips ---------- */
.fv-chip{
  display:inline-flex;align-items:center;gap:0.35rem;
  padding:0.28rem 0.7rem;border-radius:var(--fv-radius-pill);
  font-size:0.76rem;font-weight:700;letter-spacing:0.02em;
  border:1px solid transparent;white-space:nowrap;
}
.fv-chip.live{background:var(--fv-success-soft);color:var(--fv-success-strong);border-color:#a7f3d0;}
.fv-chip.demo{background:var(--fv-warning-soft);color:var(--fv-warning-strong);border-color:#fde68a;}
.fv-chip.info{background:var(--fv-info-soft);color:var(--fv-info-strong);border-color:var(--fv-primary-border);}
.fv-chip.neutral{background:var(--fv-surface-2);color:var(--fv-text-soft);border-color:var(--fv-border);}
.fv-chip.success{background:var(--fv-success-soft);color:var(--fv-success-strong);border-color:#a7f3d0;}
.fv-chip.danger{background:var(--fv-danger-soft);color:var(--fv-danger-strong);border-color:#fecaca;}

/* ---------- Quota ---------- */
.fv-quota{
  display:flex;align-items:center;justify-content:space-between;gap:0.5rem;
  margin:-0.35rem 0 0.6rem 0;
}
.fv-quota-note{font-size:0.72rem;color:var(--fv-text-muted);}

/* ---------- Hero ---------- */
.fv-hero{
  position:relative;overflow:hidden;border-radius:var(--fv-radius-lg);
  padding:2.1rem 2.25rem;margin-bottom:1.25rem;
  background:linear-gradient(135deg,#0284c7 0%,#0ea5e9 42%,#059669 100%);
  box-shadow:var(--fv-shadow-lg);
}
.fv-hero-eyebrow{
  display:inline-block;font-size:0.72rem;font-weight:700;letter-spacing:0.14em;text-transform:uppercase;
  color:#ffffff;background:rgba(255,255,255,0.16);border:1px solid rgba(255,255,255,0.28);
  padding:0.3rem 0.7rem;border-radius:var(--fv-radius-pill);margin-bottom:0.9rem;
}
.fv-hero-title{font-size:2.15rem;font-weight:800;color:#ffffff;line-height:1.1;margin:0 0 0.5rem 0;}
.fv-hero-sub{font-size:1rem;color:rgba(255,255,255,0.92);max-width:62ch;line-height:1.55;}
.fv-hero-chips{display:flex;flex-wrap:wrap;gap:0.5rem;margin-top:1.15rem;}
.fv-hero-chip{
  font-size:0.78rem;font-weight:600;color:#ffffff;
  background:rgba(255,255,255,0.14);border:1px solid rgba(255,255,255,0.26);
  padding:0.32rem 0.75rem;border-radius:var(--fv-radius-pill);
}

/* ---------- Page header ---------- */
.st-key-fv_page_head{
  background:var(--fv-surface);border:1px solid var(--fv-border);border-radius:var(--fv-radius);
  padding:1rem 1.15rem;box-shadow:var(--fv-shadow-sm);margin-bottom:1.1rem;
}
.fv-page-title{
  display:flex;align-items:center;gap:0.6rem;
  font-size:1.45rem;font-weight:800;color:var(--fv-text);line-height:1.2;
}
.fv-page-icon{font-size:1.35rem;}
.fv-page-sub{font-size:0.92rem;color:var(--fv-text-muted);margin-top:0.3rem;line-height:1.5;}

/* ---------- Topbar ---------- */
.st-key-fv_topbar{
  background:var(--fv-surface);border:1px solid var(--fv-border);border-radius:var(--fv-radius);
  padding:0.5rem 0.9rem;box-shadow:var(--fv-shadow-sm);margin-bottom:1rem;
}
.fv-breadcrumb{font-size:0.8rem;color:var(--fv-text-muted);font-weight:600;}
.fv-breadcrumb .cur{color:var(--fv-text);}

/* ---------- Section titles ---------- */
.fv-section-title{
  display:flex;align-items:center;gap:0.5rem;
  font-size:1.05rem;font-weight:700;color:var(--fv-text);margin:0.2rem 0 0.6rem 0;
}

/* ---------- Cards ---------- */
.fv-card{
  background:var(--fv-surface);border:1px solid var(--fv-border);border-radius:var(--fv-radius);
  padding:1rem 1.15rem;box-shadow:var(--fv-shadow-sm);
}
.fv-card-title{font-weight:700;color:var(--fv-text);font-size:0.95rem;margin-bottom:0.35rem;}
.fv-card-body{color:var(--fv-text-soft);font-size:0.9rem;line-height:1.55;}
.fv-card-eyebrow{
  font-size:0.98rem;font-weight:700;color:var(--fv-text);display:flex;align-items:center;gap:0.45rem;
  margin-bottom:0.35rem;
}
.fv-card-kicker{font-size:0.72rem;font-weight:700;letter-spacing:0.08em;text-transform:uppercase;color:var(--fv-primary-strong);margin-bottom:0.3rem;}

/* ---------- Home capability grid ---------- */
.st-key-fv_home_cards [data-testid="stColumn"]:has(button){
  background:var(--fv-surface);border:1px solid var(--fv-border);border-radius:var(--fv-radius-lg);
  padding:1rem 1.05rem;box-shadow:var(--fv-shadow-sm);height:100%;
  transition:transform 0.2s var(--fv-ease), box-shadow 0.2s var(--fv-ease), border-color 0.2s var(--fv-ease);
}
.st-key-fv_home_cards [data-testid="stColumn"]:has(button):hover{
  transform:translateY(-3px);box-shadow:var(--fv-shadow);border-color:var(--fv-primary-border);
}
.st-key-fv_home_cards button[data-testid^="stBaseButton"]{
  background:var(--fv-primary-soft) !important;color:var(--fv-primary-strong) !important;
  border:1px solid var(--fv-primary-border) !important;width:100%;margin-top:0.55rem;
}
.st-key-fv_home_cards button[data-testid^="stBaseButton"]:hover{
  background:var(--fv-primary) !important;color:#ffffff !important;border-color:var(--fv-primary) !important;
}
.st-key-fv_home_steps [data-testid="stColumn"]{
  background:var(--fv-surface);border:1px solid var(--fv-border);border-radius:var(--fv-radius);
  padding:1rem 1.1rem;box-shadow:var(--fv-shadow-sm);box-sizing:border-box;
}
.st-key-fv_home_steps .step-num{
  width:26px;height:26px;border-radius:50%;background:var(--fv-primary-soft);color:var(--fv-primary-strong);
  display:flex;align-items:center;justify-content:center;font-weight:800;font-size:0.8rem;margin-bottom:0.55rem;
}

/* ---------- Metric strip ---------- */
.fv-metric{
  background:var(--fv-surface);border:1px solid var(--fv-border);border-radius:var(--fv-radius);
  padding:0.85rem 0.9rem;text-align:center;box-shadow:var(--fv-shadow-sm);
}
.fv-metric .val{display:block;font-size:1.5rem;font-weight:800;line-height:1.2;}
.fv-metric .lab{
  display:block;font-size:0.7rem;color:var(--fv-text-muted);text-transform:uppercase;
  letter-spacing:0.07em;margin-top:0.3rem;font-weight:600;
}

/* ---------- Pills ---------- */
.fv-pill{
  display:inline-block;padding:0.3rem 0.8rem;border-radius:var(--fv-radius-pill);
  font-weight:700;font-size:0.82rem;margin:0.2rem 0.35rem 0.2rem 0;border:1px solid transparent;
}
.fv-pill.fresh{background:var(--fv-success-soft);color:var(--fv-success-strong);border-color:#a7f3d0;}
.fv-pill.moderate{background:var(--fv-warning-soft);color:var(--fv-warning-strong);border-color:#fde68a;}
.fv-pill.spoiled{background:var(--fv-danger-soft);color:var(--fv-danger-strong);border-color:#fecaca;}
.fv-pill.safe{background:var(--fv-success-soft);color:var(--fv-success-strong);border-color:#a7f3d0;}
.fv-pill.caution{background:var(--fv-warning-soft);color:var(--fv-warning-strong);border-color:#fde68a;}
.fv-pill.discard{background:var(--fv-danger-soft);color:var(--fv-danger-strong);border-color:#fecaca;}

/* ---------- Alerts ---------- */
.fv-alert{
  padding:0.9rem 1.1rem;border-radius:var(--fv-radius);margin:0.9rem 0;
  font-weight:600;font-size:0.92rem;line-height:1.5;border:1px solid;
}
.fv-alert.info{background:var(--fv-info-soft);border-color:var(--fv-primary-border);color:var(--fv-info-strong);}
.fv-alert.warn{background:var(--fv-warning-soft);border-color:#fde68a;color:var(--fv-warning-strong);}
.fv-alert.danger{background:var(--fv-danger-soft);border-color:#fecaca;color:var(--fv-danger-strong);}
.fv-alert.success{background:var(--fv-success-soft);border-color:#a7f3d0;color:var(--fv-success-strong);}

/* ---------- Empty state ---------- */
.fv-empty{
  background:var(--fv-surface);border:1.5px dashed var(--fv-border-strong);border-radius:var(--fv-radius-lg);
  padding:2.4rem 1.5rem;text-align:center;
}
.fv-empty-icon{font-size:2.4rem;line-height:1;}
.fv-empty-title{font-size:1.05rem;font-weight:700;color:var(--fv-text);margin:0.6rem 0 0.35rem 0;}
.fv-empty-body{font-size:0.9rem;color:var(--fv-text-muted);max-width:56ch;margin:0 auto;line-height:1.55;}

/* ---------- Violation log ---------- */
.violation{
  background:var(--fv-danger-soft);border:1px solid #fecaca;border-left:4px solid var(--fv-danger);
  padding:0.75rem 1rem;border-radius:0 var(--fv-radius-sm) var(--fv-radius-sm) 0;margin:0.5rem 0;
  color:var(--fv-text);
}
.violation .v-title{font-weight:800;color:var(--fv-danger-strong);}

/* ---------- Bars ---------- */
.fv-bars{display:flex;flex-direction:column;gap:0.6rem;}
.fv-bar-row{display:flex;align-items:center;gap:0.7rem;}
.fv-bar-label{
  flex:0 0 7.5rem;font-size:0.82rem;font-weight:600;color:var(--fv-text-soft);
  overflow:hidden;text-overflow:ellipsis;white-space:nowrap;
}
.fv-bar-track{
  flex:1 1 auto;height:10px;border-radius:var(--fv-radius-pill);
  background:var(--fv-surface-3);overflow:hidden;
}
.fv-bar-fill{display:block;height:100%;border-radius:var(--fv-radius-pill);transition:width 0.4s var(--fv-ease);}
.fv-bar-value{flex:0 0 3.5rem;text-align:right;font-size:0.82rem;font-weight:700;color:var(--fv-text);}

/* ---------- Table ---------- */
.fv-table-wrap{
  width:100%;overflow-x:auto;border:1px solid var(--fv-border);border-radius:var(--fv-radius);
  background:var(--fv-surface);box-shadow:var(--fv-shadow-sm);
}
.fv-table{width:100%;border-collapse:collapse;font-size:0.86rem;}
.fv-table th{
  text-align:left;padding:0.6rem 0.85rem;background:var(--fv-surface-2);
  color:var(--fv-text-muted);font-size:0.68rem;font-weight:700;
  letter-spacing:0.08em;text-transform:uppercase;white-space:nowrap;
  border-bottom:1px solid var(--fv-border);
}
.fv-table td{padding:0.62rem 0.85rem;border-bottom:1px solid var(--fv-border);color:var(--fv-text-soft);vertical-align:top;}
.fv-table tbody tr:last-child td{border-bottom:none;}
.fv-table tbody tr:hover{background:var(--fv-surface-2);}

/* ---------- Meter ---------- */
.fv-meter{display:block;width:100%;height:12px;border-radius:var(--fv-radius-pill);background:var(--fv-surface-3);overflow:hidden;}
.fv-meter-fill{display:block;height:100%;border-radius:var(--fv-radius-pill);transition:width 0.5s var(--fv-ease);}

/* ---------- Chips row ---------- */
.fv-chip-row{display:flex;flex-wrap:wrap;gap:0.4rem;margin:0.35rem 0 0.2rem 0;}
.fv-tag{
  display:inline-flex;align-items:center;gap:0.35rem;
  background:var(--fv-primary-soft);border:1px solid var(--fv-primary-border);color:var(--fv-primary-strong);
  border-radius:var(--fv-radius-pill);padding:0.25rem 0.7rem;font-size:0.78rem;font-weight:600;
}

/* ---------- Footer ---------- */
.fv-footer{
  text-align:center;color:var(--fv-text-muted);font-size:0.74rem;line-height:1.6;
  border-top:1px solid var(--fv-border);padding-top:0.9rem;margin-top:1.5rem;
}

/* ---------- Widgets ---------- */
[data-testid="stFileUploaderDropzone"]{
  background:var(--fv-surface-2) !important;border:1.5px dashed var(--fv-border-strong) !important;
  border-radius:var(--fv-radius) !important;padding:1.1rem !important;
  transition:border-color 0.18s var(--fv-ease), background 0.18s var(--fv-ease);
}
[data-testid="stFileUploaderDropzone"]:hover{
  border-color:var(--fv-primary) !important;background:var(--fv-primary-soft) !important;
}
[data-testid="stTextInput"] input, [data-testid="stNumberInput"] input,
[data-testid="stTextArea"] textarea{
  border-radius:var(--fv-radius-sm) !important;border:1px solid var(--fv-border-strong) !important;
  background:var(--fv-surface) !important;color:var(--fv-text) !important;
}
[data-testid="stTextInput"] input:focus, [data-testid="stNumberInput"] input:focus,
[data-testid="stTextArea"] textarea:focus{
  border-color:var(--fv-primary) !important;box-shadow:0 0 0 3px rgba(14,165,233,0.16) !important;
}
[data-baseweb="select"] > div{
  border-radius:var(--fv-radius-sm) !important;border-color:var(--fv-border-strong) !important;
}
[data-testid="stExpander"]{
  border:1px solid var(--fv-border);border-radius:var(--fv-radius);background:var(--fv-surface);
  box-shadow:var(--fv-shadow-sm);
}
hr{border-color:var(--fv-border);}

/* ---------- Motion ---------- */
@keyframes fv-fade-in{from{opacity:0;transform:translateY(8px);}to{opacity:1;transform:translateY(0);}}
.fv-fade-in{animation:fv-fade-in 0.4s var(--fv-ease);}
@media (prefers-reduced-motion: reduce){
  *, *::before, *::after{animation-duration:0.001ms !important;transition-duration:0.001ms !important;}
  button[data-testid^="stBaseButton"]:hover,
  .st-key-fv_home_cards [data-testid="stColumn"]:has(button):hover{transform:none !important;}
}

/* ---------- Responsive ---------- */
@media (max-width:900px){
  .fv-hero{padding:1.6rem 1.4rem;}
  .fv-hero-title{font-size:1.75rem;}
  .fv-page-title{font-size:1.25rem;}
}
</style>
"""
