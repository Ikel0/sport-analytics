"""
Football Analytics Page
Visualizes standings, player stats, match trends for Premier League,
Ligue 1, La Liga and Serie A.
"""

import random
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Football Analytics", page_icon="⚽", layout="wide")

# ── Reference data ─────────────────────────────────────────────────────────

LEAGUES = {
    "Premier League 🏴󠁧󠁢󠁥󠁮󠁧󠁿": {
        "teams": [
            "Manchester City", "Arsenal", "Liverpool", "Aston Villa",
            "Tottenham", "Chelsea", "Newcastle", "Manchester United",
            "West Ham", "Brighton", "Crystal Palace", "Brentford",
            "Fulham", "Wolves", "Everton", "Nottingham Forest",
        ],
        "color": "#3d195b",
    },
    "Ligue 1 🇫🇷": {
        "teams": [
            "Paris Saint-Germain", "Monaco", "Brest", "Lille",
            "Nice", "Lyon", "Lens", "Marseille",
            "Rennes", "Reims", "Montpellier", "Strasbourg",
        ],
        "color": "#003189",
    },
    "La Liga 🇪🇸": {
        "teams": [
            "Real Madrid", "Barcelona", "Girona", "Atletico Madrid",
            "Athletic Bilbao", "Real Sociedad", "Real Betis", "Valencia",
            "Villarreal", "Sevilla", "Celta Vigo", "Getafe",
        ],
        "color": "#c60b1e",
    },
    "Serie A 🇮🇹": {
        "teams": [
            "Inter Milan", "AC Milan", "Juventus", "Atalanta",
            "Bologna", "Roma", "Lazio", "Fiorentina",
            "Napoli", "Torino", "Monza", "Genoa",
        ],
        "color": "#009246",
    },
}

FOOTBALL_PLAYERS = [
    ("Erling Haaland",       "Manchester City",   "FW", 36, 8,  3),
    ("Mohamed Salah",        "Liverpool",         "FW", 28, 12, 6),
    ("Bukayo Saka",          "Arsenal",           "MF", 20, 14, 5),
    ("Phil Foden",           "Manchester City",   "MF", 19, 11, 4),
    ("Kylian Mbappé",        "Paris Saint-Germain","FW",27,  9,  6),
    ("Vinicius Junior",      "Real Madrid",       "FW", 24, 10, 5),
    ("Jude Bellingham",      "Real Madrid",       "MF", 19, 9,  8),
    ("Lautaro Martinez",     "Inter Milan",       "FW", 25, 7,  4),
    ("Luka Modric",          "Real Madrid",       "MF",  8, 6, 10),
    ("Rodri",                "Manchester City",   "MF",  7, 12,  8),
    ("Rafael Leao",          "AC Milan",          "FW", 16, 9,  5),
    ("Victor Osimhen",       "Napoli",            "FW", 26, 5,  3),
]


@st.cache_data(ttl=3600)
def load_standings(league: str) -> pd.DataFrame:
    random.seed(hash(league) % 9999)
    teams = LEAGUES[league]["teams"]
    rows = []
    for i, team in enumerate(teams):
        played = random.randint(32, 38)
        wins   = random.randint(8, played - 5)
        draws  = random.randint(3, min(10, played - wins))
        losses = played - wins - draws
        gf     = wins * random.randint(2, 3) + draws
        ga     = losses * random.randint(1, 2) + draws
        pts    = wins * 3 + draws
        rows.append({
            "Rank":   i + 1,
            "Team":   team,
            "Played": played,
            "W":      wins,
            "D":      draws,
            "L":      losses,
            "GF":     gf,
            "GA":     ga,
            "GD":     gf - ga,
            "Pts":    pts,
            "Win%":   round(wins / played, 3),
            "G/Game": round(gf / played, 2),
            "Form":   "".join(random.choices(["W", "D", "L"],
                                             weights=[wins, draws, losses], k=5)),
        })
    df = (pd.DataFrame(rows)
            .sort_values("Pts", ascending=False)
            .reset_index(drop=True))
    df["Rank"] = df.index + 1
    return df


