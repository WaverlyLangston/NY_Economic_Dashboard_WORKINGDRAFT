"""
build_page.py  –  Single-column layout, wider charts, earthy palette.
"""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots
from config import OUTPUT_FILES, DOCS_DIR

os.makedirs(DOCS_DIR, exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
CREAM      = "#F7F3EE";  WHITE     = "#FFFFFF"
TEXT_DARK  = "#2A2420";  TEXT_MID  = "#6E6460";  TEXT_LIGHT = "#A09590"
BORDER     = "#E5DDD5";  PLOT_BG   = "#FDFAF7"
NY_RUST    = "#8B5E52";  US_SAGE   = "#5C7A6A"
TAN        = "#B89A72";  DUSTY     = "#7A9BAA"
WARM_BRN   = "#9B7B6B";  DEEP_SAGE = "#4A6B5A"
SAND       = "#C4A882";  STEEL     = "#6E8A9A"
MUT_RED    = "#A05550";  OLIVE     = "#7A8C5A"

IND_PAL = [NY_RUST, US_SAGE, TAN, DUSTY, WARM_BRN,
           DEEP_SAGE, SAND, STEEL, MUT_RED, OLIVE, "#9B8B6B", "#7A9B8A"]

PEER_COL = {"New York": NY_RUST, "Massachusetts": DUSTY,
            "New Jersey": TAN, "Connecticut": US_SAGE, "United States": WARM_BRN}

CFG = {"displayModeBar": True, "responsive": True,
       "modeBarButtonsToRemove": ["select2d","lasso2d"], "displaylogo": False}

# ── Layout helpers ────────────────────────────────────────────────────────────
def L(title="", h=500, bm=110):
    """Base layout dict. Always mutate keys before unpacking — never add
    legend= as a separate kwarg to update_layout(**L(...))."""
    return {
        "title":         dict(text=title, font=dict(size=15, color=TEXT_DARK,
                              family="Georgia, serif"), x=0, xanchor="left", pad=dict(b=6)),
        "paper_bgcolor": WHITE, "plot_bgcolor": PLOT_BG,
        "font":          dict(family="'Segoe UI',Arial,sans-serif", size=11, color=TEXT_MID),
        "legend":        dict(orientation="h", yanchor="top", y=-0.13,
                              xanchor="center", x=0.5,
                              font=dict(size=10, color=TEXT_MID),
                              bgcolor="rgba(0,0,0,0)", borderwidth=0,
                              entrywidth=160, entrywidthmode="pixels"),
        "margin":        dict(l=60, r=30, t=58, b=bm),
        "height":        h,
        "hovermode":     "x unified",
        "xaxis":         dict(showgrid=False, linecolor=BORDER, tickcolor=BORDER,
                              tickfont=dict(color=TEXT_LIGHT, size=10)),
        "yaxis":         dict(gridcolor="#EDE8E3", gridwidth=1,
                              linecolor="rgba(0,0,0,0)", zeroline=False,
                              tickfont=dict(color=TEXT_LIGHT, size=10)),
        "hoverlabel":    dict(bgcolor=WHITE, bordercolor=BORDER,
                              font=dict(size=11, color=TEXT_DARK)),
    }

def sa(text, y=-0.20):
    return dict(text=text, xref="paper", yref="paper",
                x=0, y=y, xanchor="left", yanchor="top",
                font=dict(size=9, color=TEXT_LIGHT), showarrow=False)

def ddmenu(buttons, x=0.0, y=1.11):
    return [dict(buttons=buttons, direction="down", showactive=True,
                 x=x, xanchor="left", y=y, yanchor="top",
                 bgcolor=WHITE, bordercolor=BORDER, borderwidth=1,
                 font=dict(size=10, color=TEXT_DARK),
                 pad=dict(r=6, t=3, b=3, l=6))]

def to_html(fig, div_id=None):
    kw = dict(full_html=False, include_plotlyjs=False, config=CFG)
    if div_id: kw["div_id"] = div_id
    return pio.to_html(fig, **kw)

def load(key):
    p = OUTPUT_FILES.get(key)
    if p and os.path.exists(p):
        with open(p) as f: return json.load(f)
    print(f"  Missing: {key}")
    return None

def ax_title(text):
    return dict(text=text, font=dict(size=10, color=TEXT_LIGHT))

# ══ BUSINESS FORMATION ════════════════════════════════════════════════════════
def chart_bfs():
    data = load("bfs")
    if not data: return "<p>BFS data unavailable.</p>", "<p>BFS data unavailable.</p>"
    df = pd.DataFrame(data); df["time"] = pd.to_datetime(df["time"])
    src = "U.S. Census Bureau, Business Formation Statistics"

    fig_a = go.Figure()
    for col, color, name in [
        ("NY Business Applications",                 NY_RUST, "Business Applications"),
        ("NY High Propensity Business Applications", DUSTY,   "High Propensity"),
    ]:
        if col in df.columns:
            fig_a.add_trace(go.Scatter(x=df["time"], y=df[col], name=name,
                line=dict(color=color, width=1.8),
                hovertemplate="%{x|%b %Y}: %{y:,.0f}<extra></extra>"))
    la = L("New York Business Application Levels", h=480, bm=105)
    la["xaxis"]["title"] = ax_title("Monthly, Seasonally Adjusted")
    la["yaxis"]["title"] = ax_title("Applications")
    la["annotations"]    = [sa(f"Source: {src}", -0.22)]
    fig_a.update_layout(**la)

    traces_ba, traces_hba = [], []
    for col, color, geo in [
        ("NY Business Applications Per Capita 12mo MA",   NY_RUST, "New York"),
        ("U.S. Business Applications Per Capita 12mo MA", US_SAGE, "United States"),
    ]:
        y = df[col].tolist() if col in df.columns else [None]*len(df)
        traces_ba.append(go.Scatter(x=df["time"], y=y, name=geo,
            line=dict(color=color, width=2), visible=True,
            hovertemplate=f"{geo}: %{{y:.3f}}<extra></extra>"))
    for col, color, geo in [
        ("NY High Propensity Business Applications Per Capita 12mo MA",   NY_RUST, "New York"),
        ("U.S. High Propensity Business Applications Per Capita 12mo MA", US_SAGE, "United States"),
    ]:
        y = df[col].tolist() if col in df.columns else [None]*len(df)
        traces_hba.append(go.Scatter(x=df["time"], y=y, name=geo,
            line=dict(color=color, width=2), visible=False,
            hovertemplate=f"{geo}: %{{y:.3f}}<extra></extra>"))
    n = len(traces_ba)
    fig_b = go.Figure(data=traces_ba + traces_hba)
    lb = L("Business Applications per Capita — 12-Month Moving Average", h=480, bm=105)
    lb["xaxis"]["title"]  = ax_title("Monthly, Seasonally Adjusted")
    lb["yaxis"]["title"]  = ax_title("Per 1,000 People")
    lb["updatemenus"]     = ddmenu([
        dict(label="Business Applications", method="update",
             args=[{"visible": [True]*n + [False]*n}]),
        dict(label="High Propensity",        method="update",
             args=[{"visible": [False]*n + [True]*n}]),
    ])
    lb["annotations"] = [sa(f"Source: {src}", -0.22)]
    fig_b.update_layout(**lb)
    return to_html(fig_a, "bfs_levels"), to_html(fig_b, "bfs_percapita")


# ══ GDP ═══════════════════════════════════════════════════════════════════════
def _index_to(series, ref_idx):
    ref = series.iloc[ref_idx] if abs(ref_idx) <= len(series) else series.iloc[0]
    return None if (pd.isna(ref) or ref == 0) else (series / ref) - 1.0

def chart_gdp_peer():
    """Peer-state real GDP levels — NY, NJ, MA, CT, US."""
    data = load("bea_gdp")
    if not data: return "<p>GDP data unavailable.</p>"

    df    = pd.DataFrame(data)
    times = df["time"].tolist()
    src   = "U.S. Bureau of Economic Analysis, Real GDP (SQGDP9)"

    state_order = ["New York", "New Jersey", "Massachusetts", "Connecticut", "United States"]

    fig = go.Figure()
    for state in state_order:
        if state not in df.columns:
            continue
        vals = pd.to_numeric(df[state], errors="coerce").tolist()
        fig.add_trace(go.Scatter(
            x=times, y=vals, name=state,
            line=dict(color=PEER_COL.get(state, TEXT_LIGHT),
                      width=2.5 if state == "New York" else 1.8),
            hovertemplate=f"{state}: $%{{y:,.0f}}M<extra></extra>",
        ))

    lay = L("Real GDP by State", h=520, bm=110)
    lay["xaxis"]["title"]      = ax_title("Quarterly")
    lay["yaxis"]["title"]      = ax_title("Real GDP (Millions of Chained 2017 $)")
    lay["yaxis"]["tickformat"] = ",.0f"
    lay["annotations"]         = [sa(f"Source: {src}", -0.22)]
    fig.update_layout(**lay)
    return to_html(fig, "gdp_peer")

def chart_gdp_industry_growth():
    """NY vs US GDP index with JS-powered base-year/quarter selector."""
    data = load("bea_gdp")
    if not data: return "<p>GDP data unavailable.</p>"

    df     = pd.DataFrame(data)
    times  = df["time"].tolist()
    states = ["New York", "United States"]
    src    = "U.S. Bureau of Economic Analysis, Real GDP (SQGDP9)"

    raw_series = {}
    for state in states:
        if state in df.columns:
            raw_series[state] = pd.to_numeric(df[state], errors="coerce").tolist()

    def find_idx(q_str):
        try: return times.index(q_str)
        except ValueError: return 0

    default_ref = find_idx("2019Q1")
    state_colors = {"New York": NY_RUST, "United States": US_SAGE}

    def make_traces(ref_idx):
        traces = []
        for state in states:
            if state not in raw_series: continue
            vals = pd.Series(raw_series[state])
            if ref_idx >= len(vals): continue
            ref = vals.iloc[ref_idx]
            if pd.isna(ref) or ref == 0: continue
            indexed = ((vals / ref) - 1.0).tolist()
            traces.append(go.Scatter(
                x=times, y=indexed, name=state,
                line=dict(color=state_colors.get(state, TEXT_LIGHT),
                          width=2.5 if state == "New York" else 1.8),
                hovertemplate=f"{state}: %{{y:.1%}}<extra></extra>",
            ))
        return traces

    fig = go.Figure(data=make_traces(default_ref))
    fig.add_hline(y=0, line_dash="dot", line_color=BORDER, line_width=1)

    lay = L("GDP Index — New York vs. United States", h=480, bm=110)
    lay["xaxis"]["title"]      = ax_title("Quarterly")
    lay["yaxis"]["tickformat"] = ".0%"
    lay["yaxis"]["title"]      = ax_title("Change from Base Period")
    lay["annotations"]         = [sa(f"Source: {src}", -0.22)]
    fig.update_layout(**lay)

    raw_json   = json.dumps(raw_series)
    times_json = json.dumps(times)
    available_quarters = sorted(set(times))
    years    = sorted(set(q[:4] for q in available_quarters))
    quarters = ["Q1","Q2","Q3","Q4"]

    yr_opts  = "\n".join(f'<option value="{y}" {"selected" if y=="2019" else ""}>{y}</option>' for y in years)
    qtr_opts = "\n".join(f'<option value="{q}" {"selected" if q=="Q1" else ""}>{q}</option>' for q in quarters)

    chart_html = to_html(fig, "gdp_ny_us_index")

    widget = f"""
<div class="index-selector" id="gdp_ny_us_controls">
  <span class="index-label">Indexed to:</span>
  <select class="index-select" id="gdp_ny_us_year">{yr_opts}</select>
  <select class="index-select" id="gdp_ny_us_qtr">{qtr_opts}</select>
</div>
{chart_html}
<script>
(function(){{
  var raw    = {raw_json};
  var times  = {times_json};
  var states = {json.dumps(states)};

  function reindex(refStr) {{
    var refIdx = times.indexOf(refStr);
    if (refIdx < 0) refIdx = 0;
    var yArrays = [];
    states.forEach(function(state) {{
      if (!raw[state]) {{ yArrays.push([]); return; }}
      var vals = raw[state];
      var ref  = vals[refIdx];
      if (!ref || isNaN(ref)) {{ yArrays.push(vals.map(function(){{return null;}})); return; }}
      yArrays.push(vals.map(function(v){{ return (v/ref)-1; }}));
    }});
    var traces = states.map(function(_,i){{return i;}});
    Plotly.restyle('gdp_ny_us_index', {{y: yArrays}}, traces);
  }}

  function update() {{
    var yr  = document.getElementById('gdp_ny_us_year').value;
    var qtr = document.getElementById('gdp_ny_us_qtr').value;
    reindex(yr + qtr);
  }}

  document.getElementById('gdp_ny_us_year').addEventListener('change', update);
  document.getElementById('gdp_ny_us_qtr').addEventListener('change', update);
}})();
</script>"""
    return widget

def chart_gdp_industry_bar():
    """NY GDP by industry — interactive levels chart. Total visible by default;
    click legend entries to add individual industries."""
    data = load("bea_gdp_industry")
    if not data: return "<p>GDP industry data unavailable.</p>"
    qtr = data.get("quarterly_by_industry", {})
    if not qtr: return "<p>GDP quarterly industry data unavailable.</p>"

    src       = "U.S. Bureau of Economic Analysis, Real GDP (SQGDP9)"
    total_key = "All industry total"

    # Sub-components of already-included aggregates — skip to avoid double-counting
    skip = {
        "Private industries",
        "Durable goods manufacturing",
        "Nondurable goods manufacturing",
        "Federal civilian",
        "Military",
        "State and local",
    }

    industry_keys = [k for k in qtr.keys() if k != total_key and k not in skip]

    # Sort by latest value descending for a logical legend order
    def latest_val(k):
        v = qtr[k]["values"]
        return v[-1] if v else 0
    industry_keys = sorted(industry_keys, key=latest_val, reverse=True)

    # Build total lookup for % computation
    total_map = {}
    if total_key in qtr:
        total_map = dict(zip(qtr[total_key]["times"], qtr[total_key]["values"]))

    fig = go.Figure()

    # "All industry total" trace — visible by default
    if total_key in qtr:
        td = qtr[total_key]
        fig.add_trace(go.Scatter(
            x=td["times"], y=td["values"],
            name="All Industries",
            visible=True,
            line=dict(color=NY_RUST, width=2.5),
            hovertemplate="All Industries: $%{y:,.0f}M (100%)<extra></extra>",
        ))
    elif industry_keys:
        # Fallback: show highest-GDP industry if total unavailable
        k0 = industry_keys[0]
        td = qtr[k0]
        fig.add_trace(go.Scatter(
            x=td["times"], y=td["values"],
            name=k0,
            visible=True,
            line=dict(color=NY_RUST, width=2.5),
            hovertemplate=f"{k0}: $%{{y:,.0f}}M<extra></extra>",
        ))
        industry_keys = industry_keys[1:]

    # Individual industry traces — legendonly until clicked
    for i, ind in enumerate(industry_keys):
        sd         = qtr[ind]
        times_list = sd["times"]
        vals_raw   = sd["values"]

        pct_list = []
        for t, v in zip(times_list, vals_raw):
            tot = total_map.get(t)
            pct_list.append(round(v / tot * 100, 1) if tot and tot > 0 else None)

        has_pct    = bool(total_map)
        color      = IND_PAL[i % len(IND_PAL)]

        if has_pct:
            ht     = f"{ind}: $%{{y:,.0f}}M (%{{customdata[0]:.1f}}%)<extra></extra>"
            cdata  = [[p] for p in pct_list]
            fig.add_trace(go.Scatter(
                x=times_list, y=vals_raw,
                name=ind, visible="legendonly",
                line=dict(color=color, width=1.8),
                customdata=cdata,
                hovertemplate=ht,
            ))
        else:
            fig.add_trace(go.Scatter(
                x=times_list, y=vals_raw,
                name=ind, visible="legendonly",
                line=dict(color=color, width=1.8),
                hovertemplate=f"{ind}: $%{{y:,.0f}}M<extra></extra>",
            ))

    lay = L("New York GDP by Industry", h=600, bm=200)
    lay["legend"] = dict(
        orientation="h", yanchor="top", y=-0.22,
        xanchor="center", x=0.5,
        font=dict(size=9, color=TEXT_MID),
        bgcolor="rgba(0,0,0,0)", borderwidth=0,
        entrywidth=190, entrywidthmode="pixels",
        itemclick="toggle",
        itemdoubleclick="toggleothers",
    )
    lay["xaxis"]["title"]      = ax_title("Quarterly")
    lay["yaxis"]["title"]      = ax_title("Real GDP (Millions of Chained 2017 $)")
    lay["yaxis"]["tickformat"] = ",.0f"
    lay["annotations"]         = [sa(f"Source: {src}", -0.34)]
    fig.update_layout(**lay)
    return to_html(fig, "gdp_ind_levels")


# ══ HOUSING ═══════════════════════════════════════════════════════════════════
def chart_housing():
    data = load("acs_housing")
    if not data: return "<p>Housing data unavailable.</p>"
    df = pd.DataFrame(data)
    ny = df[df["geography"]=="New York"].sort_values("year")
    us = df[df["geography"]=="United States"].sort_values("year")
    src = "U.S. Census Bureau, American Community Survey (ACS 1-Year)"

    fig1 = go.Figure()
    for d, color, name in [(ny, NY_RUST, "New York"), (us, US_SAGE, "United States")]:
        fig1.add_trace(go.Scatter(x=d["year"], y=d["rental_vacancy_rate"], name=name,
            line=dict(color=color, width=2),
            hovertemplate=f"{name}: %{{y:.1%}}<extra></extra>"))
    l1 = L("Rental Vacancy Rate", h=420, bm=100)
    l1["yaxis"]["tickformat"] = ".1%"
    l1["yaxis"]["title"] = ax_title("Rate")
    l1["xaxis"]["title"] = ax_title("Year")
    fig1.update_layout(**l1)

    fig2 = go.Figure()
    ny_yoy = ny.set_index("year")["total_units"].pct_change()
    us_yoy = us.set_index("year")["total_units"].pct_change()
    for yrs, yoy, color, name in [
        (ny["year"].values[1:], ny_yoy.dropna().values, NY_RUST,  "New York"),
        (us["year"].values[1:], us_yoy.dropna().values, US_SAGE, "United States"),
    ]:
        fig2.add_trace(go.Scatter(x=yrs, y=yoy, name=name,
            line=dict(color=color, width=2),
            hovertemplate=f"{name}: %{{y:.2%}}<extra></extra>"))
    l2 = L("Changes in Housing Stock, Year-Over-Year", h=420, bm=105)
    l2["yaxis"]["tickformat"] = ".2%"
    l2["yaxis"]["title"] = ax_title("YoY Change")
    l2["xaxis"]["title"] = ax_title("Year")
    l2["annotations"]    = [sa(f"Source: {src}", -0.24)]
    fig2.update_layout(**l2)
    return to_html(fig1, "housing_vac") + to_html(fig2, "housing_stock")


# ══ JOLTS ═════════════════════════════════════════════════════════════════════
def chart_jolts():
    data = load("bls_jolts")
    if not data or not data.get("monthly"):
        return "<p>JOLTS data unavailable.</p>", "<p>JOLTS data unavailable.</p>"
    df = pd.DataFrame(data["monthly"]); df["time"] = pd.to_datetime(df["time"])
    src = "U.S. Bureau of Labor Statistics, JOLTS"

    LEVELS = {
        "NY Job Openings Level":           ("Job Openings",        DUSTY),
        "NY Hires Level":                  ("Hires",               NY_RUST),
        "NY Total Separations Level":      ("Total Separations",   US_SAGE),
        "NY Layoffs and Discharges Level": ("Layoffs & Discharges", TAN),
        "NY Quits Level":                  ("Quits",               WARM_BRN),
    }
    fig_a = go.Figure()
    for col, (lbl, color) in LEVELS.items():
        if col in df.columns:
            fig_a.add_trace(go.Scatter(x=df["time"], y=df[col], name=lbl,
                line=dict(color=color, width=1.8),
                hovertemplate=f"{lbl}: %{{y:,.0f}}<extra></extra>"))
    la = L("New York Job Market Levels", h=480, bm=100)
    la["xaxis"]["title"] = ax_title("Monthly, Seasonally Adjusted")
    la["yaxis"]["title"] = ax_title("Workers")
    la["annotations"]    = [sa(f"Source: {src}", -0.22)]
    fig_a.update_layout(**la)

    RATES = {
        "Unemployed per Opening": ("NY Unemployed per Job Opening Ratio","U.S. Unemployed per Job Opening Ratio"),
        "Job Openings Rate":      ("NY Job Openings Rate","U.S. Job Openings Rate"),
        "Hires Rate":             ("NY Hires Rate","U.S. Hires Rate"),
        "Quits Rate":             ("NY Quits Rate","U.S. Quits Rate"),
        "Layoffs Rate":           ("NY Layoffs and Discharges Rate","U.S. Layoffs and Discharges Rate"),
        "Separations Rate":       ("NY Total Separations Rate","U.S. Total Separations Rate"),
    }
    all_t, btns, idx = [], [], 0
    for metric, (ny_c, us_c) in RATES.items():
        is_first = (idx == 0)
        fmt = ".2f" if "Opening" in metric else ".1%"
        for col, color, geo in [(ny_c, NY_RUST, "New York"),(us_c, US_SAGE, "United States")]:
            y = df[col].tolist() if col in df.columns else [None]*len(df)
            all_t.append(go.Scatter(x=df["time"], y=y, name=geo,
                line=dict(color=color, width=2), visible=is_first,
                hovertemplate=f"{geo}: %{{y:{fmt}}}<extra></extra>"))
        btns.append(dict(label=metric, method="update",
            args=[{"visible":[i in [idx,idx+1] for i in range(len(RATES)*2)]}]))
        idx += 2

    fig_b = go.Figure(data=all_t)
    lb = L("New York and U.S. Job Market Rates", h=480, bm=100)
    lb["xaxis"]["title"] = ax_title("Monthly, Seasonally Adjusted")
    lb["yaxis"]["title"] = ax_title("Rate")
    lb["updatemenus"]    = ddmenu(btns)
    lb["annotations"]    = [sa(f"Source: {src}", -0.22)]
    fig_b.update_layout(**lb)
    return to_html(fig_a, "jolts_lvl"), to_html(fig_b, "jolts_rates")


# ══ CES ═══════════════════════════════════════════════════════════════════════
def chart_ces():
    data = load("bls_ces")
    if not data:
        return "<p>CES data unavailable.</p>","<p>CES data unavailable.</p>","<p>CES data unavailable.</p>"
    monthly = pd.DataFrame(data.get("monthly",[])); changes = data.get("changes",[])
    ref_date = data.get("reference_date",""); src = "U.S. Bureau of Labor Statistics, CES"
    if monthly.empty: return "<p>CES data unavailable.</p>","",""
    monthly["time"] = pd.to_datetime(monthly["time"])
    ind_idx = [c for c in monthly.columns if c.endswith(" Index")
               and c not in ("Total Nonfarm Index","Total Private Index","Government Index")]

    fig_a = go.Figure()
    for i, col in enumerate(ind_idx):
        lbl = col.replace(" Index","")
        fig_a.add_trace(go.Scatter(x=monthly["time"], y=monthly[col], name=lbl,
            line=dict(color=IND_PAL[i%len(IND_PAL)], width=1.8),
            hovertemplate=f"{lbl}: %{{y:.1%}}<extra></extra>"))
    fig_a.add_hline(y=0, line_dash="dot", line_color=BORDER, line_width=1)
    la = L("New York Jobs Index by Industry", h=520, bm=145)
    la["legend"] = dict(orientation="h", yanchor="top", y=-0.20,
                        xanchor="center", x=0.5,
                        font=dict(size=9, color=TEXT_MID),
                        bgcolor="rgba(0,0,0,0)", borderwidth=0,
                        entrywidth=175, entrywidthmode="pixels")
    la["xaxis"]["title"]      = ax_title("Monthly, Seasonally Adjusted")
    la["yaxis"]["tickformat"]  = ".0%"
    la["yaxis"]["title"]       = ax_title("Change from Base")
    la["annotations"]          = [sa(f"Source: {src} (base: {ref_date})", -0.30)]
    fig_a.update_layout(**la)

    fig_b = go.Figure()
    for col, color, lbl in [("Total Private Index",NY_RUST,"Total Private"),
                             ("Government Index",DUSTY,"Government")]:
        if col in monthly.columns:
            fig_b.add_trace(go.Scatter(x=monthly["time"], y=monthly[col], name=lbl,
                line=dict(color=color, width=2.5),
                hovertemplate=f"{lbl}: %{{y:.1%}}<extra></extra>"))
    fig_b.add_hline(y=0, line_dash="dot", line_color=BORDER, line_width=1)
    lb = L("Government vs. Total Private Employment", h=480, bm=100)
    lb["xaxis"]["title"]      = ax_title("Monthly, Seasonally Adjusted")
    lb["yaxis"]["tickformat"]  = ".0%"
    lb["yaxis"]["title"]       = ax_title("Change from Base")
    lb["annotations"]          = [sa(f"Source: {src} (base: {ref_date})", -0.22)]
    fig_b.update_layout(**lb)

    html_c = ""
    if changes:
        df_c = pd.DataFrame(changes).dropna(subset=["change"])
        df_c = df_c[~df_c["industry"].isin(["Total Nonfarm","Total Private"])].sort_values("change")
        as_of = df_c["as_of"].iloc[0] if not df_c.empty else ""
        fig_c = go.Figure(go.Bar(
            x=df_c["industry"], y=df_c["change"],
            marker_color=[NY_RUST if v>=0 else US_SAGE for v in df_c["change"]],
            hovertemplate="%{x}: %{y:+,.0f} jobs<extra></extra>"))
        lc = L(f"Change in Number of Jobs by Industry — {as_of}", h=460, bm=115)
        lc["xaxis"]["tickangle"] = -30; lc["xaxis"]["title"] = ""
        lc["yaxis"]["title"]     = ax_title("Jobs")
        lc["annotations"]        = [sa(f"Source: {src}", -0.26)]
        fig_c.update_layout(**lc)
        html_c = to_html(fig_c, "ces_chg")
    return to_html(fig_a, "ces_idx"), to_html(fig_b, "ces_gp"), html_c


# ══ LAUS ══════════════════════════════════════════════════════════════════════
def chart_laus():
    data = load("bls_laus")
    if not data: return "<p>LAUS data unavailable.</p>","<p>LAUS data unavailable.</p>"
    df = pd.DataFrame(data); df["time"] = pd.to_datetime(df["time"])
    src = "U.S. Bureau of Labor Statistics, LAUS"

    fig_a = make_subplots(specs=[[{"secondary_y": True}]])
    for col, color, name in [
        ("NY Labor Force Level", DUSTY,   "Labor Force"),
        ("NY Employment Level",  NY_RUST, "Employment"),
    ]:
        if col in df.columns:
            fig_a.add_trace(go.Scatter(x=df["time"], y=df[col], name=name,
                line=dict(color=color, width=2),
                hovertemplate=f"{name}: %{{y:,.0f}}<extra></extra>"), secondary_y=False)
    if "NY Unemployment Level" in df.columns:
        fig_a.add_trace(go.Scatter(x=df["time"], y=df["NY Unemployment Level"],
            name="Unemployment", line=dict(color=TAN, width=2),
            hovertemplate="Unemployment: %{y:,.0f}<extra></extra>"), secondary_y=True)
    fig_a.update_yaxes(title_text="Employment & Labor Force", secondary_y=False,
        gridcolor="#EDE8E3", tickfont=dict(color=TEXT_LIGHT, size=10))
    fig_a.update_yaxes(title_text="Unemployed", secondary_y=True,
        tickfont=dict(color=TEXT_LIGHT, size=10))
    fig_a.update_layout(
        title=dict(text="New York State Labor Force",
            font=dict(size=15,color=TEXT_DARK,family="Georgia, serif"), x=0, xanchor="left"),
        paper_bgcolor=WHITE, plot_bgcolor=PLOT_BG,
        font=dict(family="'Segoe UI',Arial,sans-serif",size=11,color=TEXT_MID),
        legend=dict(orientation="h", yanchor="top", y=-0.13, xanchor="center", x=0.5,
            font=dict(size=10,color=TEXT_MID), bgcolor="rgba(0,0,0,0)",
            entrywidth=160, entrywidthmode="pixels"),
        margin=dict(l=60,r=30,t=58,b=105), height=480, hovermode="x unified",
        xaxis=dict(title=ax_title("Monthly, Seasonally Adjusted"),
            showgrid=False, linecolor=BORDER, tickfont=dict(color=TEXT_LIGHT,size=10)),
        annotations=[sa(f"Source: {src}", -0.22)],
    )

    RATE_M = {
        "Unemployment Rate":              ("NY Unemployment Rate","U.S. Unemployment Rate"),
        "Labor Force Participation Rate": ("NY Labor Force Participation Rate","U.S. Labor Force Participation Rate"),
        "Employment-Population Ratio":    ("NY Employment-Population Ratio","U.S. Employment-Population Ratio"),
    }
    all_t, btns, idx = [], [], 0
    for metric, (ny_c, us_c) in RATE_M.items():
        is_first = (idx == 0)
        for col, color, geo in [(ny_c,NY_RUST,"New York"),(us_c,US_SAGE,"United States")]:
            y = df[col].tolist() if col in df.columns else [None]*len(df)
            all_t.append(go.Scatter(x=df["time"], y=y, name=geo,
                line=dict(color=color,width=2), visible=is_first,
                hovertemplate=f"{geo}: %{{y:.1%}}<extra></extra>"))
        btns.append(dict(label=metric, method="update",
            args=[{"visible":[i in [idx,idx+1] for i in range(len(RATE_M)*2)]}]))
        idx += 2
    fig_b = go.Figure(data=all_t)
    lb = L("New York and U.S. Labor Force Rates", h=480, bm=100)
    lb["xaxis"]["title"]     = ax_title("Monthly, Seasonally Adjusted")
    lb["yaxis"]["tickformat"] = ".1%"
    lb["yaxis"]["title"]     = ax_title("Rate")
    lb["updatemenus"]        = ddmenu(btns)
    lb["annotations"]        = [sa(f"Source: {src}", -0.22)]
    fig_b.update_layout(**lb)
    return to_html(fig_a, "laus_lvl"), to_html(fig_b, "laus_rates")


# ══ POPULATION & MIGRATION ════════════════════════════════════════════════════
def chart_population():
    pop_data = load("pep_population"); mig_data = load("irs_migration")
    age_data = load("pep_age"); charts = []

    if pop_data:
        ny = pd.DataFrame(pop_data)
        ny = ny[ny["geography"]=="New York"].sort_values("year")
        if not ny.empty:
            fig = go.Figure(go.Scatter(x=ny["year"], y=ny["population"],
                line=dict(color=NY_RUST,width=2.5),
                fill="tozeroy", fillcolor="rgba(139,94,82,0.07)",
                hovertemplate="Year %{x}: %{y:,.0f}<extra></extra>"))
            lay = L("New York State Population", h=420, bm=85)
            lay["yaxis"]["tickformat"] = ","
            lay["yaxis"]["title"] = ax_title("Population")
            lay["xaxis"]["title"] = ax_title("Year")
            lay["annotations"]    = [sa("Source: U.S. Census Bureau, Population Estimates", -0.20)]
            fig.update_layout(**lay)
            charts.append(to_html(fig, "pop_total"))

    if mig_data and mig_data.get("annual_net"):
        net_df = pd.DataFrame(mig_data["annual_net"])
        fig = go.Figure()
        fig.add_trace(go.Bar(name="Inflow",  x=net_df["year_label"],
            y=net_df["inflow_people"],  marker_color=US_SAGE,
            hovertemplate="%{x} Inflow: %{y:,.0f}<extra></extra>"))
        fig.add_trace(go.Bar(name="Outflow", x=net_df["year_label"],
            y=[-v for v in net_df["outflow_people"]], marker_color=TAN,
            hovertemplate="%{x} Outflow: %{y:,.0f}<extra></extra>"))
        fig.add_trace(go.Scatter(name="Net Migration", x=net_df["year_label"],
            y=net_df["net_people"], mode="lines+markers",
            line=dict(color=NY_RUST, width=2.5),
            marker=dict(color=NY_RUST, size=7),
            hovertemplate="%{x} Net: %{y:+,.0f}<extra></extra>"))
        fig.add_hline(y=0, line_color=BORDER, line_width=1)
        lay = L("New York State Domestic Migration", h=440, bm=105)
        lay["barmode"]            = "relative"
        lay["yaxis"]["title"]     = ax_title("People")
        lay["xaxis"]["title"]     = ax_title("Year")
        lay["annotations"]        = [sa("Source: IRS Statistics of Income, State-to-State Migration", -0.24)]
        fig.update_layout(**lay)
        charts.append(to_html(fig, "migration"))

    if age_data:
        age_df = pd.DataFrame(age_data)
        if not age_df.empty:
            age_order  = ["Under 5","5 To 13","14 To 17","18 To 24","25 To 44","45 To 64","65 And Over"]
            age_colors = ["#A0C878","#7A9BAA","#C4A882","#B89A72","#8B5E52","#5C7A6A","#2A2420"]
            fig = go.Figure()
            for age, color in zip(age_order, age_colors):
                grp = age_df[age_df["age_group"]==age].sort_values("year")
                if grp.empty: continue
                fig.add_trace(go.Bar(x=grp["year"], y=grp["population"], name=age,
                    marker_color=color,
                    hovertemplate=f"{age}: %{{y:,.0f}}<extra></extra>"))
            lay = L("Age Distribution of New York State Population", h=460, bm=105)
            lay["barmode"]            = "stack"
            lay["yaxis"]["tickformat"] = ","
            lay["yaxis"]["title"]     = ax_title("Population")
            lay["xaxis"]["title"]     = ax_title("Year")
            lay["annotations"]        = [sa("Source: U.S. Census Bureau, Population Estimates", -0.24)]
            fig.update_layout(**lay)
            charts.append(to_html(fig, "pop_age"))

    return "".join(charts) if charts else "<p>Population data unavailable.</p>"


# ══ POVERTY ═══════════════════════════════════════════════════════════════════
def chart_poverty():
    data = load("acs_poverty")
    if not data: return "<p>Poverty data unavailable.</p>"
    df = pd.DataFrame(data); latest = df["year"].max()
    df = df[df["year"]==latest]
    ny = df[df["geography"]=="New York"]; us = df[df["geography"]=="United States"]
    groups = ["White alone","Black or African American alone","Some other race alone",
              "Asian alone","American Indian and Alaska Native alone",
              "Two or more races","Hispanic or Latino (of any race)","Female","Male"]
    ny_r, us_r = [], []
    for g in groups:
        nr = ny[ny["group"]==g]; ur = us[us["group"]==g]
        ny_r.append(nr["rate"].values[0] if not nr.empty else None)
        us_r.append(ur["rate"].values[0] if not ur.empty else None)
    ny_t = ny[ny["group"]=="Total"]["rate"].values
    us_t = us[us["group"]=="Total"]["rate"].values
    ny_total = ny_t[0] if len(ny_t) else None
    us_total = us_t[0] if len(us_t) else None
    fig = go.Figure()
    fig.add_trace(go.Bar(x=groups, y=ny_r, name="New York", marker_color=NY_RUST,
        hovertemplate="%{x}<br>NY: %{y:.1%}<extra></extra>"))
    fig.add_trace(go.Scatter(x=groups, y=us_r, name="United States",
        mode="markers", marker=dict(color=US_SAGE,size=12,symbol="circle"),
        hovertemplate="%{x}<br>U.S.: %{y:.1%}<extra></extra>"))
    anns = []
    if ny_total is not None:
        fig.add_hline(y=ny_total, line_color=NY_RUST, line_dash="dash", line_width=1, opacity=0.5)
        anns.append(dict(text=f"NY Total: {ny_total:.1%}", xref="paper", yref="y",
            x=0.01, y=ny_total, yshift=8, font=dict(size=9,color=NY_RUST), showarrow=False))
    if us_total is not None:
        fig.add_hline(y=us_total, line_color=US_SAGE, line_dash="dot", line_width=1, opacity=0.5)
        anns.append(dict(text=f"U.S. Total: {us_total:.1%}", xref="paper", yref="y",
            x=0.6, y=us_total, yshift=8, font=dict(size=9,color=US_SAGE), showarrow=False))
    anns.append(sa(f"Source: U.S. Census Bureau, {latest} 1-Year ACS", -0.26))
    lay = L(f"Poverty Rate by Demographic Group — {latest}", h=460, bm=110)
    lay["xaxis"]["tickangle"]  = -25; lay["xaxis"]["title"] = ""
    lay["yaxis"]["tickformat"]  = ".0%"
    lay["yaxis"]["title"]      = ax_title("Poverty Rate")
    lay["annotations"]         = anns
    fig.update_layout(**lay)
    return to_html(fig, "poverty")


# ══ INCOME ════════════════════════════════════════════════════════════════════
def chart_income():
    data = load("acs_income")
    if not data: return "<p>Income data unavailable.</p>"
    df = pd.DataFrame(data); latest = df["year"].max()
    df = df[df["year"]==latest]
    ny = df[df["geography"]=="New York"]; us = df[df["geography"]=="United States"]
    groups = ["White alone","Black or African American","Some other race","Asian",
              "American Indian and Alaska Native","Two or more races",
              "Hispanic or Latino (of any race)"]
    ny_v, us_v, disp = [], [], []
    for g in groups:
        nr = ny[ny["group"].str.contains(g.split()[0],case=False,na=False)].head(1)
        ur = us[us["group"].str.contains(g.split()[0],case=False,na=False)].head(1)
        ny_v.append(float(nr["value"].values[0]) if not nr.empty and nr["value"].values[0] else None)
        us_v.append(float(ur["value"].values[0]) if not ur.empty and ur["value"].values[0] else None)
        disp.append(g)
    ny_tot = ny[ny["group"]=="All Households"]["value"].values
    us_tot = us[us["group"]=="All Households"]["value"].values
    ny_all = float(ny_tot[0]) if len(ny_tot) and ny_tot[0] else None
    us_all = float(us_tot[0]) if len(us_tot) and us_tot[0] else None
    fig = go.Figure()
    fig.add_trace(go.Bar(x=disp, y=ny_v, name="New York", marker_color=NY_RUST,
        hovertemplate="%{x}<br>NY: $%{y:,.0f}<extra></extra>"))
    fig.add_trace(go.Scatter(x=disp, y=us_v, name="United States",
        mode="markers", marker=dict(color=US_SAGE,size=12,symbol="circle"),
        hovertemplate="%{x}<br>U.S.: $%{y:,.0f}<extra></extra>"))
    anns = []
    if ny_all:
        fig.add_hline(y=ny_all, line_color=NY_RUST, line_dash="dash", line_width=1, opacity=0.5)
        anns.append(dict(text=f"NY Median: ${ny_all:,.0f}", xref="paper", yref="y",
            x=0.01, y=ny_all, yshift=8, font=dict(size=9,color=NY_RUST), showarrow=False))
    if us_all:
        fig.add_hline(y=us_all, line_color=US_SAGE, line_dash="dot", line_width=1, opacity=0.5)
        anns.append(dict(text=f"U.S. Median: ${us_all:,.0f}", xref="paper", yref="y",
            x=0.55, y=us_all, yshift=8, font=dict(size=9,color=US_SAGE), showarrow=False))
    anns.append(sa(f"Source: U.S. Census Bureau, {latest} 1-Year ACS", -0.26))
    lay = L(f"Median Household Income by Demographic Group — {latest}", h=460, bm=110)
    lay["xaxis"]["tickangle"]  = -25; lay["xaxis"]["title"] = ""
    lay["yaxis"]["tickprefix"]  = "$"; lay["yaxis"]["tickformat"] = ","
    lay["yaxis"]["title"]      = ax_title("Median HH Income")
    lay["annotations"]         = anns
    fig.update_layout(**lay)
    return to_html(fig, "income_demog")


# ══ BUILD ══════════════════════════════════════════════════════════════════════
def build():
    print("\nBuilding HTML page...")
    meta    = load("metadata") or {}
    updated = meta.get("last_updated_display","Unknown")

    print("  BFS..."); bfs_a, bfs_b   = chart_bfs()
    print("  GDP..."); gdp_peer       = chart_gdp_peer()
    print("  GDP industry growth..."); gdp_ind = chart_gdp_industry_growth()
    print("  GDP bar..."); gdp_bar    = chart_gdp_industry_bar()
    print("  Housing..."); housing    = chart_housing()
    print("  JOLTS..."); jolts_l, jolts_r = chart_jolts()
    print("  CES..."); ces_a, ces_b, ces_c = chart_ces()
    print("  LAUS..."); laus_a, laus_b = chart_laus()
    print("  Population..."); pop_html = chart_population()
    print("  Poverty..."); poverty    = chart_poverty()
    print("  Income..."); income_d   = chart_income()

    def section(anchor, source_label, title, *chart_htmls):
        charts = "\n".join(f'<div class="chart-wrap">{h}</div>' for h in chart_htmls if h)
        return f"""
<div class="section" id="{anchor}">
  <div class="section-subtitle">{source_label}</div>
  <h2 class="section-title">{title}</h2>
  <div class="section-divider"></div>
  {charts}
</div>"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>New York State Economic Dashboard - DRAFT - CENSUS API DOWN AS OF 11AM 4/21</title>
<script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
<style>
  :root {{
    --cream:#F7F3EE; --white:#FFFFFF; --text-dark:#2A2420;
    --text-mid:#6E6460; --text-light:#A09590; --border:#E5DDD5;
    --rust:#8B5E52; --sage:#5C7A6A;
  }}
  *{{ box-sizing:border-box; margin:0; padding:0; }}
  body{{ font-family:'Segoe UI',Arial,sans-serif; background:var(--cream); color:var(--text-dark); line-height:1.5; }}

  /* ── NAV ── */
  header{{
    background:var(--white); border-bottom:1px solid var(--border);
    padding:0 5%; display:flex; align-items:center; justify-content:space-between;
    position:sticky; top:0; z-index:100; height:56px;
  }}
  .site-title{{ font-family:Georgia,serif; font-size:1rem; font-weight:normal; color:var(--text-dark); letter-spacing:.5px; }}
  .site-title span{{ color:var(--rust); }}
  .updated{{ font-size:.72rem; color:var(--text-light); }}
  nav{{
    background:var(--white); border-bottom:1px solid var(--border);
    padding:0 5%; display:flex; flex-wrap:wrap;
    position:sticky; top:56px; z-index:99;
  }}
  nav a{{
    color:var(--text-light); text-decoration:none; font-size:.73rem;
    letter-spacing:.4px; text-transform:uppercase;
    padding:10px 14px; border-bottom:2px solid transparent; transition:all .15s;
  }}
  nav a:hover{{ color:var(--rust); border-bottom-color:var(--rust); }}

  /* ── LAYOUT ── */
  main{{ max-width:960px; margin:0 auto; padding:52px 5% 80px; }}

  /* ── SECTION ── */
  .section{{ margin-bottom:72px; }}
  .section-title{{ font-family:Georgia,serif; font-size:1.45rem; font-weight:normal; color:var(--text-dark); margin-bottom:3px; }}
  .section-subtitle{{ font-size:.72rem; color:var(--text-light); text-transform:uppercase; letter-spacing:.8px; margin-bottom:16px; }}
  .section-divider{{ width:30px; height:2px; background:var(--rust); margin-bottom:28px; opacity:.6; }}
  .chart-wrap{{ background:var(--white); border-radius:4px; padding:10px 6px 6px; margin-bottom:28px; }}
  .js-plotly-plot{{ width:100% !important; }}

  /* ── INDEX SELECTOR ── */
  .index-selector{{
    display:flex; align-items:center; gap:8px;
    padding:8px 12px 10px; background:var(--white);
    border-bottom:1px solid var(--border);
  }}
  .index-label{{
    font-size:.78rem; color:var(--text-mid);
    font-style:italic; white-space:nowrap;
  }}
  .index-select{{
    font-size:.78rem; color:var(--text-dark);
    background:var(--cream); border:1px solid var(--border);
    border-radius:3px; padding:3px 24px 3px 8px;
    appearance:none; -webkit-appearance:none;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='6'%3E%3Cpath d='M0 0l5 6 5-6z' fill='%23A09590'/%3E%3C/svg%3E");
    background-repeat:no-repeat; background-position:right 7px center;
    cursor:pointer;
  }}
  .index-select:focus{{ outline:none; border-color:var(--rust); }}

  @media(max-width:700px){{
    main{{ padding:32px 4% 60px; }}
    header,nav{{ padding:0 4%; }}
  }}
</style>
</head>
<body>
<header>
  <div class="site-title"><span>NY</span> Economic Dashboard &mdash; DRAFT &mdash; CENSUS API DOWN AS OF 11AM 4/21</div>
  <div class="updated">Updated {updated}</div>
</header>
<nav>
  <a href="#bfs">Business Formation</a>
  <a href="#gdp">GDP</a>
  <a href="#housing">Housing</a>
  <a href="#jolts">Job Openings</a>
  <a href="#ces">Employment</a>
  <a href="#laus">Labor Force</a>
  <a href="#population">Population</a>
  <a href="#poverty">Poverty</a>
  <a href="#income">Income</a>
</nav>
<main>

{section("bfs", "Census Bureau", "Business Formation Statistics", bfs_a, bfs_b)}
{section("gdp", "Bureau of Economic Analysis", "Gross Domestic Product", gdp_peer, gdp_ind, gdp_bar)}
{section("housing", "Census Bureau, American Community Survey", "Housing", housing)}
{section("jolts", "Bureau of Labor Statistics", "Job Openings &amp; Labor Turnover", jolts_l, jolts_r)}
{section("ces", "Bureau of Labor Statistics, Current Employment Statistics", "Employment by Industry", ces_a, ces_b, ces_c)}
{section("laus", "Bureau of Labor Statistics, LAUS", "Labor Force &amp; Unemployment", laus_a, laus_b)}
{section("population", "Census Bureau &amp; IRS Statistics of Income", "Population &amp; Migration", pop_html)}
{section("poverty", "Census Bureau, American Community Survey", "Poverty Demographics", poverty)}
{section("income", "Census Bureau, American Community Survey", "Median Household Income", income_d)}

</main>
<footer style="border-top:1px solid var(--border);background:var(--white);
               padding:24px 5%;text-align:center;
               font-size:.74rem;color:var(--text-light);">
  New York State Economic Dashboard &mdash;
  Data from U.S. Census Bureau, Bureau of Labor Statistics, Bureau of Economic Analysis, and IRS.
  Updated daily via GitHub Actions.
</footer>
</body>
</html>"""

    out = os.path.join(DOCS_DIR, "index.html")
    with open(out, "w", encoding="utf-8") as f: f.write(html)
    print(f"\n  ✓ {out}  ({os.path.getsize(out)//1024} KB)")

if __name__ == "__main__":
    build()
