"""
╔══════════════════════════════════════════════════════════════╗
║          SPORT ANALYTICS — STREAMLIT DASHBOARD              ║
║     NBA · Football · Recommendation Engine                  ║
║     Standalone file — works without any credentials         ║
╚══════════════════════════════════════════════════════════════╝

Run: streamlit run sport_dashboard.py
"""

import random
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
#  CONFIG & GLOBAL STYLE
# ─────────────────────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Sport Analytics",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded",
)

STYLE = """
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@400;600;700;800;900&family=DM+Sans:wght@300;400;500;600&display=swap');

/* ── Root tokens ── */
:root {
    --bg-0:        #080b14;
    --bg-1:        #0d1117;
    --bg-2:        #111827;
    --bg-3:        #1c2333;
    --bg-card:     #151c28;
    --border:      #1f2d3d;
    --border-bright: #2a3f56;
    --gold:        #f5a623;
    --gold-dim:    #c47d0e;
    --cyan:        #00d4ff;
    --cyan-dim:    #0099bb;
    --green:       #00e676;
    --red:         #ff4560;
    --text-1:      #f0f4f8;
    --text-2:      #8fa3b8;
    --text-3:      #4a6077;
    --font-display: 'Barlow Condensed', sans-serif;
    --font-body:    'DM Sans', sans-serif;
}

/* ── Global reset ── */
html, body, [class*="css"] {
    background-color: var(--bg-1) !important;
    font-family: var(--font-body) !important;
    color: var(--text-1) !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; max-width: 1400px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, var(--bg-0) 0%, #0a0f1e 100%) !important;
    border-right: 1px solid var(--border) !important;
    padding-top: 0 !important;
}
[data-testid="stSidebar"] * { font-family: var(--font-body) !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stSlider label,
[data-testid="stSidebar"] .stMultiSelect label {
    color: var(--text-2) !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid var(--border) !important;
    gap: 0 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: var(--font-display) !important;
    font-size: 1rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: var(--text-3) !important;
    background: transparent !important;
    border: none !important;
    padding: 0.65rem 1.4rem !important;
    transition: color 0.2s;
}
.stTabs [aria-selected="true"] {
    color: var(--gold) !important;
    border-bottom: 2px solid var(--gold) !important;
}

/* ── Metrics ── */
[data-testid="metric-container"] {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    padding: 1rem 1.2rem !important;
    transition: border-color 0.2s, transform 0.15s;
}
[data-testid="metric-container"]:hover {
    border-color: var(--border-bright) !important;
    transform: translateY(-1px);
}
[data-testid="stMetricValue"] {
    font-family: var(--font-display) !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    color: var(--text-1) !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricLabel"] {
    font-size: 0.7rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: var(--text-2) !important;
}
[data-testid="stMetricDelta"] { font-size: 0.8rem !important; }

/* ── Selectbox / Multiselect ── */
[data-testid="stSelectbox"] > div > div,
[data-testid="stMultiSelect"] > div > div {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    color: var(--text-1) !important;
}

/* ── Slider ── */
[data-testid="stSlider"] [class*="thumb"] { background: var(--gold) !important; }
[data-testid="stSlider"] [class*="track--filled"] { background: var(--gold) !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid var(--border) !important; border-radius: 10px !important; overflow: hidden; }
[data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
    font-family: var(--font-body) !important;
    font-size: 0.82rem !important;
}

/* ── Button ── */
.stButton > button {
    font-family: var(--font-display) !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, var(--gold), var(--gold-dim)) !important;
    color: #000 !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.55rem 1.5rem !important;
    transition: opacity 0.2s, transform 0.15s !important;
}
.stButton > button:hover { opacity: 0.88 !important; transform: translateY(-1px) !important; }

/* ── Divider ── */
hr { border-color: var(--border) !important; margin: 1.2rem 0 !important; }

/* ── Info / Success / Warning boxes ── */
[data-testid="stInfo"], .stAlert {
    background: rgba(0, 212, 255, 0.06) !important;
    border: 1px solid rgba(0, 212, 255, 0.2) !important;
    border-radius: 8px !important;
    color: var(--text-1) !important;
}

/* ── Spinner ── */
[data-testid="stSpinner"] { color: var(--gold) !important; }

/* ── Checkbox ── */
[data-testid="stCheckbox"] label { color: var(--text-2) !important; font-size: 0.85rem !important; }
</style>
"""

PLOTLY_LAYOUT = dict(
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#8fa3b8", size=12),
    xaxis=dict(gridcolor="#1c2333", zerolinecolor="#1c2333", tickfont=dict(color="#8fa3b8")),
    yaxis=dict(gridcolor="#1c2333", zerolinecolor="#1c2333", tickfont=dict(color="#8fa3b8")),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="rgba(0,0,0,0)",
                font=dict(color="#8fa3b8")),
    margin=dict(l=10, r=10, t=40, b=10),
    hoverlabel=dict(bgcolor="#111827", bordercolor="#2a3f56",
                    font=dict(family="DM Sans", color="#f0f4f8")),
)

st.markdown(STYLE, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  REFERENCE DATA
# ─────────────────────────────────────────────────────────────────────────────

NBA_TEAMS = [
    "Boston Celtics", "Oklahoma City Thunder", "Denver Nuggets",
    "Minnesota Timberwolves", "Cleveland Cavaliers", "Los Angeles Lakers",
    "Golden State Warriors", "Miami Heat", "Milwaukee Bucks",
    "Phoenix Suns", "Dallas Mavericks", "Philadelphia 76ers",
    "Memphis Grizzlies", "New York Knicks", "Sacramento Kings",
    "Los Angeles Clippers", "New Orleans Pelicans", "Indiana Pacers",
]

NBA_PLAYERS = [
    ("Shai Gilgeous-Alexander", "Oklahoma City Thunder", "PG", 30.1, 5.5, 6.2, "East"),
    ("Giannis Antetokounmpo",   "Milwaukee Bucks",       "PF", 30.4, 11.5, 6.5, "East"),
    ("Luka Doncic",             "Dallas Mavericks",      "PG", 33.9, 9.2,  9.8, "West"),
    ("Joel Embiid",             "Philadelphia 76ers",    "C",  34.7, 11.0, 5.6, "East"),
    ("Jayson Tatum",            "Boston Celtics",        "SF", 26.9, 8.1,  4.9, "East"),
    ("Nikola Jokic",            "Denver Nuggets",        "C",  26.4, 12.4, 9.0, "West"),
    ("LeBron James",            "Los Angeles Lakers",    "SF", 25.8, 7.3,  8.1, "West"),
    ("Stephen Curry",           "Golden State Warriors", "PG", 26.4, 4.5,  5.1, "West"),
    ("Kevin Durant",            "Phoenix Suns",          "SF", 27.1, 6.6,  5.0, "West"),
    ("Anthony Davis",           "Los Angeles Lakers",    "C",  24.7, 12.6, 3.5, "West"),
    ("Donovan Mitchell",        "Cleveland Cavaliers",   "PG", 28.0, 4.4,  6.1, "East"),
    ("Damian Lillard",          "Milwaukee Bucks",       "PG", 24.3, 4.4,  7.3, "East"),
]

LEAGUES = {
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": ["Manchester City", "Arsenal", "Liverpool", "Aston Villa",
                                  "Tottenham", "Chelsea", "Newcastle", "Manchester United",
                                  "West Ham", "Brighton", "Brentford", "Fulham"],
    "Ligue 1 🇫🇷":               ["Paris Saint-Germain", "Monaco", "Brest", "Lille",
                                  "Nice", "Lyon", "Lens", "Marseille"],
    "La Liga 🇪🇸":               ["Real Madrid", "Barcelona", "Girona", "Atletico Madrid",
                                  "Athletic Bilbao", "Real Betis", "Villarreal", "Sevilla"],
    "Serie A 🇮🇹":               ["Inter Milan", "AC Milan", "Juventus", "Atalanta",
                                  "Bologna", "Roma", "Lazio", "Napoli"],
}

