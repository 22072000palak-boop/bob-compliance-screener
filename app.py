import streamlit as st
import pandas as pd
import io
from datetime import datetime
from sanctions_db import (
    SANCTIONED_COUNTRIES,
    RESTRICTED_ENTITIES,
    RESTRICTED_PART_KEYWORDS,
    get_flags,
)

# ─────────────────────────────────────────────
# Page config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="BOM Compliance & Sanctions Screener",
    page_icon="🔍",
    layout="wide",
)

# ─────────────────────────────────────────────
# Design system — full CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
/* ── Base ── */
[data-testid="stAppViewContainer"] { background: #f1f5f9; }
[data-testid="stMainBlockContainer"] { padding-top: 1.5rem; }
body, * { box-sizing: border-box; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,#0f172a 0%,#1e293b 100%);
    border-right: 1px solid #334155;
}
[data-testid="stSidebar"] * { color: #cbd5e1 !important; }
[data-testid="stSidebar"] h3 {
    color: #f8fafc !important;
    font-size: 1rem !important;
    letter-spacing: 0.03em;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid #334155;
    margin-bottom: 0.75rem;
}
[data-testid="stSidebar"] .stExpander {
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    background: #1e293b !important;
}

/* ── Hero ── */
.hero {
    background: linear-gradient(130deg,#0f172a 0%,#1d4ed8 55%,#7c3aed 100%);
    border-radius: 16px;
    padding: 2.2rem 2.5rem 2rem;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
    box-shadow: 0 8px 32px rgba(15,23,42,0.22);
}
.hero::before {
    content: "";
    position: absolute;
    top: -40px; right: -40px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: rgba(124,58,237,0.18);
}
.hero-title {
    font-size: 2rem; font-weight: 900;
    color: #fff; margin: 0 0 0.45rem;
    letter-spacing: -0.5px; line-height: 1.2;
}
.hero-sub {
    font-size: 0.95rem; color: #bfdbfe;
    margin: 0 0 1.5rem; line-height: 1.65;
    max-width: 680px;
}
.hero-steps {
    display: flex; gap: 0.6rem; flex-wrap: wrap;
    margin-top: 0.25rem;
}
.hero-step {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 99px;
    padding: 0.3rem 0.85rem;
    font-size: 0.78rem; font-weight: 600;
    color: #e0f2fe; white-space: nowrap;
}

/* ── Section header ── */
.section-hdr {
    display: flex; align-items: center; gap: 0.6rem;
    margin: 1.6rem 0 1rem;
}
.section-hdr-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem; flex-shrink: 0;
}
.section-hdr-text { font-size: 1rem; font-weight: 700; color: #0f172a; }
.section-hdr-sub  { font-size: 0.78rem; color: #64748b; margin-top: 1px; }
.icon-blue   { background:#dbeafe; }
.icon-green  { background:#dcfce7; }
.icon-red    { background:#fee2e2; }
.icon-purple { background:#ede9fe; }
.icon-amber  { background:#fef3c7; }
.icon-slate  { background:#f1f5f9; }

/* ── Metric cards ── */
.metrics-row { display:flex; gap:0.75rem; flex-wrap:wrap; margin-bottom:1rem; }
.mc {
    flex: 1 1 140px;
    border-radius: 14px;
    padding: 1.1rem 1rem;
    text-align: center;
    border: 1px solid transparent;
    box-shadow: 0 2px 10px rgba(0,0,0,0.06);
    transition: transform 0.15s, box-shadow 0.15s;
    min-width: 0;
}
.mc:hover { transform: translateY(-3px); box-shadow: 0 6px 18px rgba(0,0,0,0.1); }
.mc-blue   { background:linear-gradient(145deg,#dbeafe,#eff6ff); border-color:#93c5fd; }
.mc-green  { background:linear-gradient(145deg,#d1fae5,#ecfdf5); border-color:#6ee7b7; }
.mc-red    { background:linear-gradient(145deg,#fee2e2,#fef2f2); border-color:#fca5a5; }
.mc-rose   { background:linear-gradient(145deg,#ffe4e6,#fff1f2); border-color:#fda4af; }
.mc-amber  { background:linear-gradient(145deg,#fef3c7,#fffbeb); border-color:#fcd34d; }
.mc-val {
    font-size: 2.4rem; font-weight: 900;
    line-height: 1; margin-bottom: 0.3rem;
}
.mc-lbl {
    font-size: 0.7rem; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.08em;
    color: #475569;
}
.mc-desc {
    font-size: 0.75rem; color: #94a3b8;
    margin-top: 0.2rem; line-height: 1.3;
}

/* ── Progress bar ── */
.pbar-wrap {
    background: #e2e8f0; border-radius: 99px;
    height: 18px; overflow: hidden;
    box-shadow: inset 0 1px 3px rgba(0,0,0,0.08);
}
.pbar-fill {
    height: 100%; border-radius: 99px;
    transition: width 0.5s ease;
    position: relative;
}
.pbar-row {
    display:flex; align-items:center; gap:1rem;
    margin-bottom: 0.5rem;
}
.pbar-label { font-size:0.85rem; font-weight:700; color:#334155; white-space:nowrap; }
.pbar-pct   { font-size:1.15rem; font-weight:900; white-space:nowrap; }

/* ── Legend ── */
.legend {
    display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:0.75rem;
}
.legend-chip {
    display:inline-flex; align-items:center; gap:0.35rem;
    border-radius:99px; padding:0.2rem 0.75rem;
    font-size:0.75rem; font-weight:600; border:1px solid transparent;
}
.lc-clear    { background:#dcfce7; border-color:#86efac; color:#15803d; }
.lc-flagged  { background:#fee2e2; border-color:#fca5a5; color:#dc2626; }
.lc-critical { background:#fca5a5; border-color:#f87171; color:#7f1d1d; }
.lc-medium   { background:#fde68a; border-color:#fbbf24; color:#92400e; }
.lc-low      { background:#bbf7d0; border-color:#4ade80; color:#14532d; }
.lc-dot { width:8px; height:8px; border-radius:50%; }

/* ── Info / tip boxes ── */
.tip-box {
    border-radius: 10px;
    padding: 0.85rem 1.1rem;
    font-size: 0.875rem;
    line-height: 1.6;
    margin-bottom: 1rem;
    border: 1px solid transparent;
}
.tip-blue   { background:#eff6ff; border-color:#bfdbfe; color:#1e40af; }
.tip-green  { background:#f0fdf4; border-color:#bbf7d0; color:#15803d; }
.tip-amber  { background:#fffbeb; border-color:#fde68a; color:#92400e; }
.tip-red    { background:#fef2f2; border-color:#fecaca; color:#991b1b; }
.tip-title  { font-weight:700; font-size:0.82rem; text-transform:uppercase;
              letter-spacing:0.06em; margin-bottom:0.35rem; }

/* ── Upload zone ── */
.upload-zone {
    border: 2px dashed #93c5fd;
    border-radius: 12px;
    background: linear-gradient(135deg,#eff6ff,#f8fafc);
    padding: 1.5rem 2rem;
    text-align: center;
    margin-bottom: 1rem;
}
.upload-zone-title { font-size:1rem; font-weight:700; color:#1e3a5f; margin-bottom:0.3rem; }
.upload-zone-sub   { font-size:0.82rem; color:#64748b; }
.format-chip {
    display:inline-block;
    background:#dbeafe; color:#1d4ed8;
    border-radius:4px; padding:1px 8px;
    font-size:0.75rem; font-weight:700;
    margin:0 2px;
}

/* ── Column-map table ── */
.cmap-card {
    background:#fff; border:1px solid #e2e8f0;
    border-radius:12px; overflow:hidden;
    margin-bottom:1rem;
    box-shadow: 0 1px 6px rgba(0,0,0,0.04);
}
.cmap-hdr {
    background: linear-gradient(90deg,#1e3a5f,#1d4ed8);
    padding:0.65rem 1.1rem;
    display:flex; align-items:center; gap:0.5rem;
}
.cmap-hdr-title { font-size:0.85rem; font-weight:700; color:#fff; }
.cmap-hdr-sub   { font-size:0.72rem; color:#bfdbfe; margin-left:auto; }
.cmap-row {
    display:grid; grid-template-columns:1fr 1fr;
    padding:0.55rem 1.1rem;
    border-bottom:1px solid #f1f5f9;
    align-items:center;
}
.cmap-row:last-child { border-bottom:none; }
.cmap-field { font-size:0.82rem; font-weight:600; color:#334155; }
.cmap-val   { font-size:0.82rem; }
.cmap-chip  { border-radius:4px; padding:2px 8px; font-size:0.78rem; font-weight:600; display:inline-block; }
.cv-found-blue   { background:#dbeafe; color:#1d4ed8; }
.cv-found-green  { background:#dcfce7; color:#15803d; }
.cv-found-amber  { background:#fef3c7; color:#92400e; }
.cv-found-purple { background:#ede9fe; color:#6d28d9; }
.cv-auto    { background:#f1f5f9; color:#64748b; font-style:italic; }
.cv-missing { background:#fee2e2; color:#dc2626; }
.cmap-sample { font-size:0.72rem; color:#94a3b8; margin-left:0.4rem; }

/* ── Results table caption row ── */
.table-meta {
    font-size:0.78rem; color:#64748b;
    margin-top:0.4rem; margin-bottom:0.25rem;
}

/* ── Flag cards ── */
.flag-card {
    border-radius:10px; padding:0.9rem 1.1rem;
    margin-bottom:0.6rem; border:1px solid transparent;
    border-left-width: 5px;
}
.fc-critical {
    background:linear-gradient(90deg,#fef2f2 0%,#fff8f8 100%);
    border-color:#fca5a5; border-left-color:#dc2626;
    box-shadow:0 2px 8px rgba(220,38,38,0.09);
}
.fc-medium {
    background:linear-gradient(90deg,#fffbeb 0%,#fffdf5 100%);
    border-color:#fde68a; border-left-color:#d97706;
    box-shadow:0 2px 8px rgba(217,119,6,0.08);
}
.fc-low {
    background:linear-gradient(90deg,#f0fdf4 0%,#f7fef9 100%);
    border-color:#bbf7d0; border-left-color:#16a34a;
}
.fc-head {
    display:flex; align-items:center; gap:0.5rem;
    margin-bottom:0.35rem; flex-wrap:wrap;
}
.fc-badge {
    border-radius:5px; padding:2px 8px;
    font-size:0.7rem; font-weight:800;
    letter-spacing:0.06em; text-transform:uppercase;
}
.fcb-critical { background:#fca5a5; color:#7f1d1d; }
.fcb-medium   { background:#fde68a; color:#78350f; }
.fcb-low      { background:#bbf7d0; color:#14532d; }
.fc-partno { font-size:0.92rem; font-weight:800; color:#0f172a; }
.fc-name   { font-size:0.9rem; color:#334155; }
.fc-meta   {
    font-size:0.8rem; color:#475569;
    display:flex; flex-wrap:wrap; gap:0.75rem;
    margin-bottom:0.35rem;
}
.fc-meta-item { display:flex; align-items:center; gap:0.25rem; }
.fc-reasons { margin-top:0.3rem; }
.fc-reason-item {
    font-size:0.8rem; font-weight:600;
    padding:2px 0; display:flex; align-items:flex-start; gap:0.4rem;
}
.fcr-critical { color:#b91c1c; }
.fcr-medium   { color:#b45309; }
.fcr-low      { color:#15803d; }

/* ── Download card ── */
.dl-card {
    background:linear-gradient(135deg,#f8fafc,#eff6ff);
    border:1px solid #bfdbfe; border-radius:12px;
    padding:1.25rem 1.5rem; margin-bottom:0.75rem;
    box-shadow:0 2px 10px rgba(29,78,216,0.07);
}
.dl-title { font-size:1rem; font-weight:700; color:#1e3a5f; margin-bottom:0.4rem; }
.dl-stats { font-size:0.84rem; color:#475569; margin-bottom:0.9rem; line-height:1.7; }
.dl-stat-good { color:#15803d; font-weight:700; }
.dl-stat-bad  { color:#dc2626; font-weight:700; }

/* ── Sidebar stat block ── */
.sb-stat {
    background:rgba(255,255,255,0.07);
    border:1px solid rgba(255,255,255,0.1);
    border-radius:10px;
    padding:0.6rem 1rem 0.55rem;
    margin-bottom:0.5rem;
    display:flex; align-items:center; gap:0.75rem;
}
.sb-stat-num  { font-size:1.5rem; font-weight:900; line-height:1; }
.sb-stat-lbl  { font-size:0.72rem; font-weight:600; text-transform:uppercase;
                letter-spacing:0.07em; color:#94a3b8; }
.sb-n-red    { color:#f87171; }
.sb-n-orange { color:#fb923c; }
.sb-n-yellow { color:#fbbf24; }

/* ── Footer ── */
.footer {
    margin-top:2.5rem; padding-top:1rem;
    border-top:1px solid #e2e8f0;
    text-align:center; font-size:0.76rem; color:#94a3b8;
    line-height:1.8;
}
.footer a { color:#60a5fa; text-decoration:none; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Hero banner
# ─────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-title">🔍 BOM Compliance &amp; Sanctions Screener</div>
    <div class="hero-sub">
        Automatically cross-reference every component in your Bill of Materials against
        global trade sanctions, denied-party supplier lists, and export-control keywords.
        Instantly see what's safe and what needs attention.
    </div>
    <div class="hero-steps">
        <span class="hero-step">① Upload your BOM file</span>
        <span class="hero-step">② Auto-detect columns</span>
        <span class="hero-step">③ Screen against sanctions</span>
        <span class="hero-step">④ Review flagged items</span>
        <span class="hero-step">⑤ Download audit report</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# Sidebar — Sanctions Reference Panel
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📋 Sanctions Reference")

    st.markdown(
        f'<div class="sb-stat">'
        f'<div class="sb-stat-num sb-n-red">{len(SANCTIONED_COUNTRIES)}</div>'
        f'<div><div class="sb-stat-lbl">Sanctioned Countries</div>'
        f'<div style="font-size:0.7rem;color:#64748b;">OFAC / EU / UN embargoes</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    with st.expander("🔴 View sanctioned countries"):
        for c in sorted(SANCTIONED_COUNTRIES):
            st.markdown(
                f'<div style="padding:2px 0;font-size:0.82rem;">'
                f'<span style="color:#f87171;">●</span> <span style="color:#cbd5e1;">{c}</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<div class="sb-stat">'
        f'<div class="sb-stat-num sb-n-orange">{len(RESTRICTED_ENTITIES)}</div>'
        f'<div><div class="sb-stat-lbl">Restricted Entities</div>'
        f'<div style="font-size:0.7rem;color:#64748b;">Denied-party supplier list</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    with st.expander("🟠 View restricted entities"):
        for e in sorted(RESTRICTED_ENTITIES):
            st.markdown(
                f'<div style="padding:2px 0;font-size:0.82rem;">'
                f'<span style="color:#fb923c;">●</span> <span style="color:#cbd5e1;">{e}</span></div>',
                unsafe_allow_html=True,
            )

    st.markdown(
        f'<div class="sb-stat">'
        f'<div class="sb-stat-num sb-n-yellow">{len(RESTRICTED_PART_KEYWORDS)}</div>'
        f'<div><div class="sb-stat-lbl">Controlled Keywords</div>'
        f'<div style="font-size:0.7rem;color:#64748b;">EAR / ITAR dual-use terms</div></div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    with st.expander("🟡 View controlled keywords"):
        for k in sorted(RESTRICTED_PART_KEYWORDS):
            st.markdown(
                f'<div style="padding:2px 0;font-size:0.82rem;">'
                f'<span style="color:#fbbf24;">●</span> <span style="color:#cbd5e1;">{k}</span></div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # Colour legend in sidebar
    st.markdown(
        '<div style="font-size:0.78rem;font-weight:700;color:#94a3b8;'
        'text-transform:uppercase;letter-spacing:0.06em;margin-bottom:0.5rem;">'
        "Colour Legend</div>",
        unsafe_allow_html=True,
    )
    for label, dot_color, text in [
        ("#dc2626", "#fca5a5", "FLAGGED — action needed"),
        ("#16a34a", "#6ee7b7", "CLEAR — no issues found"),
        ("#dc2626", "#f87171", "Critical — sanctioned country / entity"),
        ("#d97706", "#fbbf24", "Medium — controlled keyword"),
        ("#16a34a", "#4ade80", "Low — minor flag only"),
    ]:
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:0.5rem;'
            f'margin-bottom:4px;font-size:0.75rem;color:#94a3b8;">'
            f'<span style="width:10px;height:10px;border-radius:50%;'
            f'background:{dot_color};flex-shrink:0;"></span>{text}</div>',
            unsafe_allow_html=True,
        )

    st.divider()
    st.markdown(
        '<div style="font-size:0.72rem;color:#475569;line-height:1.6;">'
        "⚠️ <b style='color:#93c5fd;'>Mock database</b> for demonstration only.<br>"
        "Always verify against official "
        "<b style='color:#93c5fd;'>OFAC</b>, "
        "<b style='color:#93c5fd;'>BIS</b>, and "
        "<b style='color:#93c5fd;'>EU</b> sanctions lists before making compliance decisions."
        "</div>",
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Column mapping helpers
# ─────────────────────────────────────────────
EXPECTED_COLUMNS = {
    "part_number": [
        "part_number", "part number", "partno", "part no", "pn", "part#",
        "index", "id", "sku", "product_id", "item_id",
    ],
    "component_name": [
        "component_name", "component name", "component", "description", "item", "name",
        "product", "product_name", "title", "sub_category", "category",
    ],
    "supplier_name": [
        "supplier_name", "supplier name", "supplier", "vendor", "manufacturer", "mfr",
        "brand",
    ],
    "country_of_origin": [
        "country_of_origin", "country of origin", "country", "origin", "coo",
    ],
}

_COUNTRY_BLACKLIST = {"sale_price", "market_price", "price", "rating", "type"}


def detect_columns(df: pd.DataFrame) -> dict:
    mapping = {}
    lower_cols = {c.lower().strip(): c for c in df.columns}

    for field, aliases in EXPECTED_COLUMNS.items():
        for alias in aliases:
            if alias in lower_cols:
                if field == "country_of_origin" and alias in _COUNTRY_BLACKLIST:
                    continue
                mapping[field] = lower_cols[alias]
                break
        if field in mapping:
            continue
        for alias in aliases:
            for col_lower, col_orig in lower_cols.items():
                if alias in col_lower or col_lower in alias:
                    if field == "country_of_origin" and col_lower in _COUNTRY_BLACKLIST:
                        continue
                    mapping[field] = col_orig
                    break
            if field in mapping:
                break

    if "part_number" not in mapping:
        mapping["part_number"] = "__AUTO_INDEX__"
    return mapping


def _render_mapping_card(col_map: dict, df: pd.DataFrame) -> None:
    """Render the detected column mapping as a clean card."""
    fields = [
        ("part_number",      "🔢 Part Number",        "cv-found-blue",   "Auto-generated row IDs will be used"),
        ("component_name",   "📦 Component / Product", "cv-found-green",  "Required — product or component name"),
        ("supplier_name",    "🏭 Supplier / Brand",    "cv-found-amber",  "Required — manufacturer or brand"),
        ("country_of_origin","🌍 Country of Origin",   "cv-found-purple", "Optional — country-based sanctions checks"),
    ]
    rows_html = ""
    for field, label, chip_class, hint in fields:
        detected = col_map.get(field, "")
        if detected == "__AUTO_INDEX__":
            val_html = '<span class="cmap-chip cv-auto">auto-generated (row index)</span>'
        elif detected and detected not in ("__country__",):
            sample = ""
            try:
                vals = df[detected].dropna()
                sample = str(vals.iloc[0])[:38] if len(vals) else ""
            except Exception:
                pass
            val_html = (
                f'<span class="cmap-chip {chip_class}">{detected}</span>'
                + (f'<span class="cmap-sample">e.g. &ldquo;{sample}&rdquo;</span>' if sample else "")
            )
        else:
            val_html = f'<span class="cmap-chip cv-missing">not detected</span><span class="cmap-sample"> — {hint}</span>'

        rows_html += (
            f'<div class="cmap-row">'
            f'<div class="cmap-field">{label}</div>'
            f'<div class="cmap-val">{val_html}</div>'
            f'</div>'
        )

    st.markdown(
        f'<div class="cmap-card">'
        f'<div class="cmap-hdr">'
        f'<span class="cmap-hdr-title">🗂️ Detected Column Mapping</span>'
        f'<span class="cmap-hdr-sub">Columns auto-matched from your file</span>'
        f'</div>'
        f'{rows_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


def apply_screening(df: pd.DataFrame, col_map: dict) -> pd.DataFrame:
    results = []
    for _, row in df.iterrows():
        part_number    = str(row.get(col_map.get("part_number", ""), "")).strip()
        component_name = str(row.get(col_map.get("component_name", ""), "")).strip()
        supplier_name  = str(row.get(col_map.get("supplier_name", ""), "")).strip()
        country        = str(row.get(col_map.get("country_of_origin", ""), "")).strip()

        flags, reasons = get_flags(part_number, component_name, supplier_name, country)

        results.append({
            "Part Number":       part_number,
            "Component Name":    component_name,
            "Supplier Name":     supplier_name,
            "Country of Origin": country,
            "Status":            "🔴 FLAGGED" if flags else "🟢 CLEAR",
            "Risk Level":        _risk_level(reasons),
            "Flags":             "; ".join(reasons) if reasons else "—",
        })
    return pd.DataFrame(results)


def _risk_level(reasons: list) -> str:
    if not reasons:
        return "Low"
    critical_keywords = ["sanctioned country", "denied party", "entity list"]
    for r in reasons:
        for kw in critical_keywords:
            if kw in r.lower():
                return "Critical"
    return "Medium"


def style_status(val):
    if "FLAGGED" in str(val):
        return "background-color:#fef2f2;color:#dc2626;font-weight:700;"
    if "CLEAR" in str(val):
        return "background-color:#f0fdf4;color:#16a34a;font-weight:700;"
    return ""


def style_risk(val):
    colors = {"Critical": "#991b1b", "Medium": "#92400e", "Low": "#14532d"}
    bg     = {"Critical": "#fecaca", "Medium": "#fde68a", "Low": "#bbf7d0"}
    return f"background-color:{bg.get(val,'')};color:{colors.get(val,'')};font-weight:700;"


# ─────────────────────────────────────────────
# Section: Upload
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-hdr">
  <div class="section-hdr-icon icon-blue">📂</div>
  <div>
    <div class="section-hdr-text">Upload Bill of Materials</div>
    <div class="section-hdr-sub">Supports CSV and Excel files — column names are auto-detected</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Supported formats + column hints
tip_col1, tip_col2 = st.columns(2)
with tip_col1:
    st.markdown("""
    <div class="tip-box tip-blue">
      <div class="tip-title">📄 Accepted File Formats</div>
      <span class="format-chip">CSV</span>
      <span class="format-chip">XLSX</span>
      <span class="format-chip">XLS</span>
      &nbsp; Any size, any column order.
    </div>
    """, unsafe_allow_html=True)
with tip_col2:
    st.markdown("""
    <div class="tip-box tip-amber">
      <div class="tip-title">📋 Recognised Column Names</div>
      Standard BOM: <b>Part Number · Component Name · Supplier Name · Country of Origin</b><br>
      BigBasket / retail: <b>product</b> → Component &nbsp;|&nbsp; <b>brand</b> → Supplier
    </div>
    """, unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "Drop your BOM file here or click to browse",
    type=["csv", "xlsx", "xls"],
)

use_demo = st.checkbox(
    "✨ Use built-in demo BOM instead (10 sample components — no file needed)",
    value=not bool(uploaded_file),
)

# ─────────────────────────────────────────────
# Load data
# ─────────────────────────────────────────────
if use_demo and not uploaded_file:
    demo_data = {
        "Part Number":       ["PN-001","PN-002","PN-003","PN-004","PN-005",
                              "PN-006","PN-007","PN-008","PN-009","PN-010"],
        "Component Name":    ["Resistor 10k","Encryption Module","Aluminum Heatsink",
                              "Radar Sensor Array","USB Controller","FPGA Chip",
                              "Optical Fiber Cable","Gyroscope IMU","Power Regulator",
                              "Military-Grade Capacitor"],
        "Supplier Name":     ["Acme Electronics","SinoTech Ltd","NordAluminium GmbH",
                              "TehranParts Co","USB Innovations","Pyongyang Micro",
                              "FiberLink Inc","Minsk Sensors","PowerPure Corp",
                              "DefenseParts LLC"],
        "Country of Origin": ["USA","China","Germany","Iran","Taiwan",
                              "North Korea","Japan","Belarus","South Korea","Russia"],
    }
    raw_df = pd.DataFrame(demo_data)
    col_map = {
        "part_number":      "Part Number",
        "component_name":   "Component Name",
        "supplier_name":    "Supplier Name",
        "country_of_origin":"Country of Origin",
    }
    data_source = "Demo BOM"
elif uploaded_file:
    try:
        raw_df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith(".csv") \
                 else pd.read_excel(uploaded_file)
        col_map = detect_columns(raw_df)
        data_source = uploaded_file.name
    except Exception as e:
        st.error(f"❌ Failed to read file: {e}")
        st.stop()
else:
    st.markdown("""
    <div class="tip-box tip-blue" style="text-align:center;padding:1.5rem;">
      <div style="font-size:1.5rem;margin-bottom:0.4rem;">⬆️</div>
      <div style="font-weight:700;color:#1e40af;margin-bottom:0.3rem;">Upload a file or enable the demo above to get started</div>
      <div style="color:#3b82f6;font-size:0.85rem;">Your BOM will be screened instantly once loaded.</div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────
# Section: Dataset Preview
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-hdr">
  <div class="section-hdr-icon icon-purple">🗂️</div>
  <div>
    <div class="section-hdr-text">Dataset Preview</div>
    <div class="section-hdr-sub">Review how your columns were mapped before screening runs</div>
  </div>
</div>
""", unsafe_allow_html=True)

_render_mapping_card(col_map, raw_df)

with st.expander(
    f"📋 Raw data — {len(raw_df):,} rows × {len(raw_df.columns)} columns  "
    f"(click to expand / collapse)",
    expanded=True,
):
    st.dataframe(raw_df.head(8), use_container_width=True, hide_index=True)
    st.markdown(
        f'<div class="table-meta">Showing first 8 of {len(raw_df):,} rows &nbsp;·&nbsp; '
        f'Source: <b>{data_source}</b></div>',
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
# Validate
# ─────────────────────────────────────────────
hard_missing = [
    f for f in ("component_name", "supplier_name")
    if f not in col_map or col_map[f] == "__AUTO_INDEX__"
]
if hard_missing:
    st.markdown(
        f'<div class="tip-box tip-red">'
        f'<div class="tip-title">⛔ Required Columns Not Found</div>'
        f'Could not detect: <b>{", ".join(hard_missing)}</b>.<br>'
        f'Please ensure your file has headers like <code>product</code>, <code>brand</code>, '
        f'<code>component</code>, or <code>supplier</code>.<br><br>'
        f'<b>All columns in your file:</b> {", ".join(raw_df.columns.tolist())}'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.stop()

soft_missing = [
    f for f in ("part_number", "country_of_origin")
    if f not in col_map or col_map[f] == "__AUTO_INDEX__"
]
if soft_missing:
    labels = {"part_number": "Part Number", "country_of_origin": "Country of Origin"}
    missing_labels = [labels[f] for f in soft_missing]
    st.markdown(
        f'<div class="tip-box tip-amber">'
        f'<div class="tip-title">ℹ️ Optional Columns Not Detected</div>'
        f'<b>{", ".join(missing_labels)}</b> — those checks will be skipped or auto-filled. '
        f'Screening will continue with the available columns.'
        f'</div>',
        unsafe_allow_html=True,
    )


# ─────────────────────────────────────────────
# Run screening
# ─────────────────────────────────────────────
with st.spinner("🔍 Screening all components against sanctions lists…"):
    screening_df = raw_df.copy()
    if col_map.get("part_number") == "__AUTO_INDEX__":
        screening_df["__part_id__"] = [f"ROW-{i+1:04d}" for i in range(len(screening_df))]
        col_map = {**col_map, "part_number": "__part_id__"}
    if "country_of_origin" not in col_map:
        screening_df["__country__"] = ""
        col_map = {**col_map, "country_of_origin": "__country__"}
    result_df = apply_screening(screening_df, col_map)

screened_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

total    = len(result_df)
flagged  = (result_df["Status"].str.contains("FLAGGED")).sum()
clear    = total - flagged
critical = (result_df["Risk Level"] == "Critical").sum()
medium   = (result_df["Risk Level"] == "Medium").sum()
low_risk = (result_df["Risk Level"] == "Low").sum() - clear  # flagged-but-low
pass_rate = (clear / total * 100) if total > 0 else 0


# ─────────────────────────────────────────────
# Section: Compliance Summary
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-hdr">
  <div class="section-hdr-icon icon-blue">📊</div>
  <div>
    <div class="section-hdr-text">Compliance Summary</div>
    <div class="section-hdr-sub">Overview of screening results across all components</div>
  </div>
</div>
""", unsafe_allow_html=True)

# 5 metric cards
st.markdown(
    f'<div class="metrics-row">'
    f'<div class="mc mc-blue">'
    f'  <div class="mc-val" style="color:#1d4ed8;">{total}</div>'
    f'  <div class="mc-lbl">📦 Total Components</div>'
    f'  <div class="mc-desc">All rows screened</div>'
    f'</div>'
    f'<div class="mc mc-green">'
    f'  <div class="mc-val" style="color:#15803d;">{clear}</div>'
    f'  <div class="mc-lbl">✅ Clear</div>'
    f'  <div class="mc-desc">No issues detected</div>'
    f'</div>'
    f'<div class="mc mc-red">'
    f'  <div class="mc-val" style="color:#dc2626;">{flagged}</div>'
    f'  <div class="mc-lbl">🚩 Flagged</div>'
    f'  <div class="mc-desc">Needs review</div>'
    f'</div>'
    f'<div class="mc mc-rose">'
    f'  <div class="mc-val" style="color:#be123c;">{critical}</div>'
    f'  <div class="mc-lbl">⛔ Critical Risk</div>'
    f'  <div class="mc-desc">Sanctioned country/entity</div>'
    f'</div>'
    f'<div class="mc mc-amber">'
    f'  <div class="mc-val" style="color:#b45309;">{medium}</div>'
    f'  <div class="mc-lbl">⚠️ Medium Risk</div>'
    f'  <div class="mc-desc">Controlled keyword match</div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

# Compliance pass-rate bar
if pass_rate >= 80:
    bar_color, lbl_color, verdict = "#16a34a", "#15803d", "✅ GOOD"
elif pass_rate >= 50:
    bar_color, lbl_color, verdict = "#f59e0b", "#b45309", "⚠️ MODERATE"
else:
    bar_color, lbl_color, verdict = "#dc2626", "#991b1b", "⛔ HIGH RISK"

st.markdown(
    f'<div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;'
    f'padding:1rem 1.25rem;margin-bottom:1rem;box-shadow:0 1px 4px rgba(0,0,0,0.05);">'
    f'<div class="pbar-row">'
    f'<span class="pbar-label">Compliance Pass Rate</span>'
    f'<span class="pbar-pct" style="color:{lbl_color};">{pass_rate:.1f}%</span>'
    f'<span style="background:{bar_color}22;color:{lbl_color};border-radius:6px;'
    f'padding:2px 10px;font-size:0.78rem;font-weight:700;">{verdict}</span>'
    f'</div>'
    f'<div class="pbar-wrap">'
    f'<div class="pbar-fill" style="width:{pass_rate:.1f}%;background:{bar_color};"></div>'
    f'</div>'
    f'<div style="font-size:0.72rem;color:#94a3b8;margin-top:0.4rem;">'
    f'{clear} of {total} components passed all checks &nbsp;·&nbsp; '
    f'{flagged} flagged for review &nbsp;·&nbsp; screened at {screened_at}'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True,
)

st.divider()

# ─────────────────────────────────────────────
# Section: Screening Results Table
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-hdr">
  <div class="section-hdr-icon icon-slate">🔎</div>
  <div>
    <div class="section-hdr-text">Screening Results</div>
    <div class="section-hdr-sub">Filter, search, and inspect every component's compliance status</div>
  </div>
</div>
""", unsafe_allow_html=True)

# Colour legend above table
st.markdown(
    '<div class="legend">'
    '<span class="legend-chip lc-clear"><span class="lc-dot" style="background:#16a34a;"></span>CLEAR — safe to use</span>'
    '<span class="legend-chip lc-flagged"><span class="lc-dot" style="background:#dc2626;"></span>FLAGGED — needs review</span>'
    '<span class="legend-chip lc-critical"><span class="lc-dot" style="background:#991b1b;"></span>Critical risk</span>'
    '<span class="legend-chip lc-medium"><span class="lc-dot" style="background:#b45309;"></span>Medium risk</span>'
    '<span class="legend-chip lc-low"><span class="lc-dot" style="background:#15803d;"></span>Low risk</span>'
    '</div>',
    unsafe_allow_html=True,
)

# Filter row
f1, f2, f3 = st.columns([2, 2, 3])
with f1:
    status_filter = st.selectbox("🔴🟢 Filter by Status", ["All", "🔴 FLAGGED", "🟢 CLEAR"])
with f2:
    risk_filter = st.selectbox("⚠️ Filter by Risk Level", ["All", "Critical", "Medium", "Low"])
with f3:
    search_term = st.text_input("🔍 Search", placeholder="Component name, supplier, or part number…")

display_df = result_df.copy()
if status_filter != "All":
    display_df = display_df[display_df["Status"] == status_filter]
if risk_filter != "All":
    display_df = display_df[display_df["Risk Level"] == risk_filter]
if search_term:
    mask = (
        display_df["Component Name"].str.contains(search_term, case=False, na=False)
        | display_df["Supplier Name"].str.contains(search_term, case=False, na=False)
        | display_df["Part Number"].str.contains(search_term, case=False, na=False)
    )
    display_df = display_df[mask]

styled = (
    display_df.style
    .map(style_status, subset=["Status"])
    .map(style_risk,   subset=["Risk Level"])
    .set_properties(**{"font-size": "0.86rem"})
)
st.dataframe(styled, use_container_width=True, hide_index=True)
st.markdown(
    f'<div class="table-meta">'
    f'Showing <b>{len(display_df)}</b> of <b>{total}</b> components &nbsp;·&nbsp; '
    f'Source: <b>{data_source}</b> &nbsp;·&nbsp; Screened: {screened_at}'
    f'</div>',
    unsafe_allow_html=True,
)

st.divider()

# ─────────────────────────────────────────────
# Section: Flagged Components — Detail View
# ─────────────────────────────────────────────
flagged_df = result_df[result_df["Status"].str.contains("FLAGGED")]
if not flagged_df.empty:
    st.markdown(f"""
    <div class="section-hdr">
      <div class="section-hdr-icon icon-red">🚩</div>
      <div>
        <div class="section-hdr-text">Flagged Components — Detail View</div>
        <div class="section-hdr-sub">{len(flagged_df)} component(s) require compliance review — sorted by risk level</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Sort: Critical → Medium → Low
    order = {"Critical": 0, "Medium": 1, "Low": 2}
    flagged_sorted = flagged_df.copy()
    flagged_sorted["_sort"] = flagged_sorted["Risk Level"].map(order)
    flagged_sorted = flagged_sorted.sort_values("_sort").drop(columns="_sort")

    for _, row in flagged_sorted.iterrows():
        risk      = row["Risk Level"]
        card_cls  = {"Critical": "fc-critical", "Medium": "fc-medium", "Low": "fc-low"}.get(risk, "fc-medium")
        badge_cls = {"Critical": "fcb-critical","Medium": "fcb-medium","Low": "fcb-low"}.get(risk, "fcb-medium")
        reason_cls= {"Critical": "fcr-critical","Medium": "fcr-medium","Low": "fcr-low"}.get(risk, "fcr-medium")
        reason_icon = {"Critical": "⛔", "Medium": "⚠️", "Low": "ℹ️"}.get(risk, "⚠️")

        reasons_html = "".join(
            f'<div class="fc-reason-item {reason_cls}">'
            f'<span>{reason_icon}</span><span>{r.strip()}</span></div>'
            for r in row["Flags"].split(";") if r.strip() and r.strip() != "—"
        )

        country_display = row["Country of Origin"] if row["Country of Origin"] else "Unknown"

        st.markdown(
            f'<div class="flag-card {card_cls}">'
            f'  <div class="fc-head">'
            f'    <span class="fc-badge {badge_cls}">{risk}</span>'
            f'    <span class="fc-partno">{row["Part Number"]}</span>'
            f'    <span style="color:#94a3b8;">—</span>'
            f'    <span class="fc-name">{row["Component Name"]}</span>'
            f'  </div>'
            f'  <div class="fc-meta">'
            f'    <span class="fc-meta-item">🏭 <b>{row["Supplier Name"]}</b></span>'
            f'    <span class="fc-meta-item">🌍 <b>{country_display}</b></span>'
            f'  </div>'
            f'  <div class="fc-reasons">{reasons_html}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

# ─────────────────────────────────────────────
# Section: Analytics Charts
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-hdr">
  <div class="section-hdr-icon icon-purple">📈</div>
  <div>
    <div class="section-hdr-text">Analytics</div>
    <div class="section-hdr-sub">Visual breakdown of compliance results</div>
  </div>
</div>
""", unsafe_allow_html=True)

ch1, ch2 = st.columns(2)
with ch1:
    st.markdown(
        '<div style="font-size:0.82rem;font-weight:700;color:#334155;'
        'margin-bottom:0.4rem;">🟢🔴 Compliance Status Breakdown</div>',
        unsafe_allow_html=True,
    )
    status_counts = (
        result_df["Status"]
        .value_counts()
        .rename(index=lambda x: x.replace("🔴 ", "").replace("🟢 ", ""))
    )
    st.bar_chart(status_counts, color=["#3b82f6"])

with ch2:
    st.markdown(
        '<div style="font-size:0.82rem;font-weight:700;color:#334155;'
        'margin-bottom:0.4rem;">⛔⚠️✅ Risk Level Distribution</div>',
        unsafe_allow_html=True,
    )
    risk_counts = result_df["Risk Level"].value_counts()
    st.bar_chart(risk_counts, color=["#8b5cf6"])

non_empty_countries = result_df["Country of Origin"].replace("", pd.NA).dropna()
if non_empty_countries.nunique() > 1:
    st.markdown(
        '<div style="font-size:0.82rem;font-weight:700;color:#334155;'
        'margin-bottom:0.4rem;">🌍 Components by Country of Origin</div>',
        unsafe_allow_html=True,
    )
    country_counts = (
        result_df[result_df["Country of Origin"] != ""]
        .groupby("Country of Origin")["Status"]
        .value_counts()
        .unstack(fill_value=0)
    )
    country_counts.columns = [c.replace("🔴 ", "").replace("🟢 ", "") for c in country_counts.columns]
    st.bar_chart(country_counts, use_container_width=True)

st.divider()

# ─────────────────────────────────────────────
# Section: Export
# ─────────────────────────────────────────────
st.markdown("""
<div class="section-hdr">
  <div class="section-hdr-icon icon-green">📥</div>
  <div>
    <div class="section-hdr-text">Audit Report &amp; Export</div>
    <div class="section-hdr-sub">Download a timestamped CSV audit report for your records</div>
  </div>
</div>
""", unsafe_allow_html=True)

audit_df = result_df.copy()
audit_df["Status"]      = audit_df["Status"].str.replace("🔴 ", "", regex=False).str.replace("🟢 ", "", regex=False)
audit_df["Screened At"] = screened_at
audit_df["Data Source"] = data_source

csv_buffer = io.StringIO()
audit_df.to_csv(csv_buffer, index=False)
csv_bytes  = csv_buffer.getvalue().encode("utf-8")

timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
filename = f"BOM_Compliance_Audit_{timestamp_str}.csv"

st.markdown(
    f'<div class="dl-card">'
    f'  <div class="dl-title">📄 Compliance Audit Report — Ready to Download</div>'
    f'  <div class="dl-stats">'
    f'    <b>{total}</b> components screened &nbsp;·&nbsp; '
    f'    <span class="dl-stat-bad">{flagged} flagged</span> &nbsp;·&nbsp; '
    f'    <span class="dl-stat-good">{clear} clear</span> &nbsp;·&nbsp; '
    f'    Screened at <b>{screened_at}</b><br>'
    f'    File: <code>{filename}</code>'
    f'  </div>',
    unsafe_allow_html=True,
)

dl1, dl2 = st.columns([2, 3])
with dl1:
    st.download_button(
        label="⬇️ Download Audit Report (CSV)",
        data=csv_bytes,
        file_name=filename,
        mime="text/csv",
        use_container_width=True,
    )
with dl2:
    st.markdown(
        '<div style="padding-top:0.45rem;font-size:0.82rem;color:#64748b;line-height:1.6;">'
        "The CSV includes all columns from the original file plus "
        "<b>Status</b>, <b>Risk Level</b>, <b>Flags</b>, <b>Screened At</b>, and <b>Data Source</b>."
        "</div>",
        unsafe_allow_html=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Footer
# ─────────────────────────────────────────────
st.markdown(
    '<div class="footer">'
    "🔍 <b>BOM Compliance &amp; Sanctions Screener</b> &nbsp;·&nbsp; "
    "<span>For demonstration purposes only — not legal compliance advice</span><br>"
    "Always verify against official "
    "<a href='https://sanctionssearch.ofac.treas.gov/' target='_blank'>OFAC SDN</a>, "
    "<a href='https://www.bis.doc.gov/index.php/policy-guidance/lists-of-parties-of-concern' target='_blank'>BIS Entity List</a>, "
    "<a href='https://main.un.org/securitycouncil/en/content/un-sc-consolidated-list' target='_blank'>UN Consolidated List</a>, and "
    "<a href='https://eeas.europa.eu/topics/sanctions-policy/' target='_blank'>EU Sanctions</a> lists."
    "</div>",
    unsafe_allow_html=True,
)
