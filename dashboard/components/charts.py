"""Reusable Plotly chart components for the Sport Analytics dashboard."""
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd

DARK_BG    = "#0f0f1a"
CARD_BG    = "#1e1e2e"
FONT_COLOR = "#f0f0f0"
GRID_COLOR = "#2a2a3e"

BASE_LAYOUT = dict(
    plot_bgcolor=DARK_BG,
    paper_bgcolor=DARK_BG,
    font_color=FONT_COLOR,
    xaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
)


def win_pct_bar(df: pd.DataFrame, team_col="Team", win_col="Win%",
                title="Win Percentage", height=480) -> go.Figure:
    fig = px.bar(df.sort_values(win_col, ascending=True),
                 x=win_col, y=team_col, orientation="h",
                 color=win_col, color_continuous_scale=["#c0392b","#f39c12","#27ae60"],
                 title=title, height=height)
    fig.update_layout(**BASE_LAYOUT, coloraxis_showscale=False)
    return fig


def efficiency_scatter(df, x_col, y_col, size_col, color_col, text_col,
                       x_label, y_label, title, height=480) -> go.Figure:
    fig = px.scatter(df, x=x_col, y=y_col, size=size_col, color=color_col,
                     text=text_col, color_continuous_scale="RdYlGn",
                     title=title, labels={x_col: x_label, y_col: y_label}, height=height)
    fig.update_traces(textposition="top center", textfont_size=8)
    fig.add_vline(x=df[x_col].mean(), line_dash="dash", line_color="#888")
    fig.add_hline(y=df[y_col].mean(), line_dash="dash", line_color="#888")
    fig.update_layout(**BASE_LAYOUT)
    return fig


def score_trend_line(df, date_col, score_col, opp_col, result_col,
                     team_name, height=420) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df[date_col], y=df[score_col], name=team_name,
        line=dict(color="#3498db", width=2.5), mode="lines+markers",
        marker=dict(color=["#27ae60" if r=="W" else "#c0392b" for r in df[result_col]], size=10),
    ))
    fig.add_trace(go.Scatter(
        x=df[date_col], y=df[opp_col], name="Opponent",
        line=dict(color="#e74c3c", width=2, dash="dot"),
        mode="lines+markers", marker=dict(size=7, color="#e74c3c"),
    ))
    fig.update_layout(**BASE_LAYOUT, title=f"{team_name} — Score Trend",
                      legend=dict(orientation="h", y=1.1), height=height)
    return fig


def wl_donut(wins, losses, draws=0, height=300) -> go.Figure:
    labels = ["Wins","Draws","Losses"] if draws else ["Wins","Losses"]
    values = [wins, draws, losses] if draws else [wins, losses]
    colors = ["#27ae60","#f39c12","#c0392b"] if draws else ["#27ae60","#c0392b"]
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.55,
                           marker=dict(colors=colors)))
    fig.update_layout(paper_bgcolor=DARK_BG, font_color=FONT_COLOR,
                      title="Result Distribution", height=height)
    return fig


def player_radar(player_name, values, categories, height=420) -> go.Figure:
    vals = values + [values[0]]
    cats = categories + [categories[0]]
    fig  = go.Figure(go.Scatterpolar(
        r=vals, theta=cats, fill="toself",
        fillcolor="rgba(52,152,219,0.3)",
        line=dict(color="#3498db", width=2), name=player_name,
    ))
    fig.update_layout(
        polar=dict(bgcolor=CARD_BG,
                   radialaxis=dict(visible=True, range=[0,1], color="#888"),
                   angularaxis=dict(color=FONT_COLOR)),
        paper_bgcolor=DARK_BG, font_color=FONT_COLOR,
        title=f"Performance Radar — {player_name}", height=height,
    )
    return fig