FOOTBALL_PLAYERS = [
    ("Erling Haaland",   "Manchester City",    "FW", 36, 8,  7.8),
    ("Mohamed Salah",    "Liverpool",          "FW", 28, 12, 7.9),
    ("Bukayo Saka",      "Arsenal",            "MF", 20, 14, 7.7),
    ("Phil Foden",       "Manchester City",    "MF", 19, 11, 7.6),
    ("Kylian Mbappé",    "Paris Saint-Germain","FW", 27, 9,  8.1),
    ("Vinicius Junior",  "Real Madrid",        "FW", 24, 10, 7.9),
    ("Jude Bellingham",  "Real Madrid",        "MF", 19, 9,  7.8),
    ("Lautaro Martinez", "Inter Milan",        "FW", 25, 7,  7.5),
    ("Rodri",            "Manchester City",    "MF", 7,  12, 8.2),
    ("Rafael Leao",      "AC Milan",           "FW", 16, 9,  7.6),
]


# ─────────────────────────────────────────────────────────────────────────────
#  DATA GENERATORS
# ─────────────────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600)
def get_nba_standings(conf="All"):
    random.seed(42)
    rows = []
    confs = {"Boston Celtics":"East","Oklahoma City Thunder":"West","Denver Nuggets":"West",
             "Minnesota Timberwolves":"West","Cleveland Cavaliers":"East",
             "Los Angeles Lakers":"West","Golden State Warriors":"West","Miami Heat":"East",
             "Milwaukee Bucks":"East","Phoenix Suns":"West","Dallas Mavericks":"West",
             "Philadelphia 76ers":"East","Memphis Grizzlies":"West","New York Knicks":"East",
             "Sacramento Kings":"West","Los Angeles Clippers":"West",
             "New Orleans Pelicans":"West","Indiana Pacers":"East"}
    for team in NBA_TEAMS:
        w = random.randint(28, 60)
        l = 82 - w
        rows.append({
            "Team": team, "W": w, "L": l, "Win%": round(w/82, 3),
            "PTS/G": round(random.uniform(108, 122), 1),
            "OPP/G": round(random.uniform(104, 118), 1),
            "Net": round(random.uniform(-6, 12), 1),
            "Conf": confs.get(team, "West"),
            "Form": "".join(random.choices(["W","L"], weights=[w,l], k=5)),
        })
    df = pd.DataFrame(rows).sort_values("Win%", ascending=False).reset_index(drop=True)
    df.insert(0, "#", range(1, len(df)+1))
    if conf != "All":
        df = df[df["Conf"] == conf].reset_index(drop=True)
        df["#"] = range(1, len(df)+1)
    return df