@st.cache_data(ttl=3600)
def load_player_stats() -> pd.DataFrame:
    random.seed(77)
    rows = []
    for name, team, pos, goals, assists, key_passes in FOOTBALL_PLAYERS:
        apps = random.randint(28, 36)
        mins = apps * random.randint(75, 90)
        rows.append({
            "Player":      name,
            "Team":        team,
            "Pos":         pos,
            "Apps":        apps,
            "Goals":       goals,
            "Assists":     assists,
            "Key Passes":  key_passes,
            "G+A":         goals + assists,
            "Mins":        mins,
            "G/90":        round(goals / (mins / 90), 2),
            "Rating":      round(random.uniform(7.0, 8.8), 2),
            "Pass Acc%":   round(random.uniform(78, 93), 1),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def load_match_trends(team: str, n: int = 15) -> pd.DataFrame:
    random.seed(hash(team) % 5555)
    dates = sorted([date.today() - timedelta(days=i * 7) for i in range(n)])
    gf    = [random.randint(0, 4) for _ in range(n)]
    ga    = [random.randint(0, 3) for _ in range(n)]
    res   = ["W" if f > a else ("D" if f == a else "L") for f, a in zip(gf, ga)]
    opp_teams = random.choices(
        [t for league in LEAGUES.values() for t in league["teams"] if t != team],
        k=n,
    )
    return pd.DataFrame({
        "Date":     dates,
        "Opponent": opp_teams,
        "GF":       gf,
        "GA":       ga,
        "Result":   res,
        "Clean Sheet": [1 if a == 0 else 0 for a in ga],
    })


# ── Layout ─────────────────────────────────────────────────────────────────

st.title("⚽ Football Analytics")
st.markdown("Leagues: Premier League · Ligue 1 · La Liga · Serie A · Season 2023–24")

tab1, tab2, tab3 = st.tabs(["📊 Standings", "👤 Players", "📈 Team Trends"])

# ── TAB 1: STANDINGS ───────────────────────────────────────────────────────
with tab1:
    selected_league = st.selectbox("League", list(LEAGUES.keys()))
    standings = load_standings(selected_league)

    c1, c2, c3, c4 = st.columns(4)
    leader = standings.iloc[0]
    c1.metric("🥇 Leader", leader["Team"], f"{leader['Pts']} pts")
    c2.metric("Avg Goals/Game", f"{standings['G/Game'].mean():.2f}")
    c3.metric("Most Goals", f"{standings['GF'].max()}", standings.loc[standings['GF'].idxmax(), 'Team'])
    c4.metric("Best Defense", standings.loc[standings['GA'].idxmin(), 'Team'],
              f"{standings['GA'].min()} conceded")

    col_l, col_r = st.columns(2)

    with col_l:
        fig_pts = px.bar(
            standings.sort_values("Pts", ascending=True),
            x="Pts", y="Team", orientation="h",
            color="Pts",
            color_continuous_scale=["#c0392b", "#f39c12", "#27ae60"],
            title="Points Table",
            height=480,
        )
        fig_pts.update_layout(
            plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
            font_color="#f0f0f0", coloraxis_showscale=False,
        )
        st.plotly_chart(fig_pts, use_container_width=True)

    with col_r:
        fig_gd = px.scatter(
            standings,
            x="GA", y="GF",
            size="Pts", color="Win%",
            text="Team",
            color_continuous_scale="RdYlGn",
            title="Attack vs Defence (bubble = Points)",
            labels={"GF": "Goals Scored", "GA": "Goals Conceded"},
            height=480,
        )
        fig_gd.update_traces(textposition="top center", textfont_size=8)
        fig_gd.add_vline(x=standings["GA"].mean(), line_dash="dash", line_color="#888")
        fig_gd.add_hline(y=standings["GF"].mean(), line_dash="dash", line_color="#888")
        fig_gd.update_layout(
            plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a", font_color="#f0f0f0"
        )
        st.plotly_chart(fig_gd, use_container_width=True)

    # W/D/L stacked bar
    fig_wdl = go.Figure()
    for result, color, label in [("W", "#27ae60", "Wins"),
                                   ("D", "#f39c12", "Draws"),
                                   ("L", "#c0392b", "Losses")]:
        col_name = {"W": "W", "D": "D", "L": "L"}[result]
        fig_wdl.add_trace(go.Bar(
            name=label,
            x=standings["Team"],
            y=standings[col_name],
            marker_color=color,
        ))
    fig_wdl.update_layout(
        barmode="stack",
        title="Win / Draw / Loss Distribution",
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#f0f0f0",
        xaxis_tickangle=-35,
        height=380,
    )
    st.plotly_chart(fig_wdl, use_container_width=True)

    st.dataframe(
        standings[["Rank", "Team", "Played", "W", "D", "L",
                   "GF", "GA", "GD", "Pts", "Form"]],
        use_container_width=True, hide_index=True,
    )

# ── TAB 2: PLAYERS ─────────────────────────────────────────────────────────
with tab2:
    players = load_player_stats()

    col_a, col_b = st.columns([3, 4])
    with col_a:
        kpi = st.selectbox("Sort by", ["Goals", "Assists", "G+A", "Rating", "G/90", "Key Passes"])
    with col_b:
        pos_filter = st.multiselect("Position", ["FW", "MF", "DF"], default=["FW", "MF"])

    df_p = players[players["Pos"].isin(pos_filter)].sort_values(kpi, ascending=False)

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Top {kpi}", f"{df_p.iloc[0][kpi]}", df_p.iloc[0]["Player"])
    c2.metric(f"Avg {kpi}", f"{df_p[kpi].mean():.2f}")
    c3.metric("Players shown", len(df_p))

    # Goals vs Assists scatter
    fig_ga = px.scatter(
        df_p,
        x="Assists", y="Goals",
        size="Apps",
        color="Rating",
        text="Player",
        color_continuous_scale="Viridis",
        title="Goals vs Assists (bubble = Appearances)",
        height=460,
    )
    fig_ga.update_traces(textposition="top center", textfont_size=8)
    fig_ga.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a", font_color="#f0f0f0"
    )
    st.plotly_chart(fig_ga, use_container_width=True)

    # Top scorers bar
    top_scorers = df_p.nlargest(10, "Goals")
    fig_scorers = px.bar(
        top_scorers,
        x="Player", y="Goals",
        color="Goals",
        color_continuous_scale="Oranges",
        title="Top 10 Scorers",
        height=360,
    )
    fig_scorers.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#f0f0f0", coloraxis_showscale=False,
        xaxis_tickangle=-30,
    )
    st.plotly_chart(fig_scorers, use_container_width=True)

    st.dataframe(df_p, use_container_width=True, hide_index=True)

