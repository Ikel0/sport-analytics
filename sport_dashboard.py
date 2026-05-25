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

    page = st.selectbox("", ["🏠  Home", "🏀  NBA", "⚽  Football", "🤖  Recommender", "🔬  Similarity"],
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

    elif "Similarity" in page:
        sim_sport = st.selectbox("Sport", ["🏀 NBA", "⚽ Football"])
        sim_mode  = st.selectbox("Mode", ["Team Similarity", "Player Similarity"])
        n_similar = st.slider("Similar items to show", 3, 10, 5)

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


# ─────────────────────────────────────────────────────────────────────────────
#  PAGE 4 — SIMILARITY ENGINE
# ─────────────────────────────────────────────────────────────────────────────

elif "Similarity" in page:

    # ── imports
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.decomposition import PCA
    from sklearn.cluster import KMeans

    st.markdown("""
    <div style="padding:1rem 0 0.5rem">
      <span style="font-family:'Barlow Condensed',sans-serif;font-size:0.65rem;
           font-weight:700;letter-spacing:0.2em;color:#00e676;text-transform:uppercase">
        Multi-dimensional · Cosine Similarity · KMeans Clustering
      </span>
      <h1 style="font-family:'Barlow Condensed',sans-serif;font-size:2.8rem;
          font-weight:900;color:#f0f4f8;line-height:1;margin:0.2rem 0 0">
        🔬 SIMILARITY ENGINE
      </h1>
      <p style="color:#8fa3b8;font-size:0.9rem;margin-top:0.5rem">
        Find teams with the same playing style and players with the same statistical profile.
      </p>
    </div>""", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    # ─────────────────────────────────────────────────────────────────────────
    #  DATA — Rich synthetic stats (realistic distributions)
    # ─────────────────────────────────────────────────────────────────────────

    @st.cache_data(ttl=3600)
    def build_nba_team_stats():
        """
        NBA teams with 12 features covering:
        - Offense: PTS/G, PACE, 3PA/G, 3P%, AST/G, TOV/G, ORtg
        - Defense: OPP PTS/G, BLK/G, STL/G, DRtg, DREB%
        """
        random.seed(123)
        np.random.seed(123)
        teams = NBA_TEAMS
        styles = {
            # (pace, 3pa, ast, blk, stl) archetypes
            "Boston Celtics":             (98, 46, 27, 5.8, 7.9),
            "Oklahoma City Thunder":      (101,42, 29, 6.1, 8.1),
            "Denver Nuggets":             (96, 30, 32, 4.9, 7.4),
            "Minnesota Timberwolves":     (97, 36, 26, 6.8, 7.8),
            "Cleveland Cavaliers":        (99, 38, 28, 5.5, 7.5),
            "Los Angeles Lakers":         (100,35, 27, 5.2, 7.2),
            "Golden State Warriors":      (103,47, 31, 4.8, 8.3),
            "Miami Heat":                 (96, 34, 25, 5.4, 8.6),
            "Milwaukee Bucks":            (100,37, 26, 5.7, 7.1),
            "Phoenix Suns":               (98, 38, 28, 4.6, 7.5),
            "Dallas Mavericks":           (99, 43, 27, 4.4, 7.0),
            "Philadelphia 76ers":         (97, 33, 26, 5.9, 7.3),
            "Memphis Grizzlies":          (101,32, 28, 6.5, 9.1),
            "New York Knicks":            (95, 32, 25, 5.3, 7.6),
            "Sacramento Kings":           (103,40, 31, 4.2, 7.8),
            "Los Angeles Clippers":       (97, 37, 27, 5.1, 7.3),
            "New Orleans Pelicans":       (100,34, 27, 6.2, 8.0),
            "Indiana Pacers":             (104,41, 30, 4.5, 7.4),
        }
        rows = []
        for team in teams:
            pace, tpa, ast, blk, stl = styles.get(team, (99,37,27,5,7.5))
            pts  = round(pace * 1.15 + np.random.normal(0, 2), 1)
            fg3p = round(0.36 + tpa/1000 + np.random.normal(0, 0.02), 3)
            tov  = round(13 + np.random.normal(0, 1.5), 1)
            ortg = round(pts / pace * 100 + np.random.normal(0, 1), 1)
            opp  = round(pts - np.random.uniform(-4, 8), 1)
            drtg = round(opp / pace * 100 + np.random.normal(0, 1), 1)
            dreb = round(74 + np.random.normal(0, 3), 1)
            rows.append({
                "Team":   team,
                # Offense
                "PTS/G":  pts,
                "Pace":   pace + round(np.random.normal(0, 1), 1),
                "3PA/G":  tpa  + round(np.random.normal(0, 2), 1),
                "3P%":    fg3p,
                "AST/G":  ast  + round(np.random.normal(0, 1.5), 1),
                "TOV/G":  tov,
                "ORtg":   ortg,
                # Defense
                "OPP/G":  opp,
                "BLK/G":  blk  + round(np.random.normal(0, 0.5), 1),
                "STL/G":  stl  + round(np.random.normal(0, 0.4), 1),
                "DRtg":   drtg,
                "DREB%":  dreb,
            })
        return pd.DataFrame(rows)


    @st.cache_data(ttl=3600)
    def build_football_team_stats():
        """
        Football teams with 12 features:
        - Attack: Goals/G, xG/G, Shots/G, Possession%, KeyPasses/G, Crosses/G
        - Defense: GA/G, xGA/G, Tackles/G, Interceptions/G, PPDA (pressing), CleanSheets%
        """
        random.seed(456)
        np.random.seed(456)
        all_ft = [(t, lg) for lg, teams in LEAGUES.items() for t in teams]
        styles = {
            # (possession, press_intensity, direct_play)  0-1
            "Manchester City":    (0.65, 0.85, 0.3),
            "Arsenal":            (0.60, 0.80, 0.35),
            "Liverpool":          (0.55, 0.90, 0.5),
            "Aston Villa":        (0.50, 0.70, 0.55),
            "Tottenham":          (0.52, 0.65, 0.55),
            "Chelsea":            (0.55, 0.72, 0.45),
            "Newcastle":          (0.48, 0.75, 0.60),
            "Manchester United":  (0.50, 0.62, 0.55),
            "West Ham":           (0.46, 0.58, 0.65),
            "Brighton":           (0.60, 0.82, 0.38),
            "Brentford":          (0.44, 0.78, 0.75),
            "Fulham":             (0.50, 0.65, 0.58),
            "Paris Saint-Germain":(0.62, 0.72, 0.40),
            "Monaco":             (0.54, 0.80, 0.50),
            "Brest":              (0.52, 0.75, 0.52),
            "Lille":              (0.53, 0.82, 0.48),
            "Nice":               (0.52, 0.74, 0.52),
            "Lyon":               (0.55, 0.70, 0.45),
            "Lens":               (0.50, 0.85, 0.55),
            "Marseille":          (0.52, 0.78, 0.52),
            "Real Madrid":        (0.57, 0.70, 0.45),
            "Barcelona":          (0.65, 0.78, 0.28),
            "Girona":             (0.55, 0.80, 0.48),
            "Atletico Madrid":    (0.48, 0.88, 0.60),
            "Athletic Bilbao":    (0.50, 0.88, 0.55),
            "Real Betis":         (0.58, 0.72, 0.42),
            "Villarreal":         (0.56, 0.74, 0.44),
            "Sevilla":            (0.50, 0.76, 0.52),
            "Inter Milan":        (0.55, 0.80, 0.45),
            "AC Milan":           (0.52, 0.75, 0.50),
            "Juventus":           (0.52, 0.72, 0.52),
            "Atalanta":           (0.50, 0.82, 0.55),
            "Bologna":            (0.51, 0.75, 0.52),
            "Roma":               (0.53, 0.73, 0.50),
            "Lazio":              (0.50, 0.68, 0.55),
            "Napoli":             (0.55, 0.76, 0.46),
        }
        rows = []
        for team, league_name in all_ft:
            poss, press, direct = styles.get(team, (0.52, 0.74, 0.50))
            gf    = round(1.8 + poss*2   + np.random.normal(0, 0.25), 2)
            xg    = round(gf - 0.1       + np.random.normal(0, 0.15), 2)
            shots = round(14  + poss*10  + np.random.normal(0, 1.5), 1)
            kp    = round(10  + poss*8   + np.random.normal(0, 1.2), 1)
            cross = round(18  + direct*12 + np.random.normal(0, 2), 1)
            ga    = round(1.1 + (1-press)*1.2 + np.random.normal(0, 0.2), 2)
            xga   = round(ga  + np.random.normal(0, 0.1), 2)
            tkl   = round(18  + press*8  + np.random.normal(0, 1.5), 1)
            inte  = round(12  + press*5  + np.random.normal(0, 1), 1)
            ppda  = round(10  - press*7  + np.random.normal(0, 0.8), 2)  # lower=more press
            cs    = round(0.25 + press*0.2 + np.random.normal(0, 0.05), 2)
            rows.append({
                "Team": team, "League": league_name.split()[0],
                # Attack
                "Goals/G":  gf,   "xG/G":    xg,
                "Shots/G":  shots, "Poss%":   round(poss*100, 1),
                "KeyPass/G": kp,  "Cross/G": cross,
                # Defense
                "GA/G":    ga,    "xGA/G":   xga,
                "Tackle/G": tkl,  "Inter/G": inte,
                "PPDA":    ppda,  "CS%":     round(cs*100, 1),
            })
        return pd.DataFrame(rows)


    @st.cache_data(ttl=3600)
    def build_nba_player_stats():
        """
        Extended NBA player stats: raw + efficiency + role + physical profile.
        """
        random.seed(789)
        np.random.seed(789)
        # (name, team, pos, height_cm, weight_kg, archetype)
        PLAYERS_EXT = [
            ("Shai Gilgeous-Alexander","OKC","PG",198,95,"scorer"),
            ("Giannis Antetokounmpo","MIL","PF",211,110,"paint_dominant"),
            ("Luka Doncic","DAL","PG",201,104,"playmaker"),
            ("Joel Embiid","PHI","C",213,127,"post_scorer"),
            ("Jayson Tatum","BOS","SF",203,95,"scorer"),
            ("Nikola Jokic","DEN","C",211,129,"playmaker"),
            ("LeBron James","LAL","SF",206,113,"playmaker"),
            ("Stephen Curry","GSW","PG",188,84,"shooter"),
            ("Kevin Durant","PHX","SF",211,104,"scorer"),
            ("Anthony Davis","LAL","C",208,115,"paint_dominant"),
            ("Donovan Mitchell","CLE","PG",191,98,"scorer"),
            ("Damian Lillard","MIL","PG",188,91,"shooter"),
            ("Zion Williamson","NOP","PF",198,129,"paint_dominant"),
            ("Devin Booker","PHX","SG",196,95,"scorer"),
            ("Bam Adebayo","MIA","C",206,116,"paint_dominant"),
            ("Tyrese Haliburton","IND","PG",196,84,"playmaker"),
            ("Domantas Sabonis","SAC","C",211,107,"playmaker"),
            ("Trae Young","ATL","PG",185,74,"playmaker"),
            ("Jaren Jackson Jr","MEM","PF",211,107,"stretch_big"),
            ("Kristaps Porzingis","BOS","C",221,109,"stretch_big"),
            ("Karl-Anthony Towns","MIN","C",213,113,"stretch_big"),
            ("Paul George","LAC","SF",203,100,"two_way"),
            ("Kawhi Leonard","LAC","SF",201,102,"two_way"),
            ("Rudy Gobert","MIN","C",216,138,"paint_dominant"),
            ("Fred VanVleet","HOU","PG",188,91,"playmaker"),
            ("Mikal Bridges","NYK","SF",201,95,"two_way"),
        ]
        archetypes = {
            "scorer":       (27, 5,  4,  0.52, 0.40, 0.87, 30),
            "playmaker":    (22, 8,  10, 0.53, 0.36, 0.78, 33),
            "shooter":      (24, 5,  5,  0.47, 0.42, 0.91, 32),
            "paint_dominant":(26,12, 3,  0.60, 0.15, 0.74, 32),
            "stretch_big":  (20, 9,  2,  0.51, 0.38, 0.80, 28),
            "two_way":      (20, 5,  4,  0.49, 0.37, 0.84, 32),
        }
        rows = []
        for name, team, pos, ht, wt, arch in PLAYERS_EXT:
            base_pts, base_reb, base_ast, fg, fg3, ft, mins = archetypes[arch]
            pts  = round(base_pts + np.random.normal(0, 3), 1)
            reb  = round(base_reb + np.random.normal(0, 2), 1)
            ast  = round(base_ast + np.random.normal(0, 2), 1)
            stl  = round(1.2 + np.random.normal(0, 0.5), 1)
            blk  = round((0.5 if pos in ("PG","SG") else 1.5) + np.random.normal(0,0.4), 1)
            tov  = round(2.5 + ast*0.15 + np.random.normal(0,0.5), 1)
            fg_p = round(fg  + np.random.normal(0, 0.03), 3)
            fg3p = round(fg3 + np.random.normal(0, 0.03), 3)
            ft_p = round(ft  + np.random.normal(0, 0.04), 3)
            gp   = random.randint(55, 75)
            min_ = round(mins + np.random.normal(0, 2), 1)
            # Per-36 efficiency
            pts36 = round(pts  / min_ * 36, 1)
            reb36 = round(reb  / min_ * 36, 1)
            ast36 = round(ast  / min_ * 36, 1)
            ts    = round(pts  / (2*(fg_p*round(pts/fg_p*0.48,0) + 0.44*round(pts/ft_p*0.25,0) + 1e-9)), 3)
            rows.append({
                "Player": name, "Team": team, "Pos": pos,
                "Height": ht,   "Weight": wt,  "Archetype": arch,
                # Raw
                "PTS": pts, "REB": reb, "AST": ast, "STL": stl, "BLK": blk, "TOV": tov,
                # Efficiency
                "FG%": fg_p, "3P%": fg3p, "FT%": ft_p, "TS%": round(min(ts,0.75), 3),
                # Per-36
                "PTS/36": pts36, "REB/36": reb36, "AST/36": ast36,
                # Physical
                "MIN": min_, "GP": gp,
            })
        return pd.DataFrame(rows)


    # ─────────────────────────────────────────────────────────────────────────
    #  SIMILARITY ENGINE CORE
    # ─────────────────────────────────────────────────────────────────────────

    def compute_similarity(df: pd.DataFrame, features: list, id_col: str):
        """
        Returns:
          sim_df   — full N×N similarity matrix as DataFrame
          scores   — per-entity average similarity (how 'generic' vs 'unique')
          pca_df   — 2D PCA projection for scatter
          labels   — KMeans cluster labels (k=4)
        """
        X      = df[features].values.astype(float)
        scaler = StandardScaler()
        X_sc   = scaler.fit_transform(X)

        sim_mat = cosine_similarity(X_sc)
        sim_df  = pd.DataFrame(sim_mat,
                               index=df[id_col], columns=df[id_col])

        # PCA 2D
        pca    = PCA(n_components=2, random_state=42)
        X_2d   = pca.fit_transform(X_sc)
        pca_df = pd.DataFrame(X_2d, columns=["PC1","PC2"])
        pca_df[id_col] = df[id_col].values

        # KMeans clustering (k=4 styles)
        km     = KMeans(n_clusters=4, random_state=42, n_init=10)
        labels = km.fit_predict(X_sc)
        pca_df["Cluster"] = [f"Style {c+1}" for c in labels]

        # Avg similarity score (uniqueness — higher = more similar to others)
        avg_sim = sim_mat.mean(axis=1)

        return sim_df, avg_sim, pca_df, labels


    def top_n_similar(sim_df: pd.DataFrame, entity: str, n: int = 5):
        """Return top-N most similar entities (excluding self)."""
        row = sim_df.loc[entity].drop(entity).sort_values(ascending=False)
        return row.head(n)


    def radar_compare(df, features, entities, id_col, maxvals=None):
        """Multi-entity radar chart."""
        colors = ["#f5a623","#00d4ff","#00e676","#ff4560","#a78bfa"]
        fig = go.Figure()
        for i, ent in enumerate(entities):
            row  = df[df[id_col] == ent].iloc[0]
            vals = [row[f] for f in features]
            if maxvals:
                vals = [v/maxvals[j] for j,v in enumerate(vals)]
            fig.add_trace(go.Scatterpolar(
                r=vals+[vals[0]], theta=features+[features[0]],
                fill="toself",
                fillcolor=f"rgba({int(colors[i][1:3],16)},{int(colors[i][3:5],16)},{int(colors[i][5:],16)},0.10)",
                line=dict(color=colors[i], width=2.2),
                name=ent,
            ))
        fig.update_layout(
            **{k:v for k,v in PLOTLY_LAYOUT.items() if k not in ("xaxis","yaxis")},
            polar=dict(
                bgcolor="rgba(0,0,0,0)",
                radialaxis=dict(visible=True, range=[0,1] if maxvals else None,
                                gridcolor="#1c2333", tickfont=dict(color="#4a6077",size=8)),
                angularaxis=dict(tickfont=dict(color="#8fa3b8",size=10), gridcolor="#1c2333"),
            ),
            height=420,
            legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center",
                        font=dict(color="#8fa3b8",size=11)),
        )
        return fig


    def heatmap_fig(sim_df, title):
        fig = go.Figure(go.Heatmap(
            z=sim_df.values,
            x=sim_df.columns.tolist(),
            y=sim_df.index.tolist(),
            colorscale=[[0,"#080b14"],[0.3,"#1c2333"],[0.7,"#f5a623"],[1,"#fff"]],
            zmin=0, zmax=1,
            hoverongaps=False,
            hovertemplate="%{y} × %{x}<br>Similarity: %{z:.3f}<extra></extra>",
        ))
        fig.update_layout(
            **PLOTLY_LAYOUT,
            height=560,
            xaxis=dict(tickangle=-40, tickfont=dict(size=9,color="#8fa3b8")),
            yaxis=dict(tickfont=dict(size=9,color="#8fa3b8")),
            title=dict(text=title, font=dict(family="Barlow Condensed",
                       size=18, color="#f0f4f8"), x=0),
        )
        return fig


    # ─────────────────────────────────────────────────────────────────────────
    #  RENDER
    # ─────────────────────────────────────────────────────────────────────────

    s_sport = sim_sport if "sim_sport" in dir() else "🏀 NBA"
    s_mode  = sim_mode  if "sim_mode"  in dir() else "Team Similarity"
    n_sim   = n_similar if "n_similar" in dir() else 5

    # ══════════════════════════════════════════════════════════════════════════
    #  TEAM SIMILARITY
    # ══════════════════════════════════════════════════════════════════════════
    if s_mode == "Team Similarity":

        section("🏟️", "Team Style Similarity",
                "Which teams play the most similar style?")

        if "NBA" in s_sport:
            df_ts    = build_nba_team_stats()
            feat_off = ["PTS/G","Pace","3PA/G","3P%","AST/G","TOV/G","ORtg"]
            feat_def = ["OPP/G","BLK/G","STL/G","DRtg","DREB%"]
            feat_all = feat_off + feat_def
            id_col   = "Team"
            radar_feats = ["PTS/G","Pace","3P%","AST/G","STL/G","BLK/G","ORtg"]

            # Style labels
            style_map = {
                "Boston Celtics":"3PT Heavy","Golden State Warriors":"3PT Heavy",
                "Dallas Mavericks":"3PT Heavy","Indiana Pacers":"Fast & Open",
                "Sacramento Kings":"Fast & Open","Oklahoma City Thunder":"Athletic",
                "Memphis Grizzlies":"Athletic","Denver Nuggets":"Post/Pass",
                "Los Angeles Lakers":"Post/Pass","Philadelphia 76ers":"Post/Pass",
                "Milwaukee Bucks":"Physical","Minnesota Timberwolves":"Defensive",
                "Miami Heat":"Defensive","New York Knicks":"Grind",
                "Cleveland Cavaliers":"Balanced","Phoenix Suns":"Balanced",
                "Los Angeles Clippers":"Balanced","New Orleans Pelicans":"Athletic",
            }
            df_ts["Style"] = df_ts["Team"].map(style_map).fillna("Balanced")

        else:
            df_ts    = build_football_team_stats()
            feat_off = ["Goals/G","xG/G","Shots/G","Poss%","KeyPass/G","Cross/G"]
            feat_def = ["GA/G","xGA/G","Tackle/G","Inter/G","PPDA","CS%"]
            feat_all = feat_off + feat_def
            id_col   = "Team"
            radar_feats = ["Goals/G","Poss%","Shots/G","Tackle/G","PPDA","CS%"]

            style_map_f = {}
            for t in df_ts["Team"]:
                row = df_ts[df_ts["Team"]==t].iloc[0]
                if row["Poss%"] >= 58:
                    style_map_f[t] = "Tiki-Taka"
                elif row["PPDA"] <= 6:
                    style_map_f[t] = "High Press"
                elif row["Cross/G"] >= 24:
                    style_map_f[t] = "Direct/Wings"
                elif row["Goals/G"] >= 2.2:
                    style_map_f[t] = "Attacking"
                else:
                    style_map_f[t] = "Solid/Compact"
            df_ts["Style"] = df_ts["Team"].map(style_map_f)

        sim_df, avg_sim, pca_df, cluster_labels = compute_similarity(df_ts, feat_all, id_col)
        df_ts["Cluster"] = pca_df["Cluster"].values

        # ── Team selector
        sel_team = st.selectbox(
            f"Select a {'NBA team' if 'NBA' in s_sport else 'football club'}",
            df_ts[id_col].tolist(), key="sim_team_sel")

        sims = top_n_similar(sim_df, sel_team, n_sim)

        # ── KPI strip
        own_row = df_ts[df_ts[id_col]==sel_team].iloc[0]
        kpi_row([
            ("Style",       own_row["Style"],                    None, None),
            ("Play Group",  own_row["Cluster"],                  None, None),
            ("Most Similar",sims.index[0],                       f"{sims.iloc[0]:.3f}", None),
            ("Uniqueness",  f"{1-avg_sim[df_ts[id_col].tolist().index(sel_team)]:.3f}",
             "lower = more unique", None),
        ])

        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        # ── Similar teams cards
        section("🔗", "Most Similar Teams", f"to {sel_team}")
        sim_cols = st.columns(min(n_sim, 5))
        for col, (t, score) in zip(sim_cols, sims.items()):
            tr = df_ts[df_ts[id_col]==t].iloc[0]
            col.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border);
                 border-top:3px solid #00e676;border-radius:10px;padding:1rem;
                 text-align:center">
              <div style="font-family:'Barlow Condensed',sans-serif;font-size:1rem;
                   font-weight:800;color:#f0f4f8;line-height:1.2">{t}</div>
              <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.8rem;
                   font-weight:900;color:#00e676;margin:0.3rem 0">{score:.3f}</div>
              <div style="font-size:0.7rem;color:#4a6077;text-transform:uppercase;
                   letter-spacing:0.08em">similarity</div>
              <div style="margin-top:0.5rem;font-size:0.75rem;color:#8fa3b8">
                Style: <strong style="color:#f5a623">{tr['Style']}</strong>
              </div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)

        # ── Radar comparison: selected + top 2 similar
        compare_teams = [sel_team] + sims.index[:2].tolist()
        section("📡", "Style Radar", f"{sel_team} vs {sims.index[0]} vs {sims.index[1]}")

        # normalize radar
        maxv = [df_ts[f].max() for f in radar_feats]

        col_rad, col_bar = st.columns([3,2])
        with col_rad:
            fig_rad = radar_compare(df_ts, radar_feats, compare_teams, id_col, maxv)
            st.plotly_chart(fig_rad, use_container_width=True)

        with col_bar:
            # Stat delta bar: selected vs top similar
            other = sims.index[0]
            delta_feats = feat_off[:6] if "NBA" in s_sport else feat_off[:6]
            val_sel   = df_ts[df_ts[id_col]==sel_team][delta_feats].iloc[0]
            val_other = df_ts[df_ts[id_col]==other][delta_feats].iloc[0]
            delta     = val_sel - val_other

            colors_delta = ["#00e676" if d >= 0 else "#ff4560" for d in delta.values]
            fig_delta = go.Figure(go.Bar(
                x=delta.values.round(2), y=delta_feats, orientation="h",
                marker_color=colors_delta,
                text=[f"{v:+.2f}" for v in delta.values],
                textposition="outside",
                textfont=dict(color="#8fa3b8", size=9),
            ))
            apply_plotly(fig_delta, 420,
                         f"Δ Stats: {sel_team[:12]} vs {other[:12]}")
            fig_delta.add_vline(x=0, line_color="rgba(139,163,184,0.4)")
            fig_delta.update_layout(
                yaxis=dict(autorange="reversed",
                           tickfont=dict(size=9, color="#8fa3b8")))
            st.plotly_chart(fig_delta, use_container_width=True)

        # ── PCA scatter — all teams
        section("🗺️", "Style Map", "All teams projected in 2D (PCA)")
        pca_df[id_col]    = df_ts[id_col].values
        pca_df["Style"]   = df_ts["Style"].values
        pca_df["Cluster"] = df_ts["Cluster"].values
        pca_df["Highlight"] = pca_df[id_col].apply(
            lambda t: "🎯 Selected" if t == sel_team
            else ("🔗 Similar" if t in sims.index[:3].tolist() else "Other"))

        fig_pca = px.scatter(
            pca_df, x="PC1", y="PC2",
            color="Cluster", text=id_col, symbol="Highlight",
            color_discrete_sequence=["#f5a623","#00d4ff","#00e676","#a78bfa"],
            symbol_map={"🎯 Selected":"star","🔗 Similar":"diamond","Other":"circle"},
            size_max=14,
        )
        fig_pca.update_traces(textposition="top center",
                              textfont=dict(size=8, color="#8fa3b8"),
                              marker=dict(size=10))
        apply_plotly(fig_pca, 500, "")
        fig_pca.update_layout(
            xaxis_title="Offensive dimension (PC1)",
            yaxis_title="Defensive dimension (PC2)",
            legend=dict(orientation="h", y=1.05, x=0,
                        font=dict(color="#8fa3b8",size=10)),
        )
        st.plotly_chart(fig_pca, use_container_width=True)

        # ── Full similarity heatmap
        with st.expander("🔥 Full Similarity Heatmap (all teams)"):
            st.plotly_chart(
                heatmap_fig(sim_df, "Team Style Similarity Matrix"),
                use_container_width=True)

        # ── Stats table
        with st.expander("📋 Full Stats Table"):
            disp_cols = [id_col,"Style","Cluster"] + feat_all[:8]
            st.dataframe(df_ts[disp_cols].sort_values(id_col),
                         use_container_width=True, hide_index=True)


    # ══════════════════════════════════════════════════════════════════════════
    #  PLAYER SIMILARITY
    # ══════════════════════════════════════════════════════════════════════════
    else:
        section("👤", "Player Profile Similarity",
                "Find players with the same statistical DNA")

        if "NBA" in s_sport:
            df_pl = build_nba_player_stats()
            id_col = "Player"

            # Feature groups
            feat_raw  = ["PTS","REB","AST","STL","BLK","TOV"]
            feat_eff  = ["FG%","3P%","FT%","TS%"]
            feat_p36  = ["PTS/36","REB/36","AST/36"]
            feat_phys = ["Height","Weight","MIN"]
            feat_all_p = feat_raw + feat_eff + feat_p36 + feat_phys
            radar_feats_p = ["PTS","REB","AST","STL","BLK","TS%","MIN"]

        else:
            # Football players
            df_pl = get_football_players()
            id_col = "Player"
            df_pl["Height"]   = [181,188,178,175,170,182,186,179,184,181][:len(df_pl)]
            df_pl["Weight"]   = [88, 83, 75, 77, 73, 84, 79, 76, 80, 78][:len(df_pl)]
            df_pl["G/90_def"] = [0.02]*len(df_pl)
            df_pl["Arch"]     = ["FW","FW","MF","MF","FW","FW","MF","FW","MF","FW"][:len(df_pl)]

            feat_raw  = ["Goals","Ast","G+A","Key P"]
            feat_eff  = ["G/90","Rating","Pass%"]
            feat_phys = ["Height","Weight","Apps"]
            feat_all_p = feat_raw + feat_eff + feat_phys
            radar_feats_p = ["Goals","Ast","G/90","Rating","Key P","Pass%"]

        sim_df_p, avg_sim_p, pca_df_p, cl_p = compute_similarity(df_pl, feat_all_p, id_col)

        # ── Tabs: Find Similar / Compare / Archetypes
        tab_find, tab_cmp, tab_arch = st.tabs(
            ["FIND SIMILAR PLAYERS", "HEAD-TO-HEAD COMPARE", "ARCHETYPES MAP"])

        # ── TAB: FIND SIMILAR ─────────────────────────────────────────────
        with tab_find:
            c_sel, c_pos_f = st.columns([3,2])
            with c_sel:
                sel_player = st.selectbox("Select player", df_pl[id_col].tolist(),
                                          key="sim_player_sel")
            with c_pos_f:
                if "NBA" in s_sport:
                    pos_filt = st.multiselect("Filter by position",
                        ["PG","SG","SF","PF","C"], default=[])
                else:
                    pos_filt = st.multiselect("Filter by position",
                        ["FW","MF","DF"], default=[])

            df_filt = df_pl[df_pl["Pos"].isin(pos_filt)] if pos_filt else df_pl
            # recompute sim on filtered
            if pos_filt and sel_player in df_filt[id_col].values:
                sim_df_filt, _, _, _ = compute_similarity(df_filt, feat_all_p, id_col)
                sims_p = top_n_similar(sim_df_filt, sel_player, n_sim)
            else:
                sims_p = top_n_similar(sim_df_p, sel_player, n_sim)

            pr = df_pl[df_pl[id_col]==sel_player].iloc[0]

            kpi_row([
                ("Position",  pr["Pos"],                    None, None),
                ("Archetype", pr.get("Archetype", pr.get("Arch","—")), None, None),
                ("Most Similar", sims_p.index[0],           f"{sims_p.iloc[0]:.3f}", None),
                ("Profile Score", f"{sims_p.mean():.3f}",  "avg similarity", None),
            ])

            # ── Similar player cards
            section("🔗", "Most Similar Players", f"to {sel_player}")
            card_cols = st.columns(min(n_sim, 5))
            for col, (pl, score) in zip(card_cols, sims_p.items()):
                pr2 = df_pl[df_pl[id_col]==pl].iloc[0]
                col.markdown(f"""
                <div style="background:var(--bg-card);border:1px solid var(--border);
                     border-top:3px solid #00d4ff;border-radius:10px;padding:1rem;
                     text-align:center">
                  <div style="font-family:'Barlow Condensed',sans-serif;font-size:0.95rem;
                       font-weight:800;color:#f0f4f8;line-height:1.2">{pl}</div>
                  <div style="font-size:0.72rem;color:#8fa3b8">{pr2['Team']} · {pr2['Pos']}</div>
                  <div style="font-family:'Barlow Condensed',sans-serif;font-size:1.8rem;
                       font-weight:900;color:#00d4ff;margin:0.3rem 0">{score:.3f}</div>
                  <div style="font-size:0.68rem;color:#4a6077;text-transform:uppercase;
                       letter-spacing:0.08em">similarity</div>
                  <div style="margin-top:0.5rem;font-size:0.75rem;color:#8fa3b8">
                    {'Arch: <strong style="color:#f5a623">'+pr2.get("Archetype",pr2.get("Arch","—"))+'</strong>' if "NBA" in s_sport else f'Goals: <strong style="color:#f5a623">{pr2.get("Goals","-")}</strong>'}
                  </div>
                </div>""", unsafe_allow_html=True)

            st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

            # ── Radar: selected vs top 2 similar
            compare_pl = [sel_player] + sims_p.index[:2].tolist()
            section("📡", "Profile Radar", " vs ".join(compare_pl[:2]))

            maxv_p = [df_pl[f].max() for f in radar_feats_p]
            col_r2, col_tbl_p = st.columns([3,2])
            with col_r2:
                fig_r2 = radar_compare(df_pl, radar_feats_p, compare_pl, id_col, maxv_p)
                st.plotly_chart(fig_r2, use_container_width=True)
            with col_tbl_p:
                show_cols = [id_col,"Pos","Team"] + feat_raw[:4] + feat_eff[:2]
                comp_df = df_pl[df_pl[id_col].isin(compare_pl)][show_cols]
                st.dataframe(comp_df, use_container_width=True, hide_index=True)

            # ── Delta bar vs most similar
            other_p = sims_p.index[0]
            delta_f = feat_raw[:4] + feat_eff[:3]
            v1 = df_pl[df_pl[id_col]==sel_player][delta_f].iloc[0]
            v2 = df_pl[df_pl[id_col]==other_p][delta_f].iloc[0]
            d  = v1 - v2
            fig_dp = go.Figure(go.Bar(
                x=d.values.round(3), y=delta_f, orientation="h",
                marker_color=["#00e676" if x>=0 else "#ff4560" for x in d.values],
                text=[f"{x:+.3f}" for x in d.values], textposition="outside",
                textfont=dict(color="#8fa3b8", size=9),
            ))
            apply_plotly(fig_dp, 340,
                         f"Δ Stats: {sel_player.split()[-1]} vs {other_p.split()[-1]}")
            fig_dp.add_vline(x=0, line_color="rgba(139,163,184,0.35)")
            fig_dp.update_layout(yaxis=dict(autorange="reversed",
                                            tickfont=dict(size=9,color="#8fa3b8")))
            st.plotly_chart(fig_dp, use_container_width=True)

        # ── TAB: HEAD-TO-HEAD ─────────────────────────────────────────────
        with tab_cmp:
            section("⚔️", "Head-to-Head Comparison")
            c1, c2 = st.columns(2)
            with c1:
                p1 = st.selectbox("Player A", df_pl[id_col].tolist(),
                                  index=0, key="hth_p1")
            with c2:
                p2 = st.selectbox("Player B", df_pl[id_col].tolist(),
                                  index=1, key="hth_p2")

            r1 = df_pl[df_pl[id_col]==p1].iloc[0]
            r2 = df_pl[df_pl[id_col]==p2].iloc[0]
            sim_score = sim_df_p.loc[p1, p2] if p1 in sim_df_p.index and p2 in sim_df_p.index else 0

            # Similarity badge
            sim_color = "#00e676" if sim_score > 0.85 else ("#f5a623" if sim_score > 0.7 else "#ff4560")
            sim_label = "Very Similar" if sim_score > 0.85 else ("Similar" if sim_score > 0.7 else "Different Profiles")
            st.markdown(f"""
            <div style="text-align:center;padding:0.8rem;background:var(--bg-card);
                 border:1px solid {sim_color};border-radius:10px;margin-bottom:1rem">
              <span style="font-family:'Barlow Condensed',sans-serif;font-size:2.5rem;
                    font-weight:900;color:{sim_color}">{sim_score:.3f}</span>
              <span style="font-size:0.8rem;color:#8fa3b8;margin-left:0.5rem">
                similarity · {sim_label}
              </span>
            </div>""", unsafe_allow_html=True)

            # Side-by-side stats
            compare_two = [p1, p2]
            maxv_2 = [df_pl[f].max() for f in radar_feats_p]

            col_rr, col_sb = st.columns([2,3])
            with col_rr:
                fig_hth = radar_compare(df_pl, radar_feats_p, compare_two, id_col, maxv_2)
                st.plotly_chart(fig_hth, use_container_width=True)

            with col_sb:
                compare_stats = [id_col,"Pos","Team"] + feat_raw + feat_eff
                st.dataframe(
                    df_pl[df_pl[id_col].isin([p1,p2])][compare_stats],
                    use_container_width=True, hide_index=True)

            # Grouped bar: raw stats side by side
            bar_feats = feat_raw[:5]
            fig_gb = go.Figure()
            for pl_, color_ in [(p1,"#f5a623"),(p2,"#00d4ff")]:
                r = df_pl[df_pl[id_col]==pl_].iloc[0]
                fig_gb.add_trace(go.Bar(
                    name=pl_, x=bar_feats,
                    y=[r[f] for f in bar_feats],
                    marker_color=color_,
                    text=[f"{r[f]:.1f}" for f in bar_feats],
                    textposition="outside",
                    textfont=dict(color="#8fa3b8", size=10),
                ))
            fig_gb.update_layout(barmode="group")
            apply_plotly(fig_gb, 340, "Raw Stats Comparison")
            st.plotly_chart(fig_gb, use_container_width=True)

        # ── TAB: ARCHETYPES MAP ───────────────────────────────────────────
        with tab_arch:
            section("🗺️", "Archetypes Map",
                    "All players clustered by statistical profile (PCA 2D)")

            pca_df_p[id_col] = df_pl[id_col].values
            pca_df_p["Pos"]  = df_pl["Pos"].values
            pca_df_p["Arch"] = df_pl.get("Archetype", df_pl.get("Arch", df_pl["Pos"])).values
            pca_df_p["PTS"]  = df_pl["PTS"].values if "PTS" in df_pl.columns else df_pl["Goals"].values

            fig_arch = px.scatter(
                pca_df_p, x="PC1", y="PC2",
                color="Cluster", text=id_col, size="PTS",
                color_discrete_sequence=["#f5a623","#00d4ff","#00e676","#a78bfa"],
                size_max=20,
                hover_data={"Arch":True, "Pos":True, "PC1":False, "PC2":False},
            )
            fig_arch.update_traces(
                textposition="top center",
                textfont=dict(size=8, color="#8fa3b8"),
            )
            apply_plotly(fig_arch, 560, "")
            fig_arch.update_layout(
                xaxis_title="Scoring / Efficiency dimension (PC1)",
                yaxis_title="Playmaking / Defense dimension (PC2)",
                legend=dict(orientation="h", y=1.04, x=0,
                            font=dict(color="#8fa3b8", size=11)),
            )
            st.plotly_chart(fig_arch, use_container_width=True)

            # Archetype summary table
            if "Archetype" in df_pl.columns:
                arch_sum = (df_pl.groupby("Archetype")
                               .agg({"PTS":"mean","REB":"mean","AST":"mean",
                                     "TS%":"mean","Player":"count"})
                               .round(2).reset_index()
                               .rename(columns={"Player":"N"}))
                section("📋", "Archetype Averages")
                st.dataframe(arch_sum, use_container_width=True, hide_index=True)

            # Full similarity heatmap
            with st.expander("🔥 Full Player Similarity Heatmap"):
                st.plotly_chart(
                    heatmap_fig(sim_df_p, "Player Profile Similarity Matrix"),
                    use_container_width=True)