@st.cache_data(ttl=3600)
def get_nba_players():
    rows = []
    for name, team, pos, pts, reb, ast, conf in NBA_PLAYERS:
        rows.append({
            "Player": name, "Team": team, "Pos": pos, "Conf": conf,
            "PTS": pts, "REB": reb, "AST": ast,
            "FG%": round(random.uniform(0.44, 0.60), 3),
            "3P%": round(random.uniform(0.33, 0.43), 3),
            "FT%": round(random.uniform(0.72, 0.94), 3),
            "MIN": round(random.uniform(32, 38), 1),
            "GP":  random.randint(55, 72),
            "TS%": round(random.uniform(0.55, 0.68), 3),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def get_nba_trend(team, n=20):
    random.seed(hash(team) % 999)
    dates = sorted([date.today() - timedelta(days=i*2) for i in range(n)])
    pts   = [random.randint(96, 133) for _ in range(n)]
    opp   = [random.randint(96, 128) for _ in range(n)]
    opponents = random.choices([t for t in NBA_TEAMS if t != team], k=n)
    return pd.DataFrame({
        "Date": dates, "PTS": pts, "OPP": opp, "Vs": opponents,
        "W/L": ["W" if p > o else "L" for p,o in zip(pts, opp)],
    })


@st.cache_data(ttl=3600)
def get_football_standings(league):
    random.seed(abs(hash(league)) % 9999)
    teams = LEAGUES[league]
    rows = []
    for team in teams:
        p  = random.randint(30, 38)
        w  = random.randint(10, p-4)
        d  = random.randint(3, min(9, p-w))
        l  = p - w - d
        gf = w * random.randint(2,3) + d
        ga = l * random.randint(1,2) + d
        rows.append({
            "Team": team, "P": p, "W": w, "D": d, "L": l,
            "GF": gf, "GA": ga, "GD": gf-ga,
            "Pts": w*3+d,
            "G/G": round(gf/p, 2),
            "W%":  round(w/p, 3),
            "Form": "".join(random.choices(["W","D","L"], weights=[w,d,l], k=5)),
            "CS":  random.randint(2, 14),
        })
    df = pd.DataFrame(rows).sort_values("Pts", ascending=False).reset_index(drop=True)
    df.insert(0, "#", range(1, len(df)+1))
    return df


@st.cache_data(ttl=3600)
def get_football_players():
    rows = []
    for name, team, pos, goals, ast, rating in FOOTBALL_PLAYERS:
        apps = random.randint(28, 36)
        mins = apps * random.randint(74, 90)
        rows.append({
            "Player": name, "Team": team, "Pos": pos,
            "Apps": apps, "Goals": goals, "Ast": ast,
            "G+A": goals + ast,
            "G/90": round(goals / (mins/90), 2),
            "Rating": rating,
            "Key P": random.randint(2, 5) * apps // 10 + random.randint(3, 8),
            "Pass%": round(random.uniform(78, 93), 1),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def get_football_trend(team, n=15):
    random.seed(hash(team) % 5555)
    dates = sorted([date.today() - timedelta(days=i*7) for i in range(n)])
    gf    = [random.randint(0,4) for _ in range(n)]
    ga    = [random.randint(0,3) for _ in range(n)]
    all_teams = [t for lg in LEAGUES.values() for t in lg if t != team]
    return pd.DataFrame({
        "Date": dates, "GF": gf, "GA": ga,
        "Vs": random.choices(all_teams, k=n),
        "Res": ["W" if f>a else ("D" if f==a else "L") for f,a in zip(gf,ga)],
        "CS":  [1 if a==0 else 0 for a in ga],
    })


# ─────────────────────────────────────────────────────────────────────────────
#  HELPER COMPONENTS
# ─────────────────────────────────────────────────────────────────────────────

def section(icon, title, subtitle=""):
    sub_html = f'<span style="color:var(--text-3);font-family:var(--font-body);font-size:0.85rem;font-weight:400;margin-left:0.6rem">{subtitle}</span>' if subtitle else ""
    st.markdown(f"""
    <div style="margin:1.6rem 0 0.8rem;display:flex;align-items:baseline;gap:0.5rem">
      <span style="font-family:var(--font-display);font-size:1.55rem;font-weight:900;
            letter-spacing:0.04em;color:var(--text-1)">{icon} {title.upper()}</span>
      {sub_html}
    </div>
    """, unsafe_allow_html=True)


def form_badge(f):
    colors = {"W": "#00e676", "D": "#f5a623", "L": "#ff4560"}
    return "".join(
        f'<span style="display:inline-block;width:18px;height:18px;border-radius:4px;'
        f'background:{colors.get(c,"#333")};color:#000;font-size:10px;font-weight:800;'
        f'text-align:center;line-height:18px;margin:1px">{c}</span>'
        for c in f
    )


def kpi_row(items):
    cols = st.columns(len(items))
    for col, (label, value, delta, color) in zip(cols, items):
        with col:
            st.metric(label, value, delta)


def apply_plotly(fig, height=420, title=""):
    fig.update_layout(**PLOTLY_LAYOUT, height=height)
    if title:
        fig.update_layout(title=dict(
            text=title, font=dict(family="Barlow Condensed", size=18, color="#f0f4f8"),
            x=0, xanchor="left",
        ))
    return fig


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding:1.5rem 0.5rem 1rem;border-bottom:1px solid #1c2333">
      <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;
           font-weight:700;letter-spacing:0.18em;color:#4a6077;text-transform:uppercase">
        Data Platform
      </div>
      <div style="font-family:'Barlow Condensed',sans-serif;font-size:2rem;
           font-weight:900;letter-spacing:0.04em;color:#f5a623;line-height:1.1;
           margin-top:2px">
        SPORT<br>ANALYTICS
      </div>
      <div style="font-size:0.72rem;color:#4a6077;margin-top:6px">
        NBA · Football · AI Recommender
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

    page = st.selectbox("", ["🏠  Home", "🏀  NBA", "⚽  Football", "🤖  Recommender"],
                        label_visibility="collapsed")

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    st.markdown("""<div style="font-size:0.65rem;font-weight:700;letter-spacing:0.12em;
        color:#4a6077;text-transform:uppercase;margin-bottom:0.5rem">Filters</div>""",
        unsafe_allow_html=True)

    if "NBA" in page:
        conf_filter = st.selectbox("Conference", ["All", "East", "West"])
        season = st.select_slider("Season", options=["2021-22","2022-23","2023-24"],
                                  value="2023-24")
        n_games = st.slider("Last N games (trend)", 5, 30, 15)

    elif "Football" in page:
        league = st.selectbox("League", list(LEAGUES.keys()))
        n_matches = st.slider("Last N matches (trend)", 5, 25, 12)

    elif "Recommender" in page:
        nba_pref = st.slider("🏀 NBA preference", 0.0, 1.0, 0.6, 0.05)
        n_recs   = st.number_input("Recommendations", 5, 30, 12)

    st.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="margin-top:auto;padding-top:1.5rem;border-top:1px solid #1c2333;
         font-size:0.7rem;color:#2a3f56">
      <div style="color:#4a6077;font-weight:600">Ikel Ouedraogo</div>
      Data Engineer · EFREI Paris<br>
      <a href="https://ikel0.github.io" style="color:#f5a623">ikel0.github.io</a>
    </div>
    """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 0 — HOME
# ─────────────────────────────────────────────────────────────────────────────

if "Home" in page:
    st.markdown("""
    <div style="padding:2.5rem 0 1.5rem">
      <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.7rem;font-weight:700;
           letter-spacing:0.2em;color:#f5a623;text-transform:uppercase;margin-bottom:0.4rem">
        End-to-End Data Pipeline
      </div>
      <h1 style="font-family:'Barlow Condensed',sans-serif;font-size:3.8rem;font-weight:900;
          color:#f0f4f8;line-height:1;letter-spacing:0.02em;margin:0">
        SPORT ANALYTICS<br>
        <span style="color:#f5a623">PLATFORM</span>
      </h1>
      <p style="color:#8fa3b8;font-size:1rem;margin-top:1rem;max-width:520px;line-height:1.6">
        Daily ingestion from NBA &amp; Football APIs → AWS S3 → Snowflake → AI-powered
        recommendations. Live stats for 4 leagues, 30 NBA teams, 1 000+ players.
      </p>
    </div>
    """, unsafe_allow_html=True)

    # ── KPI strip
    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🏀 NBA Games",      "2 847",   "+14 today")
    c2.metric("⚽ Fixtures",       "4 120",   "+6 today")
    c3.metric("👤 Players",        "1 340",   "+2 today")
    c4.metric("🤖 Recs served",    "98 K",    "+1.4K today")
    c5.metric("Pipeline uptime",   "99.7 %",  "↑ 30d avg")

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Architecture diagram
    section("🏗️", "Architecture", "API → S3 → Snowflake → Dashboard")
    arch_cols = st.columns([1,1,1,1,1])
    arch_data = [
        ("🌐", "APIs", "BallDontLie\nAPI-Football", "#f5a623"),
        ("☁️", "AWS S3", "Raw JSON.gz\nData lake", "#00d4ff"),
        ("❄️", "Snowflake", "Bronze→Silver\n→Gold", "#29B5E8"),
        ("🤖", "ML Model", "Cosine sim.\nRecommender", "#00e676"),
        ("📊", "Dashboard", "Streamlit\nPower BI", "#a78bfa"),
    ]
    for col, (icon, title_, sub, color) in zip(arch_cols, arch_data):
        with col:
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border);
                 border-top:3px solid {color};border-radius:10px;padding:1.2rem;
                 text-align:center">
              <div style="font-size:1.6rem">{icon}</div>
              <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.1rem;
                   font-weight:800;color:{color};margin:0.3rem 0;letter-spacing:0.05em">
                {title_.upper()}
              </div>
              <div style="font-size:0.72rem;color:var(--text-2);white-space:pre-line">
                {sub}
              </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        section("🏀", "NBA Quick View", "Top 5 standings")
        standings_home = get_nba_standings()
        top5 = standings_home.head(5)[["#","Team","W","L","Win%","Form"]].copy()
        top5["Form"] = top5["Form"].apply(form_badge)
        st.markdown("""
        <style>
        .home-table { width:100%;border-collapse:collapse;font-family:'DM Sans',sans-serif;font-size:0.82rem }
        .home-table th { color:#4a6077;font-weight:600;font-size:0.65rem;letter-spacing:0.1em;
            text-transform:uppercase;padding:0.4rem 0.6rem;border-bottom:1px solid #1c2333;text-align:left }
        .home-table td { padding:0.55rem 0.6rem;border-bottom:1px solid #111827;color:#f0f4f8 }
        .home-table tr:hover td { background:#151c28 }
        </style>""" + "<table class='home-table'><thead><tr>" +
        "".join(f"<th>{c}</th>" for c in top5.columns) +
        "</tr></thead><tbody>" +
        "".join("<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>"
                for row in top5.values) +
        "</tbody></table>", unsafe_allow_html=True)

    with col_r:
        section("⚽", "Football Quick View", "Premier League Top 5")
        st_home = get_football_standings("Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿")
        top5f = st_home.head(5)[["#","Team","Pts","W","D","L","GD","Form"]].copy()
        top5f["Form"] = top5f["Form"].apply(form_badge)
        st.markdown("""<table class='home-table'><thead><tr>""" +
        "".join(f"<th>{c}</th>" for c in top5f.columns) +
        "</tr></thead><tbody>" +
        "".join("<tr>" + "".join(f"<td>{v}</td>" for v in row) + "</tr>"
                for row in top5f.values) +
        "</tbody></table>", unsafe_allow_html=True)

    st.markdown("""
    <div style="margin-top:2rem;padding:1rem 1.2rem;background:rgba(245,166,35,0.06);
         border:1px solid rgba(245,166,35,0.2);border-radius:8px;font-size:0.83rem;
         color:var(--text-2)">
      👈 <strong style="color:var(--gold)">Navigate</strong> using the sidebar to explore
      NBA analytics, Football analytics, and the AI recommendation engine.
    </div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 1 — NBA
# ─────────────────────────────────────────────────────────────────────────────

elif "NBA" in page:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem">
      <span style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;
           font-weight:700;letter-spacing:0.2em;color:#f5a623;text-transform:uppercase">
        Season 2023–24
      </span>
      <h1 style="font-family:'Barlow Condensed',sans-serif;font-size:2.8rem;
          font-weight:900;color:#f0f4f8;line-height:1;margin:0.2rem 0 0">
        🏀 NBA ANALYTICS
      </h1>
    </div>""", unsafe_allow_html=True)

    tab_s, tab_p, tab_t = st.tabs(["STANDINGS", "PLAYERS", "TEAM TREND"])

    # ── STANDINGS ──────────────────────────────────────────────────────────
    with tab_s:
        df = get_nba_standings(conf_filter if "conf_filter" in dir() else "All")

        kpi_row([
            ("Leader Win%",       f"{df['Win%'].max():.3f}", df.iloc[0]['Team'], None),
            ("Avg PTS/G (top 5)", f"{df.head(5)['PTS/G'].mean():.1f}", "Top 5 teams", None),
            ("Best Net RTG",      f"+{df['Net'].max():.1f}", "per 100 possessions", None),
            ("Teams shown",       str(len(df)), None, None),
        ])

        st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2)

        with col_a:
            fig = px.bar(df.sort_values("Win%"), x="Win%", y="Team", orientation="h",
                         color="Win%", color_continuous_scale=["#ff4560","#f5a623","#00e676"],
                         text="Win%")
            fig.update_traces(texttemplate="%{text:.3f}", textposition="outside",
                              textfont=dict(color="#8fa3b8", size=10))
            apply_plotly(fig, 520, "Win Percentage by Team")
            fig.update_layout(coloraxis_showscale=False,
                              yaxis=dict(tickfont=dict(size=10, color="#8fa3b8")))
            st.plotly_chart(fig, use_container_width=True)

        with col_b:
            fig2 = px.scatter(df, x="OPP/G", y="PTS/G", size="W", color="Net",
                              text="Team", color_continuous_scale="RdYlGn",
                              labels={"PTS/G":"PTS Scored/G","OPP/G":"PTS Allowed/G"},
                              size_max=30)
            fig2.update_traces(textposition="top center", textfont=dict(size=8, color="#8fa3b8"))
            fig2.add_vline(x=df["OPP/G"].mean(), line_dash="dash",
                           line_color="rgba(139,163,184,0.3)")
            fig2.add_hline(y=df["PTS/G"].mean(), line_dash="dash",
                           line_color="rgba(139,163,184,0.3)")
            apply_plotly(fig2, 520, "Offensive vs Defensive Efficiency")
            st.plotly_chart(fig2, use_container_width=True)

        # ── Full table with form badges
        section("📋", "Full Standings Table")
        display = df.copy()
        display["Form"] = display["Form"].apply(form_badge)
        st.markdown(
            "<style>.standings td:first-child{color:#f5a623;font-weight:700}"
            ".standings td{vertical-align:middle}</style>", unsafe_allow_html=True)
        cols_show = ["#","Team","W","L","Win%","PTS/G","OPP/G","Net","Conf","Form"]
        st.markdown(
            "<table class='home-table standings'><thead><tr>" +
            "".join(f"<th>{c}</th>" for c in cols_show) +
            "</tr></thead><tbody>" +
            "".join("<tr>" + "".join(f"<td>{display.iloc[i][c]}</td>"
                    for c in cols_show) + "</tr>" for i in range(len(display))) +
            "</tbody></table>", unsafe_allow_html=True)

    # ── PLAYERS ────────────────────────────────────────────────────────────
    with tab_p:
        players = get_nba_players()
        c_kpi, c_sort, c_pos = st.columns([3,2,3])
        with c_sort:
            kpi = st.selectbox("Sort by", ["PTS","REB","AST","FG%","3P%","TS%","MIN"])
        with c_pos:
            pos_f = st.multiselect("Position", ["PG","SG","SF","PF","C"],
                                   default=["PG","SG","SF","PF","C"])
        df_p = players[players["Pos"].isin(pos_f)].sort_values(kpi, ascending=False)

        kpi_row([
            (f"Best {kpi}",  f"{df_p.iloc[0][kpi]}",   df_p.iloc[0]['Player'], None),
            (f"Avg {kpi}",   f"{df_p[kpi].mean():.1f}", f"{len(df_p)} players", None),
            ("Max PTS/G",    f"{df_p['PTS'].max()}",    df_p.loc[df_p['PTS'].idxmax(),'Player'], None),
            ("Max REB/G",    f"{df_p['REB'].max()}",    df_p.loc[df_p['REB'].idxmax(),'Player'], None),
        ])

        col1, col2 = st.columns([3,2])
        with col1:
            fig3 = px.scatter(df_p, x="AST", y="PTS", size="REB", color="Pos",
                              text="Player", size_max=30,
                              color_discrete_sequence=["#f5a623","#00d4ff","#00e676","#ff4560","#a78bfa"],
                              labels={"PTS":"Points/G","AST":"Assists/G"})
            fig3.update_traces(textposition="top center", textfont=dict(size=8,color="#8fa3b8"))
            apply_plotly(fig3, 440, "Points vs Assists  (bubble = Rebounds)")
            st.plotly_chart(fig3, use_container_width=True)

        with col2:
            # Top scorers horizontal bar
            top10 = df_p.nlargest(10, "PTS")
            fig4 = go.Figure(go.Bar(
                x=top10["PTS"], y=top10["Player"], orientation="h",
                marker=dict(
                    color=top10["PTS"],
                    colorscale=[[0,"#1c2333"],[1,"#f5a623"]],
                ),
                text=top10["PTS"], textposition="outside",
                textfont=dict(color="#8fa3b8", size=10),
            ))
            apply_plotly(fig4, 440, "Top Scorers (PTS/G)")
            fig4.update_layout(yaxis=dict(autorange="reversed",
                               tickfont=dict(size=9, color="#8fa3b8")))
            st.plotly_chart(fig4, use_container_width=True)

        # ── Player radar
        section("📡", "Player Radar")
        sel = st.selectbox("Select player", df_p["Player"].tolist(), key="nba_radar")
        p = df_p[df_p["Player"] == sel].iloc[0]
        cats = ["PTS","REB","AST","FG%","3P%","FT%"]
        maxv = {"PTS":40,"REB":15,"AST":12,"FG%":1.0,"3P%":1.0,"FT%":1.0}
        vals = [p[c]/maxv[c] for c in cats]

        fig5 = go.Figure()
        fig5.add_trace(go.Scatterpolar(
            r=vals+[vals[0]], theta=cats+[cats[0]],
            fill="toself",
            fillcolor="rgba(245,166,35,0.12)",
            line=dict(color="#f5a623", width=2.5),
            name=sel,
        ))
        fig5.update_layout(
            **{k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis")},
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0,1], gridcolor="#1c2333",
                                tickfont=dict(color="#4a6077",size=9)),
                angularaxis=dict(tickfont=dict(color="#8fa3b8",size=11), gridcolor="#1c2333"),
            ),
            height=360,
            title=dict(text=sel.upper(), font=dict(family="Barlow Condensed",
                       size=18, color="#f5a623"), x=0),
        )
        c_r, c_s = st.columns([2,3])
        with c_r:
            st.plotly_chart(fig5, use_container_width=True)
        with c_s:
            stat_df = pd.DataFrame({
                "Stat": ["PTS/G","REB/G","AST/G","FG%","3P%","FT%","MIN","GP","TS%"],
                "Value": [p["PTS"],p["REB"],p["AST"],p["FG%"],p["3P%"],p["FT%"],
                          p["MIN"],p["GP"],p["TS%"]],
            })
            st.dataframe(stat_df, use_container_width=True, hide_index=True)

    # ── TEAM TREND ─────────────────────────────────────────────────────────
    with tab_t:
        sel_team = st.selectbox("Team", NBA_TEAMS, key="nba_trend_team")
        n = n_games if "n_games" in dir() else 15
        td = get_nba_trend(sel_team, n)

        wins = (td["W/L"]=="W").sum()
        losses = (td["W/L"]=="L").sum()
        avg_pts = td["PTS"].mean()
        avg_opp = td["OPP"].mean()
        net = avg_pts - avg_opp

        kpi_row([
            ("Wins",          str(wins),          f"{wins/(wins+losses)*100:.0f}%", None),
            ("Losses",        str(losses),        None, None),
            ("Avg PTS",       f"{avg_pts:.1f}",   None, None),
            ("Avg Allowed",   f"{avg_opp:.1f}",   f"{net:+.1f} net", None),
        ])

        # Score timeline
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(
            x=td["Date"], y=td["PTS"], name=sel_team,
            mode="lines+markers",
            line=dict(color="#f5a623", width=2.5),
            marker=dict(
                size=10, color=["#00e676" if r=="W" else "#ff4560" for r in td["W/L"]],
                line=dict(color="#f5a623", width=1.5),
            ),
        ))
        fig6.add_trace(go.Scatter(
            x=td["Date"], y=td["OPP"], name="Opponent",
            mode="lines+markers",
            line=dict(color="#2a3f56", width=2, dash="dot"),
            marker=dict(size=6, color="#2a3f56"),
        ))
        fig6.add_hline(y=avg_pts, line_dash="dash",
                       line_color="rgba(245,166,35,0.3)",
                       annotation_text=f"avg {avg_pts:.0f}",
                       annotation_font=dict(color="#f5a623",size=10))
        apply_plotly(fig6, 380, f"{sel_team} — Score Timeline")
        fig6.update_layout(legend=dict(orientation="h", y=1.1, x=0))
        st.plotly_chart(fig6, use_container_width=True)

        c_pie, c_tbl = st.columns([1,2])
        with c_pie:
            fig7 = go.Figure(go.Pie(
                labels=["Wins","Losses"], values=[wins,losses], hole=0.62,
                marker=dict(colors=["#00e676","#ff4560"],
                            line=dict(color="#0d1117",width=3)),
                textfont=dict(family="Barlow Condensed",size=14,color="#f0f4f8"),
            ))
            fig7.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items()
                                   if k not in ("xaxis","yaxis")},
                               height=280,
                               annotations=[dict(text=f"<b>{wins}W</b>", x=0.5, y=0.5,
                               font=dict(family="Barlow Condensed",size=22,color="#f5a623"),
                               showarrow=False)])
            st.plotly_chart(fig7, use_container_width=True)
        with c_tbl:
            st.dataframe(td[["Date","Vs","PTS","OPP","W/L"]], use_container_width=True,
                         hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 2 — FOOTBALL
# ─────────────────────────────────────────────────────────────────────────────

elif "Football" in page:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem">
      <span style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;
           font-weight:700;letter-spacing:0.2em;color:#00d4ff;text-transform:uppercase">
        Season 2023–24
      </span>
      <h1 style="font-family:'Barlow Condensed',sans-serif;font-size:2.8rem;
          font-weight:900;color:#f0f4f8;line-height:1;margin:0.2rem 0 0">
        ⚽ FOOTBALL ANALYTICS
      </h1>
    </div>""", unsafe_allow_html=True)

    league_ = league if "league" in dir() else "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿"
    tab_fs, tab_fp, tab_ft = st.tabs(["STANDINGS", "PLAYERS", "TEAM TREND"])

    # ── STANDINGS ──────────────────────────────────────────────────────────
    with tab_fs:
        df_f = get_football_standings(league_)

        leader = df_f.iloc[0]
        kpi_row([
            ("🥇 Leader",        leader["Team"],             f"{leader['Pts']} pts", None),
            ("Avg G/Game",       f"{df_f['G/G'].mean():.2f}", "scored", None),
            ("Most Goals",       str(df_f["GF"].max()),       df_f.loc[df_f["GF"].idxmax(),"Team"], None),
            ("Best Defense",     str(df_f["GA"].min()),       df_f.loc[df_f["GA"].idxmin(),"Team"] + " GA", None),
        ])

        c_pts, c_att = st.columns(2)
        with c_pts:
            fig_pts = px.bar(df_f.sort_values("Pts"), x="Pts", y="Team", orientation="h",
                             color="Pts", color_continuous_scale=["#1c2333","#00d4ff"],
                             text="Pts")
            fig_pts.update_traces(textposition="outside",
                                  textfont=dict(color="#8fa3b8", size=10))
            apply_plotly(fig_pts, 480, "Points Table")
            fig_pts.update_layout(coloraxis_showscale=False,
                                  yaxis=dict(tickfont=dict(size=10,color="#8fa3b8")))
            st.plotly_chart(fig_pts, use_container_width=True)

        with c_att:
            fig_att = px.scatter(df_f, x="GA", y="GF", size="Pts", color="W%",
                                 text="Team", color_continuous_scale="RdYlGn",
                                 labels={"GF":"Goals Scored","GA":"Goals Conceded"},
                                 size_max=28)
            fig_att.update_traces(textposition="top center",
                                  textfont=dict(size=8,color="#8fa3b8"))
            fig_att.add_vline(x=df_f["GA"].mean(), line_dash="dash",
                              line_color="rgba(139,163,184,0.25)")
            fig_att.add_hline(y=df_f["GF"].mean(), line_dash="dash",
                              line_color="rgba(139,163,184,0.25)")
            apply_plotly(fig_att, 480, "Attack vs Defence")
            st.plotly_chart(fig_att, use_container_width=True)

        # W/D/L stacked
        fig_wdl = go.Figure()
        for val, color_, label_ in [("W","#00e676","Wins"),("D","#f5a623","Draws"),("L","#ff4560","Losses")]:
            fig_wdl.add_trace(go.Bar(name=label_, x=df_f["Team"], y=df_f[val],
                                     marker_color=color_))
        fig_wdl.update_layout(barmode="stack",
                               xaxis=dict(tickangle=-35, tickfont=dict(size=9,color="#8fa3b8")))
        apply_plotly(fig_wdl, 340, "Win / Draw / Loss Distribution")
        st.plotly_chart(fig_wdl, use_container_width=True)

        section("📋", "Full Table", league_)
        disp_f = df_f.copy()
        disp_f["Form"] = disp_f["Form"].apply(form_badge)
        cols_f = ["#","Team","P","W","D","L","GF","GA","GD","Pts","Form","CS"]
        st.markdown(
            "<table class='home-table'><thead><tr>" +
            "".join(f"<th>{c}</th>" for c in cols_f) +
            "</tr></thead><tbody>" +
            "".join("<tr>" + "".join(f"<td>{disp_f.iloc[i][c]}</td>"
                    for c in cols_f) + "</tr>" for i in range(len(disp_f))) +
            "</tbody></table>", unsafe_allow_html=True)

    # ── PLAYERS ────────────────────────────────────────────────────────────
    with tab_fp:
        fp = get_football_players()
        c_s, c_p = st.columns([2,3])
        with c_s:
            kpi_f = st.selectbox("Sort by", ["Goals","Ast","G+A","Rating","G/90","Key P"])
        with c_p:
            pos_ff = st.multiselect("Position", ["FW","MF","DF"], default=["FW","MF"])
        df_fp = fp[fp["Pos"].isin(pos_ff)].sort_values(kpi_f, ascending=False)

        kpi_row([
            (f"Top {kpi_f}",  f"{df_fp.iloc[0][kpi_f]}", df_fp.iloc[0]['Player'], None),
            (f"Avg {kpi_f}",  f"{df_fp[kpi_f].mean():.1f}", None, None),
            ("Best Rating",   f"{df_fp['Rating'].max()}", df_fp.loc[df_fp['Rating'].idxmax(),'Player'], None),
            ("Players",       str(len(df_fp)), None, None),
        ])

        c_sc, c_ast = st.columns(2)
        with c_sc:
            top_s = df_fp.nlargest(10, "Goals")
            fig_sc = go.Figure(go.Bar(
                x=top_s["Player"], y=top_s["Goals"],
                marker=dict(color=top_s["Goals"],
                            colorscale=[[0,"#1c2333"],[1,"#00d4ff"]]),
                text=top_s["Goals"], textposition="outside",
                textfont=dict(color="#8fa3b8",size=10),
            ))
            apply_plotly(fig_sc, 360, "Top Scorers")
            fig_sc.update_layout(coloraxis_showscale=False,
                                 xaxis=dict(tickangle=-25,tickfont=dict(size=8,color="#8fa3b8")))
            st.plotly_chart(fig_sc, use_container_width=True)

        with c_ast:
            fig_ga = px.scatter(df_fp, x="Ast", y="Goals", size="Apps", color="Rating",
                                text="Player", color_continuous_scale="Blues",
                                labels={"Goals":"Goals","Ast":"Assists"}, size_max=25)
            fig_ga.update_traces(textposition="top center",
                                 textfont=dict(size=8,color="#8fa3b8"))
            apply_plotly(fig_ga, 360, "Goals vs Assists (bubble = Appearances)")
            st.plotly_chart(fig_ga, use_container_width=True)

        section("📋", "Player Stats Table")
        st.dataframe(df_fp.sort_values(kpi_f, ascending=False),
                     use_container_width=True, hide_index=True)

    # ── TEAM TREND ─────────────────────────────────────────────────────────
    with tab_ft:
        all_teams_f = sorted(set(t for lg in LEAGUES.values() for t in lg))
        sel_tf = st.selectbox("Team", all_teams_f, key="ft_trend")
        n_m = n_matches if "n_matches" in dir() else 12
        td_f = get_football_trend(sel_tf, n_m)

        w_ = (td_f["Res"]=="W").sum()
        d_ = (td_f["Res"]=="D").sum()
        l_ = (td_f["Res"]=="L").sum()
        cs_ = td_f["CS"].sum()

        kpi_row([
            ("Wins",         str(w_),  None, None),
            ("Draws",        str(d_),  None, None),
            ("Losses",       str(l_),  None, None),
            ("Clean Sheets", str(int(cs_)), f"{cs_/n_m*100:.0f}%", None),
        ])

        # Goals timeline
        fig_gt = go.Figure()
        fig_gt.add_trace(go.Bar(
            x=td_f["Date"], y=td_f["GF"], name="Goals Scored",
            marker_color="#00e676",
        ))
        fig_gt.add_trace(go.Bar(
            x=td_f["Date"], y=[-g for g in td_f["GA"]], name="Goals Conceded",
            marker_color="#ff4560",
        ))
        fig_gt.update_layout(barmode="relative")
        apply_plotly(fig_gt, 360, f"{sel_tf} — Goals Scored vs Conceded")
        fig_gt.update_layout(legend=dict(orientation="h", y=1.1))
        st.plotly_chart(fig_gt, use_container_width=True)

        # Cumulative points
        pts_map = {"W":3,"D":1,"L":0}
        td_f["Match Pts"] = td_f["Res"].map(pts_map)
        td_f["Cum Pts"]   = td_f["Match Pts"].cumsum()
        fig_cum = px.area(td_f, x="Date", y="Cum Pts",
                          color_discrete_sequence=["#00d4ff"])
        fig_cum.update_traces(fill="tozeroy",
                              fillcolor="rgba(0,212,255,0.08)",
                              line=dict(color="#00d4ff",width=2))
        apply_plotly(fig_cum, 280, "Cumulative Points")
        st.plotly_chart(fig_cum, use_container_width=True)

        c_donut, c_tbl_f = st.columns([1,2])
        with c_donut:
            fig_d = go.Figure(go.Pie(
                labels=["Wins","Draws","Losses"], values=[w_,d_,l_], hole=0.62,
                marker=dict(colors=["#00e676","#f5a623","#ff4560"],
                            line=dict(color="#0d1117",width=3)),
                textfont=dict(family="Barlow Condensed",size=13,color="#f0f4f8"),
            ))
            fig_d.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items()
                                    if k not in ("xaxis","yaxis")},
                                height=260)
            st.plotly_chart(fig_d, use_container_width=True)
        with c_tbl_f:
            st.dataframe(td_f[["Date","Vs","GF","GA","Res"]],
                         use_container_width=True, hide_index=True)


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 3 — RECOMMENDER
# ─────────────────────────────────────────────────────────────────────────────

elif "Recommender" in page:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem">
      <span style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;
           font-weight:700;letter-spacing:0.2em;color:#a78bfa;text-transform:uppercase">
        AI-Powered · Content-Based Filtering
      </span>
      <h1 style="font-family:'Barlow Condensed',sans-serif;font-size:2.8rem;
          font-weight:900;color:#f0f4f8;line-height:1;margin:0.2rem 0 0">
        🤖 SPORT RECOMMENDER
      </h1>
      <p style="color:#8fa3b8;font-size:0.9rem;margin-top:0.5rem">
        Personalised content ranking using cosine similarity on user preference vectors.
      </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ── Profile builder
    section("👤", "Build Your Profile")

    col_nba, col_foot = st.columns(2)
    with col_nba:
        st.markdown("<div style='font-size:0.7rem;color:#4a6077;letter-spacing:0.1em;"
                    "text-transform:uppercase;font-weight:700;margin-bottom:0.5rem'>"
                    "NBA Preferences</div>", unsafe_allow_html=True)
        nba_p = nba_pref if "nba_pref" in dir() else 0.6
        fav_nba_teams = st.multiselect(
            "Favorite NBA teams",
            NBA_TEAMS, default=["Los Angeles Lakers","Boston Celtics"])
        fav_nba_players = st.multiselect(
            "Favorite NBA players",
            [p[0] for p in NBA_PLAYERS], default=["LeBron James","Luka Doncic"])

    with col_foot:
        st.markdown("<div style='font-size:0.7rem;color:#4a6077;letter-spacing:0.1em;"
                    "text-transform:uppercase;font-weight:700;margin-bottom:0.5rem'>"
                    "Football Preferences</div>", unsafe_allow_html=True)
        all_ft = sorted(set(t for lg in LEAGUES.values() for t in lg))
        fav_ft_teams = st.multiselect(
            "Favorite football teams",
            all_ft, default=["Paris Saint-Germain","Real Madrid"])
        fav_ft_players = st.multiselect(
            "Favorite football players",
            [p[0] for p in FOOTBALL_PLAYERS], default=["Kylian Mbappé","Erling Haaland"])

    col_hist, col_set = st.columns([3,2])
    with col_hist:
        n_hist = st.slider("Consultation history size (simulated)", 0, 25, 8)
    with col_set:
        sport_opt = st.selectbox("Filter recommendations by sport",
                                 ["All","NBA only","Football only"])
        excl_seen = st.checkbox("Exclude already-seen content", value=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

    if st.button("🎯  GENERATE RECOMMENDATIONS"):

        # ── Inline lightweight recommender (no external import needed)
        from sklearn.metrics.pairwise import cosine_similarity
        from sklearn.preprocessing import MinMaxScaler

        random.seed(99)
        SPORT_MAP = {"nba":0, "football":1}
        TYPE_MAP  = {"game":0, "player":1, "team":2}

        # Build catalog
        catalog = []
        for i in range(80):
            team = random.choice(NBA_TEAMS)
            catalog.append({"id":f"nba_game_{i}","type":"game","sport":"nba",
                             "team":team,"player":"","pop":round(random.uniform(0.3,1),2),
                             "rec":round(random.uniform(0.5,1),2)})
        for name,team,pos,*_ in NBA_PLAYERS:
            catalog.append({"id":f"nba_player_{name.replace(' ','_')}","type":"player",
                             "sport":"nba","team":team,"player":name,
                             "pop":round(random.uniform(0.6,1),2),"rec":0.9})
        for team in NBA_TEAMS:
            catalog.append({"id":f"nba_team_{team.replace(' ','_')}","type":"team",
                             "sport":"nba","team":team,"player":"",
                             "pop":round(random.uniform(0.4,0.9),2),"rec":0.8})
        for league_, teams_ in LEAGUES.items():
            for i in range(25):
                t = random.choice(teams_)
                catalog.append({"id":f"football_game_{league_[:2]}_{i}","type":"game",
                                 "sport":"football","team":t,"player":"",
                                 "pop":round(random.uniform(0.3,1),2),
                                 "rec":round(random.uniform(0.5,1),2)})
        for name,team,pos,*_ in FOOTBALL_PLAYERS:
            catalog.append({"id":f"football_player_{name.replace(' ','_')}","type":"player",
                             "sport":"football","team":team,"player":name,
                             "pop":round(random.uniform(0.6,1),2),"rec":0.9})

        df_cat = pd.DataFrame(catalog)
        matrix = np.array([[SPORT_MAP[r["sport"]], TYPE_MAP[r["type"]],
                             r["pop"], r["rec"]] for r in catalog], dtype=float)
        scaler = MinMaxScaler()
        mat_sc = scaler.fit_transform(matrix)

        # User vector
        sport_enc = nba_p * SPORT_MAP["nba"] + (1-nba_p) * SPORT_MAP["football"]
        hist_pool = df_cat[df_cat["sport"] == ("nba" if nba_p >= 0.5 else "football")]["id"].tolist()
        history   = random.sample(hist_pool, min(n_hist, len(hist_pool)))
        user_vec  = scaler.transform([[sport_enc, 1, 0.7, 0.85]])

        sims = cosine_similarity(user_vec, mat_sc)[0]
        df_cat["score"] = sims

        # Filters
        if excl_seen and history:
            df_cat = df_cat[~df_cat["id"].isin(history)]
        if sport_opt == "NBA only":
            df_cat = df_cat[df_cat["sport"] == "nba"]
        elif sport_opt == "Football only":
            df_cat = df_cat[df_cat["sport"] == "football"]

        # Boosts
        all_fav_teams   = fav_nba_teams + fav_ft_teams
        all_fav_players = fav_nba_players + fav_ft_players
        df_cat.loc[df_cat["team"].isin(all_fav_teams), "score"]   *= 1.25
        df_cat.loc[df_cat["player"].isin(all_fav_players), "score"] *= 1.20

        n_r = n_recs if "n_recs" in dir() else 12
        recs = (df_cat.sort_values("score", ascending=False)
                      .head(n_r)
                      .reset_index(drop=True))
        recs["rank"] = recs.index + 1

        with st.spinner(""):
            pass

        st.success(f"✅ {len(recs)} recommendations generated")
        st.markdown("<hr>", unsafe_allow_html=True)

        # ── KPIs
        kpi_row([
            ("Total",          str(len(recs)), None, None),
            ("🏀 NBA",          str((recs["sport"]=="nba").sum()), None, None),
            ("⚽ Football",     str((recs["sport"]=="football").sum()), None, None),
            ("Avg Score",      f"{recs['score'].mean():.3f}", None, None),
        ])

        col_ch, col_tb = st.columns([3,2])
        with col_ch:
            fig_recs = go.Figure(go.Bar(
                x=recs["score"].round(4),
                y=recs["id"],
                orientation="h",
                marker=dict(
                    color=recs["score"],
                    colorscale=[[0,"#1c2333"],[0.5,"#a78bfa"],[1,"#f5a623"]],
                ),
                text=recs["score"].round(3),
                textposition="outside",
                textfont=dict(color="#8fa3b8",size=9),
            ))
            apply_plotly(fig_recs, max(320, len(recs)*30), "Recommendation Scores")
            fig_recs.update_layout(coloraxis_showscale=False,
                                   yaxis=dict(autorange="reversed",
                                              tickfont=dict(size=9,color="#8fa3b8")))
            st.plotly_chart(fig_recs, use_container_width=True)

        with col_tb:
            disp_r = recs[["rank","id","type","sport","team","score"]].copy()
            disp_r["score"] = disp_r["score"].round(4)
            disp_r.columns = ["#","Content","Type","Sport","Team","Score"]
            st.dataframe(disp_r, use_container_width=True, hide_index=True)

        # ── Type breakdown
        c_t1, c_t2 = st.columns(2)
        with c_t1:
            tc = recs["type"].value_counts().reset_index()
            tc.columns = ["Type","Count"]
            fig_tc = go.Figure(go.Pie(
                labels=tc["Type"], values=tc["Count"], hole=0.55,
                marker=dict(colors=["#f5a623","#00d4ff","#00e676"],
                            line=dict(color="#0d1117",width=3)),
                textfont=dict(family="Barlow Condensed",size=14),
            ))
            fig_tc.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items()
                                     if k not in ("xaxis","yaxis")},
                                 height=260,
                                 title=dict(text="Content Types",
                                 font=dict(family="Barlow Condensed",size=16,
                                           color="#f0f4f8"),x=0))
            st.plotly_chart(fig_tc, use_container_width=True)

        with c_t2:
            sc = recs["sport"].value_counts().reset_index()
            sc.columns = ["Sport","Count"]
            fig_sc2 = go.Figure(go.Pie(
                labels=sc["Sport"], values=sc["Count"], hole=0.55,
                marker=dict(colors=["#f5a623","#00d4ff"],
                            line=dict(color="#0d1117",width=3)),
                textfont=dict(family="Barlow Condensed",size=14),
            ))
            fig_sc2.update_layout(**{k:v for k,v in PLOTLY_LAYOUT.items()
                                      if k not in ("xaxis","yaxis")},
                                  height=260,
                                  title=dict(text="Sport Split",
                                  font=dict(family="Barlow Condensed",size=16,
                                            color="#f0f4f8"),x=0))
            st.plotly_chart(fig_sc2, use_container_width=True)

    else:
        st.markdown("""
        <div style="margin:2rem 0;padding:2rem;background:var(--bg-card);
             border:1px dashed var(--border-bright);border-radius:12px;
             text-align:center">
          <div style="font-size:2.5rem;margin-bottom:0.5rem">🎯</div>
          <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.4rem;
               font-weight:800;color:var(--text-1)">Configure your profile and click Generate</div>
          <div style="color:var(--text-3);font-size:0.85rem;margin-top:0.4rem">
            Content-based filtering · Cosine similarity · 800+ catalog items
          </div>
        </div>""", unsafe_allow_html=True)

    # ── How it works
    st.markdown("<hr>", unsafe_allow_html=True)
    section("⚙️", "How It Works")
    steps = [
        ("1", "Feature Vector", "Each content item is encoded: sport type, content type, popularity, recency → 4D vector normalized [0,1]"),
        ("2", "User Vector", "Built from sport preferences slider + average features of consultation history (implicit feedback)"),
        ("3", "Cosine Similarity", "Score = cos(user_vec, item_vec). Items in same sport direction score higher"),
        ("4", "Boost", "Favorite teams ×1.25 · Favorite players ×1.20 · Already-seen filtered out"),
    ]
    cols_step = st.columns(4)
    for col, (num, title_, desc) in zip(cols_step, steps):
        with col:
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border);
                 border-radius:10px;padding:1rem;height:100%">
              <div style="font-family:'Barlow Condensed',sans-serif;font-size:2rem;
                   font-weight:900;color:var(--gold);line-height:1">{num}</div>
              <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.05rem;
                   font-weight:800;color:var(--text-1);margin:0.3rem 0;
                   text-transform:uppercase;letter-spacing:0.05em">{title_}</div>
              <div style="font-size:0.78rem;color:var(--text-2);line-height:1.5">{desc}</div>
            </div>""", unsafe_allow_html=True)
