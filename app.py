import streamlit as st
import hashlib
import hmac
import math
from datetime import datetime, timedelta
from collections import Counter

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(
    page_title="Crashtory V3.5",
    layout="wide"
)

# =====================================================================
# THEME (cyberpunk / matrix, minimalist)
# To change the accent colour, edit --neon below AND primaryColor in
# .streamlit/config.toml
# =====================================================================
THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@300;400;600;800&display=swap');

:root {
    --bg: #05080a;
    --panel: #0b1110;
    --line: #12352a;
    --neon: #00ff9c;
    --text: #b8f5d8;
    --muted: #5f7a6e;
}

/* ---------- base ---------- */
.stApp {
    background-color: var(--bg);
    background-image:
        linear-gradient(rgba(0,255,156,0.035) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,156,0.035) 1px, transparent 1px);
    background-size: 32px 32px;
    color: var(--text);
    font-family: 'JetBrains Mono', monospace;
}

/* subtle CRT scanlines */
.stApp::after {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background: repeating-linear-gradient(
        0deg,
        rgba(0,0,0,0.18) 0px,
        rgba(0,0,0,0.18) 1px,
        transparent 1px,
        transparent 3px
    );
    z-index: 9999;
}

.block-container {
    max-width: 1100px;
    padding-top: 2.5rem;
}

/* hide streamlit chrome */
#MainMenu, footer,
[data-testid="stToolbar"],
[data-testid="stDecoration"] { visibility: hidden; }
[data-testid="stHeader"] { background: transparent; }

/* ---------- hero ---------- */
.ct-hero { margin-bottom: 2.2rem; }
.ct-tag {
    color: var(--muted);
    font-size: 0.72rem;
    letter-spacing: 0.3em;
}
.ct-title {
    font-family: 'JetBrains Mono', monospace;
    font-size: 3.2rem;
    font-weight: 800;
    color: var(--neon);
    letter-spacing: 0.12em;
    line-height: 1.1;
    margin: 0.3rem 0;
    text-shadow: 0 0 8px rgba(0,255,156,0.55), 0 0 28px rgba(0,255,156,0.25);
}
.ct-sub {
    color: var(--text);
    font-size: 0.95rem;
    opacity: 0.85;
}
.ct-cursor {
    color: var(--neon);
    animation: ct-blink 1s steps(1) infinite;
}
@keyframes ct-blink { 50% { opacity: 0; } }

/* ---------- section headers ---------- */
.ct-section {
    font-family: 'JetBrains Mono', monospace;
    color: var(--neon);
    font-size: 0.85rem;
    letter-spacing: 0.25em;
    text-transform: uppercase;
    border-bottom: 1px solid var(--line);
    padding-bottom: 0.45rem;
    margin: 2rem 0 1rem 0;
}
.ct-section span { color: var(--muted); }

/* ---------- labels ---------- */
[data-testid="stWidgetLabel"] p {
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.72rem !important;
}

/* ---------- inputs ---------- */
[data-baseweb="input"],
[data-baseweb="base-input"],
[data-baseweb="select"] > div {
    background: var(--panel) !important;
    border: 1px solid var(--line) !important;
    border-radius: 2px !important;
}
[data-baseweb="input"]:focus-within,
[data-baseweb="select"] > div:focus-within {
    border-color: var(--neon) !important;
    box-shadow: 0 0 0 1px var(--neon), 0 0 12px rgba(0,255,156,0.25) !important;
}
.stTextInput input,
.stNumberInput input,
.stDateInput input {
    background: var(--panel) !important;
    color: var(--neon) !important;
    font-family: 'JetBrains Mono', monospace !important;
}

