"""
Recommendation Engine Page
Interactive demo of the content-based sport recommender.
"""

import random
import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

sys.path.insert(0, str(Path(__file__).parents[2]))

from models.recommender import ContentItem, SportRecommender, UserProfile
from models.train import (
    FOOTBALL_TEAMS, NBA_PLAYERS, NBA_TEAMS, FOOTBALL_PLAYERS, build_catalog,
)

st.set_page_config(page_title="Recommendations", page_icon="🤖", layout="wide")


@st.cache_resource
def get_recommender() -> SportRecommender:
    """Load or train the recommender (cached across sessions)."""
    model_path = Path("models/recommender.pkl")
    if model_path.exists():
        import joblib
        return joblib.load(model_path)
    # Train on the fly if no saved model
    catalog = build_catalog()
    rec = SportRecommender()
    rec.fit(catalog)
    return rec


@st.cache_data(ttl=3600)
def get_catalog_df() -> pd.DataFrame:
    catalog = build_catalog()
    return pd.DataFrame([{
        "content_id":   c.content_id,
        "content_type": c.content_type,
        "sport":        c.sport,
        "team":         c.team,
        "player":       c.player,
        "league":       c.league,
        "season":       c.season,
        "popularity":   c.popularity_score,
        "recency":      c.recency_score,
    } for c in catalog])


# ── Layout ─────────────────────────────────────────────────────────────────

st.title("🤖 Sport Content Recommender")
st.markdown(
    "Content-based filtering engine — personalises your sport feed "
    "based on preferences and consultation history."
)

recommender = get_recommender()
catalog_df  = get_catalog_df()

st.markdown("---")

# ── User Profile Builder ───────────────────────────────────────────────────
st.subheader("👤 Build Your Profile")

col1, col2 = st.columns(2)

with col1:
    st.markdown("**Sport Preferences**")
    nba_pref = st.slider("🏀 NBA interest", 0.0, 1.0, 0.6, 0.05)
    football_pref = round(1 - nba_pref, 2)
    st.caption(f"⚽ Football interest: {football_pref}")

    st.markdown("**Favorite NBA Teams**")
    fav_nba_teams = st.multiselect(
        "NBA Teams", NBA_TEAMS,
        default=["Los Angeles Lakers", "Boston Celtics"],
    )

    fav_nba_players = st.multiselect(
        "NBA Players",
        [p[0] for p in NBA_PLAYERS],
        default=["LeBron James", "Stephen Curry"],
    )

with col2:
    st.markdown("**Favorite Football Teams**")
    all_football_teams = sorted(set(
        t for teams in FOOTBALL_TEAMS.values() for t in teams
    ))
    fav_football_teams = st.multiselect(
        "Football Teams", all_football_teams,
        default=["Paris Saint-Germain", "Real Madrid"],
    )

    fav_football_players = st.multiselect(
        "Football Players",
        [p[0] for p in FOOTBALL_PLAYERS],
        default=["Kylian Mbappé", "Erling Haaland"],
    )

    st.markdown("**Consultation History (simulate)**")
    n_history = st.slider("Number of past consultations", 0, 20, 8)
    # Randomly pick history items from preferred sport
    random.seed(42)
    history_pool = catalog_df[
        catalog_df["sport"] == ("nba" if nba_pref >= 0.5 else "football")
    ]["content_id"].tolist()
    consultation_history = random.sample(
        history_pool, min(n_history, len(history_pool))
    )

# ── Recommendation parameters ─────────────────────────────────────────────
st.markdown("---")
st.subheader("⚙️ Recommendation Settings")

col_a, col_b, col_c = st.columns(3)
with col_a:
    n_recs = st.number_input("Number of recommendations", 5, 30, 10)
with col_b:
    sport_filter = st.selectbox("Filter by sport", ["All", "NBA", "Football"])
with col_c:
    exclude_seen = st.checkbox("Exclude already-seen content", value=True)

