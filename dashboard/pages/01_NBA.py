"""
NBA Analytics Page
Standings, player stats, game trends, performance KPIs.
Runs in demo mode (synthetic data) when Snowflake is not configured.
"""
import random
from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="NBA Analytics", page_icon="🏀", layout="wide")

NBA_TEAMS = [
    "Boston Celtics","Oklahoma City Thunder","Denver Nuggets","Minnesota Timberwolves",
    "Cleveland Cavaliers","Los Angeles Lakers","Golden State Warriors","Miami Heat",
    "Milwaukee Bucks","Phoenix Suns","Dallas Mavericks","Philadelphia 76ers",
    "Memphis Grizzlies","New York Knicks","Sacramento Kings",
]
NBA_PLAYERS = [
    ("LeBron James","Los Angeles Lakers","SF",25.8,7.3,8.1),
    ("Stephen Curry","Golden State Warriors","PG",26.4,4.5,5.1),
    ("Giannis Antetokounmpo","Milwaukee Bucks","PF",30.4,11.5,6.5),
    ("Luka Doncic","Dallas Mavericks","PG",33.9,9.2,9.8),
    ("Nikola Jokic","Denver Nuggets","C",26.4,12.4,9.0),
    ("Kevin Durant","Phoenix Suns","SF",27.1,6.6,5.0),
    ("Joel Embiid","Philadelphia 76ers","C",34.7,11.0,5.6),
    ("Jayson Tatum","Boston Celtics","SF",26.9,8.1,4.9),
    ("Anthony Davis","Los Angeles Lakers","C",24.7,12.6,3.5),
    ("Damian Lillard","Milwaukee Bucks","PG",24.3,4.4,7.3),
    ("Shai Gilgeous-Alexander","Oklahoma City Thunder","PG",30.1,5.5,6.2),
    ("Donovan Mitchell","Cleveland Cavaliers","PG",28.0,4.4,6.1),
]