# ── TAB 3: TEAM TRENDS ─────────────────────────────────────────────────────
with tab3:
    all_teams = sorted(set(
        t for league in LEAGUES.values() for t in league["teams"]
    ))
    selected_team = st.selectbox("Select team", all_teams)
    n_matches = st.slider("Last N matches", 5, 25, 12)

    trends = load_match_trends(selected_team, n_matches)

    wins   = (trends["Result"] == "W").sum()
    draws  = (trends["Result"] == "D").sum()
    losses = (trends["Result"] == "L").sum()
    clean_sheets = trends["Clean Sheet"].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Wins", wins)
    c2.metric("Draws", draws)
    c3.metric("Losses", losses)
    c4.metric("Clean Sheets", int(clean_sheets))

    # Goals scored/conceded timeline
    fig_goals = go.Figure()
    fig_goals.add_trace(go.Bar(
        x=trends["Date"], y=trends["GF"],
        name="Goals Scored",
        marker_color="#27ae60",
    ))
    fig_goals.add_trace(go.Bar(
        x=trends["Date"], y=[-g for g in trends["GA"]],
        name="Goals Conceded",
        marker_color="#c0392b",
    ))
    fig_goals.update_layout(
        barmode="relative",
        title=f"{selected_team} — Goals Scored vs Conceded",
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#f0f0f0",
        xaxis_title="Date",
        yaxis_title="Goals",
        legend=dict(orientation="h", y=1.1),
        height=380,
    )
    st.plotly_chart(fig_goals, use_container_width=True)

    # Cumulative points
    pts_map = {"W": 3, "D": 1, "L": 0}
    trends["Match Pts"] = trends["Result"].map(pts_map)
    trends["Cumulative Pts"] = trends["Match Pts"].cumsum()

    fig_cum = px.line(
        trends, x="Date", y="Cumulative Pts",
        title="Cumulative Points Over Season Period",
        markers=True,
        color_discrete_sequence=["#3498db"],
        height=320,
    )
    fig_cum.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a", font_color="#f0f0f0"
    )
    st.plotly_chart(fig_cum, use_container_width=True)

    col_pie, col_tbl = st.columns([2, 3])
    with col_pie:
        fig_pie = go.Figure(go.Pie(
            labels=["Wins", "Draws", "Losses"],
            values=[wins, draws, losses],
            hole=0.5,
            marker=dict(colors=["#27ae60", "#f39c12", "#c0392b"]),
        ))
        fig_pie.update_layout(
            paper_bgcolor="#0f0f1a", font_color="#f0f0f0",
            title="Result Distribution", height=300,
        )
        st.plotly_chart(fig_pie, use_container_width=True)
    with col_tbl:
        st.dataframe(
            trends[["Date", "Opponent", "GF", "GA", "Result"]],
            use_container_width=True, hide_index=True,
        )