# ── Generate ──────────────────────────────────────────────────────────────
if st.button("🎯 Generate Recommendations", type="primary"):

    profile = UserProfile(
        user_id="dashboard_user",
        sport_preferences={"nba": nba_pref, "football": football_pref},
        favorite_teams=fav_nba_teams + fav_football_teams,
        favorite_players=fav_nba_players + fav_football_players,
        consultation_history=consultation_history,
    )

    sport_arg = None if sport_filter == "All" else sport_filter.lower()

    with st.spinner("Computing recommendations..."):
        recs = recommender.recommend(
            profile,
            n=n_recs,
            sport_filter=sport_arg,
            exclude_seen=exclude_seen,
        )

    st.success(f"✅ {len(recs)} recommendations generated")
    st.markdown("---")

    # ── KPIs
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Recommendations", len(recs))
    c2.metric("NBA items", (recs["sport"] == "nba").sum())
    c3.metric("Football items", (recs["sport"] == "football").sum())
    c4.metric("Avg Score", f"{recs['similarity_score'].mean():.3f}")

    col_chart, col_table = st.columns([3, 2])

    with col_chart:
        # Bar chart — similarity scores
        fig_recs = px.bar(
            recs.sort_values("similarity_score"),
            x="similarity_score",
            y="content_id",
            orientation="h",
            color="sport",
            color_discrete_map={"nba": "#3498db", "football": "#27ae60"},
            title="Recommendation Scores",
            labels={"similarity_score": "Similarity Score", "content_id": "Content"},
            height=420,
        )
        fig_recs.update_layout(
            plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
            font_color="#f0f0f0",
        )
        st.plotly_chart(fig_recs, use_container_width=True)

    with col_table:
        # Formatted recommendations table
        display = recs[["content_id", "content_type", "sport",
                         "team", "player", "similarity_score"]].copy()
        display["similarity_score"] = display["similarity_score"].round(4)
        display.columns = ["ID", "Type", "Sport", "Team", "Player", "Score"]
        st.dataframe(display, use_container_width=True, hide_index=True)

    # ── Content type breakdown donut
    type_counts = recs["content_type"].value_counts().reset_index()
    type_counts.columns = ["Type", "Count"]
    fig_type = go.Figure(go.Pie(
        labels=type_counts["Type"],
        values=type_counts["Count"],
        hole=0.5,
        marker=dict(colors=["#3498db", "#e74c3c", "#f39c12", "#9b59b6"]),
    ))
    fig_type.update_layout(
        title="Content Type Distribution",
        paper_bgcolor="#0f0f1a", font_color="#f0f0f0", height=300,
    )
    st.plotly_chart(fig_type, use_container_width=True)

    # ── Similar content explorer
    st.markdown("---")
    st.subheader("🔍 Similar Content Explorer")
    selected_item = st.selectbox(
        "Find content similar to:", recs["content_id"].tolist()
    )
    if selected_item:
        similar = recommender.get_similar_content(selected_item, n=6)
        st.dataframe(similar, use_container_width=True, hide_index=True)

# ── Catalog overview ──────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📚 Catalog Overview")

col_ov1, col_ov2 = st.columns(2)

with col_ov1:
    sport_dist = catalog_df["sport"].value_counts().reset_index()
    sport_dist.columns = ["Sport", "Items"]
    fig_sport = px.pie(
        sport_dist, names="Sport", values="Items",
        title="Catalog by Sport",
        color_discrete_map={"nba": "#3498db", "football": "#27ae60"},
        hole=0.4,
    )
    fig_sport.update_layout(
        paper_bgcolor="#0f0f1a", font_color="#f0f0f0", height=300
    )
    st.plotly_chart(fig_sport, use_container_width=True)

with col_ov2:
    type_dist = catalog_df["content_type"].value_counts().reset_index()
    type_dist.columns = ["Type", "Items"]
    fig_type_all = px.bar(
        type_dist, x="Type", y="Items",
        title="Catalog by Content Type",
        color="Items",
        color_continuous_scale="Blues",
    )
    fig_type_all.update_layout(
        plot_bgcolor="#0f0f1a", paper_bgcolor="#0f0f1a",
        font_color="#f0f0f0", coloraxis_showscale=False, height=300,
    )
    st.plotly_chart(fig_type_all, use_container_width=True)

st.caption(f"Total catalog items: {len(catalog_df):,}")