/* ---------- buttons ---------- */
.stButton > button,
.stDownloadButton > button {
    background: transparent;
    color: var(--neon);
    border: 1px solid var(--neon);
    border-radius: 2px;
    padding: 0.6rem 2.2rem;
    text-transform: uppercase;
    letter-spacing: 0.22em;
    font-weight: 600;
    transition: all 0.15s ease;
}
.stButton > button p,
.stDownloadButton > button p {
    font-family: 'JetBrains Mono', monospace;
}
.stButton > button:hover,
.stDownloadButton > button:hover,
.stButton > button:focus:not(:active) {
    background: var(--neon);
    color: var(--bg);
    border-color: var(--neon);
    box-shadow: 0 0 18px rgba(0,255,156,0.55);
}
.stButton > button:hover p,
.stDownloadButton > button:hover p { color: var(--bg) !important; }
.stButton > button:active { transform: translateY(1px); }

/* ---------- metrics ---------- */
[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--line);
    border-left: 2px solid var(--neon);
    border-radius: 2px;
    padding: 0.9rem 1rem;
}
[data-testid="stMetricLabel"] p {
    color: var(--muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 0.7rem !important;
}
[data-testid="stMetricValue"] {
    color: var(--neon) !important;
    font-family: 'JetBrains Mono', monospace;
    font-weight: 600;
    text-shadow: 0 0 10px rgba(0,255,156,0.35);
}

/* ---------- progress bar ---------- */
.stProgress > div > div > div > div {
    background: var(--neon) !important;
    box-shadow: 0 0 10px var(--neon);
}

/* ---------- alerts & tables ---------- */
[data-testid="stAlert"] {
    background: var(--panel) !important;
    border: 1px solid var(--line);
    border-radius: 2px;
}
[data-testid="stDataFrame"] {
    border: 1px solid var(--line);
    border-radius: 2px;
}

/* ---------- expander ---------- */
[data-testid="stExpander"] {
    background: var(--panel);
    border: 1px solid var(--line);
    border-radius: 2px;
}

/* ---------- scrollbar ---------- */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--line); }
::-webkit-scrollbar-thumb:hover { background: var(--neon); }