@st.cache_data(ttl=3600)
def load_standings():
    random.seed(42)
    rows = []
    for i, team in enumerate(NBA_TEAMS):
        wins = random.randint(30, 65)
        rows.append({
            "Rank": i+1, "Team": team, "W": wins, "L": 82-wins,
            "Win%": round(wins/82, 3),
            "PTS/G": round(random.uniform(108, 122), 1),
            "OPP PTS/G": round(random.uniform(105, 118), 1),
            "Net RTG": round(random.uniform(-4, 10), 1),
            "Form": "".join(random.choices(["W","L"], weights=[wins, 82-wins], k=5)),
            "Conference": random.choice(["East","West"]),
        })
    df = pd.DataFrame(rows).sort_values("W", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    return df


@st.cache_data(ttl=3600)
def load_player_stats():
    rows = []
    for name, team, pos, pts, reb, ast in NBA_PLAYERS:
        rows.append({
            "Player": name, "Team": team, "Pos": pos,
            "PTS": pts, "REB": reb, "AST": ast,
            "FG%": round(random.uniform(0.44, 0.58), 3),
            "3P%": round(random.uniform(0.33, 0.43), 3),
            "FT%": round(random.uniform(0.72, 0.92), 3),
            "MIN": round(random.uniform(32, 38), 1),
            "Games": random.randint(55, 72),
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=3600)
def load_game_trends(team, n=20):
    random.seed(hash(team) % 1000)
    dates = sorted([date.today() - timedelta(days=i*2) for i in range(n)])
    scores = [random.randint(98, 130) for _ in range(n)]
    opp    = [random.randint(98, 126) for _ in range(n)]
    opps   = random.choices([t for t in NBA_TEAMS if t != team], k=n)
    return pd.DataFrame({
        "Date": dates, "PTS": scores, "OPP PTS": opp,
        "Opponent": opps,
        "Result": ["W" if s > o else "L" for s, o in zip(scores, opp)],
    })


# ── Page ───────────────────────────────────────────────────────────────────
st.title("🏀 NBA Analytics")
st.markdown("Season 2023–24 · Updated daily via Airflow pipeline")

tab1, tab2, tab3 = st.tabs(["📊 Standings", "👤 Players", "📈 Team Trends"])

with tab1:
    standings = load_standings()
    conf = st.selectbox("Conference", ["All","East","West"])
    df_show = standings if conf == "All" else standings[standings["Conference"] == conf].copy()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Best Win%", f"{df_show['Win%'].max():.3f}", df_show.iloc[0]["Team"])
    c2.metric("Avg PTS/G (Top 5)", f"{df_show.head(5)['PTS/G'].mean():.1f}")
    c3.metric("Highest Net RTG", f"+{df_show['Net RTG'].max():.1f}")
    c4.metric("Teams", len(df_show))

    fig = px.bar(df_show.sort_values("Win%", ascending=True),
        x="Win%", y="Team", orientation="h", color="Win%",
        color_continuous_scale=["#c0392b","#f39c12","#27ae60"],
        title="Team Win Percentage", height=500)
    fig.update_layout(plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
                      font_color="#f0f0f0", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.scatter(df_show, x="OPP PTS/G", y="PTS/G", size="W", color="Win%",
        text="Team", color_continuous_scale="RdYlGn", height=480,
        title="Offensive vs Defensive Efficiency",
        labels={"PTS/G": "Points Scored / Game", "OPP PTS/G": "Points Allowed / Game"})
    fig2.update_traces(textposition="top center", textfont_size=9)
    fig2.add_vline(x=df_show["OPP PTS/G"].mean(), line_dash="dash", line_color="#888")
    fig2.add_hline(y=df_show["PTS/G"].mean(), line_dash="dash", line_color="#888")
    fig2.update_layout(plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a", font_color="#f0f0f0")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(df_show[["Rank","Team","W","L","Win%","PTS/G","OPP PTS/G","Net RTG","Form"]],
                 use_container_width=True, hide_index=True)

with tab2:
    players = load_player_stats()
    col_a, col_b = st.columns([3,4])
    with col_a:
        kpi = st.selectbox("Sort by", ["PTS","REB","AST","FG%","3P%","MIN"])
    with col_b:
        pos_filter = st.multiselect("Position", ["PG","SG","SF","PF","C"],
                                    default=["PG","SG","SF","PF","C"])
    df_p = players[players["Pos"].isin(pos_filter)].sort_values(kpi, ascending=False)

    c1, c2, c3 = st.columns(3)
    c1.metric(f"Top {kpi}", f"{df_p.iloc[0][kpi]}", df_p.iloc[0]['Player'])
    c2.metric(f"Avg {kpi}", f"{df_p[kpi].mean():.1f}")
    c3.metric("Players", len(df_p))

    fig3 = px.scatter(df_p, x="AST", y="PTS", size="REB", color="Pos", text="Player",
        title="Points vs Assists (bubble = Rebounds)", height=480,
        color_discrete_sequence=px.colors.qualitative.Bold)
    fig3.update_traces(textposition="top center", textfont_size=8)
    fig3.update_layout(plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a", font_color="#f0f0f0")
    st.plotly_chart(fig3, use_container_width=True)

    sel = st.selectbox("Radar chart — select player", df_p["Player"].tolist())
    p   = df_p[df_p["Player"] == sel].iloc[0]
    cats = ["PTS","REB","AST","FG%","3P%","FT%"]
    maxv = {"PTS":40,"REB":15,"AST":12,"FG%":1,"3P%":1,"FT%":1}
    vals = [p[c]/maxv[c] for c in cats]
    fig4 = go.Figure(go.Scatterpolar(r=vals+[vals[0]], theta=cats+[cats[0]],
        fill="toself", fillcolor="rgba(52,152,219,0.3)",
        line=dict(color="#3498db", width=2), name=sel))
    fig4.update_layout(polar=dict(bgcolor="#1e1e2e",
        radialaxis=dict(visible=True, range=[0,1], color="#888"),
        angularaxis=dict(color="#f0f0f0")),
        paper_bgcolor="#0f0f1a", font_color="#f0f0f0",
        title=f"Performance Radar — {sel}", height=420)
    st.plotly_chart(fig4, use_container_width=True)
    st.dataframe(df_p, use_container_width=True, hide_index=True)

with tab3:
    sel_team = st.selectbox("Select team", NBA_TEAMS)
    n_games  = st.slider("Last N games", 5, 30, 15)
    trends   = load_game_trends(sel_team, n_games)
    wins     = (trends["Result"] == "W").sum()
    losses   = (trends["Result"] == "L").sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Wins",  wins)
    c2.metric("Losses", losses)
    c3.metric("Avg PTS", f"{trends['PTS'].mean():.1f}")
    c4.metric("Avg PTS allowed", f"{trends['OPP PTS'].mean():.1f}",
              f"{trends['PTS'].mean()-trends['OPP PTS'].mean():+.1f}")

    fig5 = go.Figure()
    fig5.add_trace(go.Scatter(x=trends["Date"], y=trends["PTS"], name=sel_team,
        line=dict(color="#3498db", width=2.5), mode="lines+markers",
        marker=dict(color=["#27ae60" if r=="W" else "#c0392b" for r in trends["Result"]], size=10)))
    fig5.add_trace(go.Scatter(x=trends["Date"], y=trends["OPP PTS"], name="Opponent",
        line=dict(color="#e74c3c", width=2, dash="dot"), mode="lines+markers",
        marker=dict(size=7, color="#e74c3c")))
    fig5.update_layout(title=f"{sel_team} — Score Trend",
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a", font_color="#f0f0f0",
        legend=dict(orientation="h", y=1.1), height=420)
    st.plotly_chart(fig5, use_container_width=True)

    fig6 = go.Figure(go.Pie(labels=["Wins","Losses"], values=[wins, losses], hole=0.55,
        marker=dict(colors=["#27ae60","#c0392b"])))
    fig6.update_layout(title="W/L Distribution", paper_bgcolor="#0f0f1a",
                       font_color="#f0f0f0", height=300)
    col_d, col_t = st.columns([2,3])
    with col_d:
        st.plotly_chart(fig6, use_container_width=True)
    with col_t:
        st.dataframe(trends[["Date","Opponent","PTS","OPP PTS","Result"]],
                     use_container_width=True, hide_index=True)
