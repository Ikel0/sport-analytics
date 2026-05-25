"""Sport Analytics Dashboard — Main Entry Point"""
import streamlit as st
st.set_page_config(page_title="Sport Analytics", page_icon="🏆", layout="wide",
                   initial_sidebar_state="expanded")
st.markdown("""<style>
[data-testid="stSidebar"] { background: linear-gradient(180deg,#0f0f1a,#1a1a2e); }
[data-testid="stSidebar"] * { color: #f0f0f0 !important; }
[data-testid="metric-container"] { background:#1e1e2e; border:1px solid #333355;
    border-radius:10px; padding:12px; }
</style>""", unsafe_allow_html=True)

st.sidebar.title("🏆 Sport Analytics")
st.sidebar.markdown("---")
st.sidebar.markdown("**Navigate:**\n- 🏀 NBA Analytics\n- ⚽ Football Analytics\n- 🤖 Recommendations")
st.sidebar.markdown("---")
st.sidebar.caption("Python · Snowflake · AWS · Airflow")
st.sidebar.caption("© 2026 Ikel Ouedraogo")

st.title("🏆 Sport Analytics Platform")
st.markdown("**End-to-end data pipeline** for basketball & football — from API ingestion to AI-powered recommendations.")

c1,c2,c3,c4 = st.columns(4)
c1.metric("🏀 NBA Games Tracked","2,847","+12 today")
c2.metric("⚽ Football Fixtures","4,120","+8 today")
c3.metric("👤 Players Profiled","1,340","+3 today")
c4.metric("🤖 Recommendations","98K","+1.2K today")
st.markdown("---")

col_l, col_r = st.columns(2)
with col_l:
    st.subheader("🏀 NBA — Top 5")
    st.markdown("""| Team | W | L | Win% |
|---|---|---|---|
| Boston Celtics | 58 | 14 | .806 |
| Oklahoma City Thunder | 55 | 17 | .764 |
| Denver Nuggets | 52 | 20 | .722 |
| Minnesota Timberwolves | 49 | 23 | .681 |
| Cleveland Cavaliers | 48 | 24 | .667 |""")
with col_r:
    st.subheader("⚽ Football — Premier League Top 5")
    st.markdown("""| Team | Pts | GF | GA |
|---|---|---|---|
| Manchester City | 91 | 96 | 33 |
| Arsenal | 89 | 91 | 29 |
| Liverpool | 82 | 86 | 41 |
| Aston Villa | 68 | 76 | 61 |
| Tottenham | 60 | 74 | 62 |""")
st.markdown("---")
st.info("👈 Use the sidebar to explore NBA, Football analytics, and personalized recommendations.")