/* ---------- footer ---------- */
.ct-foot {
    color: var(--muted);
    font-size: 0.7rem;
    letter-spacing: 0.25em;
    text-align: center;
    margin-top: 3rem;
    opacity: 0.7;
}
</style>
"""

st.markdown(THEME_CSS, unsafe_allow_html=True)

# Palette for charts (matches CSS vars)
NEON = "#00ff9c"
MUTED = "#5f7a6e"
TEXT = "#b8f5d8"
PANEL = "#0b1110"
LINE = "#12352a"
AMBER = "#ffb000"
MAGENTA = "#ff2bd6"
CYAN = "#00d0ff"


def section(num, label):
    st.markdown(
        f'<div class="ct-section"><span>{num}</span> // {label}</div>',
        unsafe_allow_html=True
    )


st.markdown(
    """
    <div class="ct-hero">
        <div class="ct-tag">SYS://CRASHTORY  v3.5</div>
        <div class="ct-title">CRASHTORY</div>
        <div class="ct-sub">> stake crash history generator<span class="ct-cursor">_</span></div>
    </div>
    """,
    unsafe_allow_html=True
)

# =====================================================================
# INPUTS
# =====================================================================
section("01", "Input")

latest_hash = st.text_input("Latest Hash", placeholder="paste 64-character hash")
seed = st.text_input("Seed", placeholder="paste seed")

section("02", "Reference Time (UTC)")

col1, col2 = st.columns(2)
with col1:
    known_date = st.date_input("Date of Latest Hash")
with col2:
    known_time = st.time_input("Time of Latest Hash", step=1)

section("03", "Options")

rounds = st.number_input(
    "Number of historical outputs",
    min_value=1,
    max_value=50000,
    value=1000
)

o1, o2, o3 = st.columns(3)
with o1:
    generate_timestamps = st.checkbox("Estimated Timestamps", value=True)
with o2:
    show_hashes = st.checkbox("Show Hashes", value=False)
with o3:
    show_stats = st.checkbox("Show Statistics", value=True)

st.write("")


# =====================================================================
# CORE MATH (unchanged)
# =====================================================================
def calculate_multiplier(hash_value, seed_value):
    digest = hmac.new(
        hash_value.encode(),
        seed_value.encode(),
        hashlib.sha256
    ).hexdigest()

    value = int(digest[:8], 16)

    # Stake shows instant crashes as 1.00x, never below
    return max(1.0, ((2 ** 32) / (value + 1)) * 0.99)


# --- Duration formula ---
# Originally fitted on 3,147 real rounds across 3 days.
# DURATION_DELAY recalibrated on 1,041 matched real rounds (Nov 20-21, 2026):
# the old value drifted ~0.031s per round (-32s after 1,040 rounds).
# DURATION_K unchanged (error was constant regardless of multiplier).
DURATION_DELAY = 11.508714            # launch-pad seconds before liftoff
DURATION_K = 0.059885340656503055     # growth rate per second


def estimate_round_duration(multiplier):
    growth_time = math.log(max(multiplier, 1)) / DURATION_K
    return DURATION_DELAY + growth_time


# =====================================================================
# GENERATION
# =====================================================================
def generate_rounds(start_hash, seed_value, n_rounds, anchor_time, with_ts):
    current_hash = start_hash.strip().lower()
    current_time = anchor_time

    hashes, multipliers, times = [], [], []

    progress = st.progress(0)
    step = max(1, n_rounds // 100)

    for i in range(n_rounds):
        multiplier = calculate_multiplier(current_hash, seed_value)

        # Round 0 is the anchor; each older round steps back by its own duration
        if with_ts and i > 0:
            current_time -= timedelta(seconds=estimate_round_duration(multiplier))

        hashes.append(current_hash)
        multipliers.append(multiplier)
        times.append(current_time if with_ts else None)

        current_hash = hashlib.sha256(current_hash.encode()).hexdigest()

        if i % step == 0:
            progress.progress(min((i + 1) / n_rounds, 1.0))

    progress.progress(1.0)
    return hashes, multipliers, times, current_time


# =====================================================================
# INDICATORS
# =====================================================================
OVERLAY_OPTIONS = [
    "Rolling Median",
    "SMA (geometric)",
    "EMA (log)",
    "Bollinger Bands (log)",
    "Target Line",
]

PANEL_HIT = "Hit Rate vs Expected"
PANEL_DROUGHT = "Drought (rounds since target)"
PANEL_Z = "Hit Z-Score"
PANEL_RSI = "RSI (log multiplier)"
PANEL_OPTIONS = [PANEL_HIT, PANEL_DROUGHT, PANEL_Z, PANEL_RSI]


def expected_hit_prob(target):
    # From the formula: P(m >= x) ≈ 0.99 / x
    return min(1.0, 0.99 / target)


def drought_quantile(pe, q):
    """Drought length k such that P(drought >= k) <= 1 - q."""
    if pe >= 1:
        return 0
    return math.ceil(math.log(1 - q) / math.log(1 - pe))


def expected_longest_drought(n, pe):
    """Approximate expected longest run of misses in n rounds."""
    if pe >= 1 or n * pe <= 1:
        return 0
    return math.log(n * pe) / -math.log(1 - pe)


def compute_indicators(chrono, target, pe, prm):
    out = chrono.copy()
    m = out["mult"]
    lm = np.log(m)  # log space: multipliers are heavy-tailed

    # Overlays
    out["sma_geo"] = np.exp(lm.rolling(prm["ma"]).mean())
    out["ema_log"] = np.exp(lm.ewm(span=prm["ma"], adjust=False).mean())
    out["median"] = m.rolling(prm["ma"]).median()

    mid = lm.rolling(prm["bb"]).mean()
    sd = lm.rolling(prm["bb"]).std()
    out["bb_mid"] = np.exp(mid)
    out["bb_up"] = np.exp(mid + prm["bb_k"] * sd)
    out["bb_lo"] = np.exp(mid - prm["bb_k"] * sd)

    # RSI (Wilder) on log multiplier
    d = lm.diff()
    gain = d.clip(lower=0).ewm(alpha=1 / prm["rsi"], adjust=False).mean()
    loss = (-d.clip(upper=0)).ewm(alpha=1 / prm["rsi"], adjust=False).mean()
    out["rsi"] = 100 - 100 / (1 + gain / loss)

    # Hit-based indicators
    hits = (m >= target).astype(float)
    w = prm["hit"]
    out["hit_rate"] = hits.rolling(w).mean() * 100
    out["hit_z"] = (hits.rolling(w).sum() - w * pe) / math.sqrt(w * pe * (1 - pe))

    # Rounds since last hit (0 on a hit round)
    grp = hits.cumsum()
    drought = hits.groupby(grp).cumcount()
    drought[grp == 0] += 1  # misses before the very first hit
    out["drought"] = drought

    return out


def build_figure(view, overlays, panels, target, pe, prm, log_y, connect, has_ts):
    x = view["time"] if has_ts else view["round"]

    rows = 1 + len(panels)
    heights = ([0.5] + [0.5 / len(panels)] * len(panels)) if panels else [1.0]

    fig = make_subplots(
        rows=rows,
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.04,
        row_heights=heights,
        subplot_titles=["MULTIPLIER"] + [p.upper() for p in panels],
    )
    # Style subplot titles before adding any line annotations
    fig.update_annotations(font=dict(color=MUTED, size=10))

    # ---------- main series ----------
    hit_mask = (view["mult"] >= target).to_numpy()
    fig.add_trace(
        go.Scattergl(
            x=x,
            y=view["mult"],
            mode="lines+markers" if connect else "markers",
            marker=dict(size=4, color=np.where(hit_mask, NEON, MUTED)),
            line=dict(width=0.6, color="rgba(95,122,110,0.4)"),
            customdata=view["round"],
            hovertemplate="Round %{customdata}<br>%{y:.2f}x<extra></extra>",
            name="Multiplier",
        ),
        row=1, col=1,
    )

    # ---------- overlays ----------
    def overlay_line(y, name, color, dash=None, width=1.3):
        fig.add_trace(
            go.Scattergl(
                x=x, y=y, mode="lines", name=name,
                line=dict(color=color, width=width, dash=dash),
                hovertemplate=f"{name}: %{{y:.2f}}x<extra></extra>",
            ),
            row=1, col=1,
        )

    if "Bollinger Bands (log)" in overlays:
        fig.add_trace(
            go.Scattergl(
                x=x, y=view["bb_up"], mode="lines", name="BB upper",
                line=dict(color=CYAN, width=1), hoverinfo="skip",
            ),
            row=1, col=1,
        )
        fig.add_trace(
            go.Scattergl(
                x=x, y=view["bb_lo"], mode="lines", name="BB lower",
                line=dict(color=CYAN, width=1), fill="tonexty",
                fillcolor="rgba(0,208,255,0.07)", hoverinfo="skip",
            ),
            row=1, col=1,
        )
        overlay_line(view["bb_mid"], "BB mid", CYAN, dash="dot", width=1)

    if "SMA (geometric)" in overlays:
        overlay_line(view["sma_geo"], f"SMA{prm['ma']} (geo)", AMBER)

    if "EMA (log)" in overlays:
        overlay_line(view["ema_log"], f"EMA{prm['ma']} (log)", MAGENTA)

    if "Rolling Median" in overlays:
        overlay_line(view["median"], f"Median{prm['ma']}", TEXT)

    if "Target Line" in overlays:
        # Drawn as a trace (not a shape) so it behaves correctly on log axes
        overlay_line(
            np.full(len(view), target),
            f"Target {target:.2f}x",
            AMBER, dash="dash", width=1,
        )

    # ---------- indicator panels ----------
    for r, name in enumerate(panels, start=2):

        if name == PANEL_HIT:
            band = prm["z"] * math.sqrt(pe * (1 - pe) / prm["hit"]) * 100
            fig.add_hrect(
                y0=max(0, pe * 100 - band), y1=min(100, pe * 100 + band),
                fillcolor=NEON, opacity=0.07, line_width=0, row=r, col=1,
            )
            fig.add_hline(
                y=pe * 100, line=dict(color=AMBER, dash="dash", width=1),
                annotation_text=f"expected {pe * 100:.2f}%",
                annotation_font=dict(color=AMBER, size=10),
                annotation_position="top left", row=r, col=1,
            )
            fig.add_trace(
                go.Scattergl(
                    x=x, y=view["hit_rate"], mode="lines",
                    name=f"Hit% ≥{target:.2f}x ({prm['hit']})",
                    line=dict(color=NEON, width=1.2),
                    hovertemplate="Hit rate: %{y:.2f}%<extra></extra>",
                ),
                row=r, col=1,
            )

        elif name == PANEL_DROUGHT:
            for q, lbl in [(0.5, "p50"), (0.95, "p95"), (0.99, "p99")]:
                k = drought_quantile(pe, q)
                fig.add_hline(
                    y=k, line=dict(color=MUTED, dash="dot", width=1),
                    annotation_text=f"{lbl} = {k}",
                    annotation_font=dict(color=MUTED, size=10),
                    annotation_position="top left", row=r, col=1,
                )
            fig.add_trace(
                go.Scattergl(
                    x=x, y=view["drought"], mode="lines",
                    name="Drought", line=dict(color=MAGENTA, width=1),
                    hovertemplate="Rounds since ≥target: %{y}<extra></extra>",
                ),
                row=r, col=1,
            )

        elif name == PANEL_Z:
            fig.add_hrect(
                y0=-prm["z"], y1=prm["z"], fillcolor=NEON, opacity=0.07,
                line_width=0, row=r, col=1,
            )
            fig.add_hline(y=0, line=dict(color=MUTED, width=1), row=r, col=1)
            fig.add_trace(
                go.Scattergl(
                    x=x, y=view["hit_z"], mode="lines",
                    name=f"Hit Z ({prm['hit']})", line=dict(color=CYAN, width=1.2),
                    hovertemplate="Z: %{y:.2f}<extra></extra>",
                ),
                row=r, col=1,
            )

        elif name == PANEL_RSI:
            for lvl in (30, 70):
                fig.add_hline(
                    y=lvl, line=dict(color=MUTED, dash="dot", width=1),
                    row=r, col=1,
                )
            fig.add_trace(
                go.Scattergl(
                    x=x, y=view["rsi"], mode="lines",
                    name=f"RSI{prm['rsi']}", line=dict(color=AMBER, width=1.2),
                    hovertemplate="RSI: %{y:.1f}<extra></extra>",
                ),
                row=r, col=1,
            )
            fig.update_yaxes(range=[0, 100], row=r, col=1)

    # ---------- layout ----------
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=PANEL,
        font=dict(family="JetBrains Mono, monospace", color=TEXT, size=11),
        height=440 + 170 * len(panels),
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation="h", y=1.02, x=0, yanchor="bottom",
            bgcolor="rgba(0,0,0,0)", font=dict(size=10),
        ),
        hovermode="closest",
    )
    fig.update_xaxes(
        gridcolor=LINE, zeroline=False,
        showspikes=True, spikemode="across",
        spikecolor=MUTED, spikethickness=1,
    )
    fig.update_yaxes(gridcolor=LINE, zeroline=False)

    if log_y:
        fig.update_yaxes(type="log", row=1, col=1)

    if not has_ts:
        # Round 1 = newest, keep newest on the right
        fig.update_xaxes(autorange="reversed")

    return fig


def render_chart_section(multipliers, times, has_ts):
    n = len(multipliers)

    c1, c2, c3 = st.columns(3)
    with c1:
        plot_n = st.number_input(
            "Rounds to plot (most recent)",
            min_value=1, max_value=n, value=min(n, 1050),
            help="How many of the newest rounds to show on the chart.",
        )
    with c2:
        target = st.number_input(
            "Target multiplier",
            min_value=1.01, max_value=1_000_000.0,
            value=2.0, step=0.5, format="%.2f",
            help="The cash-out point you care about. Green dots = rounds that reached it.",
        )
    with c3:
        log_y = st.checkbox(
            "Log scale (Y)", value=True,
            help="Stretches the Y axis so huge rounds don't squash everything else.",
        )
        connect = st.checkbox("Connect points", value=False)

    overlays = st.multiselect(
        "Overlays (main chart)",
        OVERLAY_OPTIONS,
        default=["Rolling Median", "Target Line"],
        help=(
            "Smoothing lines drawn over the dots. "
            "Rolling Median is the easiest to read: the 'typical' recent round."
        ),
    )
    panels = st.multiselect(
        "Indicator panels",
        PANEL_OPTIONS,
        default=[PANEL_HIT, PANEL_DROUGHT],
        help=(
            "Extra charts under the main one. Hit Rate and Drought are the most useful. "
            "Shaded bands = normal luck."
        ),
    )

    with st.expander("Indicator parameters"):
        p1, p2, p3 = st.columns(3)
        with p1:
            ma = st.number_input(
                "MA / Median window", 2, 5000, 50,
                help="How many recent rounds the smoothing lines look back at.",
            )
            rsi_p = st.number_input("RSI period", 2, 500, 14)
        with p2:
            bb = st.number_input("Bollinger window", 2, 5000, 50)
            bb_k = st.number_input("Bollinger σ", 0.5, 5.0, 2.0, step=0.5)
        with p3:
            hit_w = st.number_input(
                "Hit-rate / Z window", 5, 10000, 100,
                help="How many recent rounds the hit-rate is measured over.",
            )
            z = st.number_input(
                "Noise band (± z)", 0.5, 5.0, 2.0, step=0.5,
                help="Width of the shaded 'normal luck' zone. Leave at 2.",
            )

    prm = dict(ma=int(ma), rsi=int(rsi_p), bb=int(bb), bb_k=bb_k, hit=int(hit_w), z=z)
    pe = expected_hit_prob(target)

    # Chronological order (oldest -> newest). Indicators are computed on the
    # FULL history, then sliced, so the plotted window has no warm-up gap.
    chrono = pd.DataFrame({
        "round": np.arange(n, 0, -1),
        "mult": np.array(multipliers[::-1], dtype=float),
    })
    if has_ts:
        chrono["time"] = pd.to_datetime(times[::-1])

    ind = compute_indicators(chrono, target, pe, prm)
    view = ind.iloc[-int(plot_n):]

    # ---------- summary metrics ----------
    obs = (view["mult"] >= target).mean() * 100
    longest = int(view["drought"].max())
    exp_long = expected_longest_drought(len(view), pe)

    lm_full = pd.Series(np.log(chrono["mult"]))
    ac = lm_full.autocorr(lag=1) if n > 2 else float("nan")
    ac_band = 2 / math.sqrt(n) if n > 0 else float("nan")

    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric(
            f"Hit ≥{target:.2f}x (view)",
            f"{obs:.2f}%",
            f"{obs - pe * 100:+.2f} vs exp {pe * 100:.2f}%",
            delta_color="off",
            help="Share of plotted rounds that reached your target, vs what the math expects.",
        )
    with m2:
        st.metric(
            "Current Drought",
            f"{int(view['drought'].iloc[-1])}",
            f"p95 = {drought_quantile(pe, 0.95)}",
            delta_color="off",
            help="Misses in a row right now. A long drought does NOT make a hit 'due'.",
        )
    with m3:
        st.metric(
            "Longest Drought (view)",
            f"{longest}",
            f"expected ≈ {exp_long:.0f}",
            delta_color="off",
            help="Worst losing streak in the chart vs how long the worst streak normally is.",
        )
    with m4:
        st.metric(
            "Lag-1 Autocorr (log)",
            f"{ac:+.4f}",
            f"noise band ±{ac_band:.4f}",
            delta_color="off",
            help="Tests whether one round affects the next. Inside the band = no connection.",
        )

    fig = build_figure(view, overlays, panels, target, pe, prm, log_y, connect, has_ts)
    st.plotly_chart(
        fig,
        config={"displaylogo": False, "scrollZoom": True},
    )

    st.caption(
        "Bands show the range normal randomness produces. "
        "Values inside them are noise; values outside happen occasionally by chance. "
        "Rounds are independent, so no indicator predicts the next round."
    )


# =====================================================================
# GENERATE -> store in session_state so widget changes don't wipe results
# =====================================================================
if st.button("Generate"):

    if not latest_hash.strip():
        st.error("Latest hash is required.")
        st.stop()

    if not seed.strip():
        st.error("Seed is required.")
        st.stop()

    parsed_timestamp = datetime.combine(known_date, known_time)

    hashes, multipliers, times, earliest = generate_rounds(
        latest_hash, seed, int(rounds), parsed_timestamp, generate_timestamps
    )

    st.session_state["results"] = dict(
        hashes=hashes,
        multipliers=multipliers,
        times=times,
        has_ts=generate_timestamps,
        anchor=parsed_timestamp,
        earliest=earliest,
    )


# =====================================================================
# RENDER RESULTS
# =====================================================================
res = st.session_state.get("results")

if res:
    multipliers = res["multipliers"]
    times = res["times"]
    has_ts = res["has_ts"]
    n = len(multipliers)

    df = pd.DataFrame({
        "Round": range(1, n + 1),
        "Timestamp": [
            t.strftime("%Y-%m-%d %H:%M:%S") if t is not None else ""
            for t in times
        ],
        "Hash": res["hashes"],
        "Multiplier": [f"{int(m * 100) / 100:.2f}x" for m in multipliers],
    })

    if not show_hashes:
        df = df.drop(columns=["Hash"])

    def color_multiplier(val):
        num = float(str(val).replace("x", ""))
        if num >= 2:
            return "color: #00ff9c; font-weight: bold;"
        return "color: #5f7a6e;"

    styled_df = df.style.map(color_multiplier, subset=["Multiplier"])

    st.success(f"> {n:,} rounds generated")

    if show_stats:
        section("04", "Statistics")

        avg_multiplier = sum(multipliers) / n
        highest_multiplier = max(multipliers)
        median_multiplier = sorted(multipliers)[n // 2]
        hit_2x = sum(1 for x in multipliers if x >= 2)
        hit_10x = sum(1 for x in multipliers if x >= 10)
        hit_100x = sum(1 for x in multipliers if x >= 100)

        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Average Multiplier", f"{avg_multiplier:.2f}x")
            st.metric("Median Multiplier", f"{median_multiplier:.2f}x")
        with c2:
            st.metric("Highest Multiplier", f"{highest_multiplier:.2f}x")
            st.metric("Hit Rate ≥2x", f"{hit_2x / n * 100:.2f}%")
        with c3:
            st.metric("Hit Rate ≥10x", f"{hit_10x / n * 100:.2f}%")
            st.metric("Hit Rate ≥100x", f"{hit_100x / n * 100:.2f}%")

        section("05", "< 2x Streak Analysis")

        streaks = []
        current_streak = 0
        for value in multipliers:
            if value < 2:
                current_streak += 1
            else:
                if current_streak > 0:
                    streaks.append(current_streak)
                current_streak = 0
        if current_streak > 0:
            streaks.append(current_streak)

        if streaks:
            streak_df = pd.DataFrame(
                sorted(Counter(streaks).items()),
                columns=["Streak Length", "Occurrences"],
            )
            s1, s2 = st.columns([3, 1])
            with s1:
                st.dataframe(streak_df, use_container_width=True, hide_index=True)
            with s2:
                st.metric("Maximum <2x Streak", max(streaks))

        if has_ts:
            section("06", "Timeline")
            span = res["anchor"] - res["earliest"]
            t1, t2, t3 = st.columns(3)
            with t1:
                st.metric("Latest Timestamp", res["anchor"].strftime("%Y-%m-%d %H:%M"))
            with t2:
                st.metric("Earliest Estimate", res["earliest"].strftime("%Y-%m-%d %H:%M"))
            with t3:
                st.metric("Estimated Timespan", str(span).split(".")[0])

    section("07", "Chart & Indicators")
    render_chart_section(multipliers, times, has_ts)

    section("08", "Historical Outputs")
    st.write(styled_df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV", csv, "crashtory_v3_5.csv", "text/csv")

st.markdown(
    '<div class="ct-foot">CRASHTORY // END OF LINE</div>',
    unsafe_allow_html=True
)
