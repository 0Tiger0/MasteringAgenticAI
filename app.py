"""
🚙 JeepTrail AI — Off-Road Trail Explorer Dashboard
A Streamlit app for browsing, filtering, and visualizing 200 US off-road trails.
Run with:  streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------------------------------- #
# Page configuration
# --------------------------------------------------------------------------- #
st.set_page_config(
    page_title="JeepTrail AI",
    page_icon="🚙",
    layout="wide",
    initial_sidebar_state="expanded",
)

DATA_PATH = Path(__file__).parent / "data" / "trails.csv"

# Consistent color sequence for a clean, modern look
PLOT_TEMPLATE = "plotly_white"
ACCENT = "#C75B12"  # trail-orange accent

# Logical ordering for difficulty
DIFFICULTY_ORDER = ["Easy", "Moderate", "Hard", "Extreme"]
DIFFICULTY_COLORS = {
    "Easy": "#2E933C",
    "Moderate": "#E8A33D",
    "Hard": "#D9622B",
    "Extreme": "#B3001B",
}


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
@st.cache_data
def load_data(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    # Enforce difficulty ordering for nicer charts/tables
    df["Difficulty"] = pd.Categorical(
        df["Difficulty"], categories=DIFFICULTY_ORDER, ordered=True
    )
    return df


if not DATA_PATH.exists():
    st.error(f"❌ Could not find data file at `{DATA_PATH}`. "
             "Run the dataset generator first.")
    st.stop()

df = load_data(DATA_PATH)


# --------------------------------------------------------------------------- #
# Header
# --------------------------------------------------------------------------- #
st.title("🚙 JeepTrail AI Dashboard")
st.markdown(
    "#### 🏔️ Explore **200 off-road trails** across the United States\n"
    "Filter by state, difficulty, vehicle, and trail type — then dive into "
    "the charts and trail table below. 🧭"
)
st.divider()


# --------------------------------------------------------------------------- #
# Sidebar filters
# --------------------------------------------------------------------------- #
st.sidebar.header("🔎 Filters")
st.sidebar.caption("Narrow down the trails to plan your next adventure.")

states = st.sidebar.multiselect(
    "📍 State",
    options=sorted(df["State"].unique()),
    default=[],
    placeholder="All states",
)

difficulties = st.sidebar.multiselect(
    "⛰️ Difficulty",
    options=DIFFICULTY_ORDER,
    default=[],
    placeholder="All difficulties",
)

vehicles = st.sidebar.multiselect(
    "🛻 Vehicle Requirement",
    options=sorted(df["Vehicle_Requirement"].unique()),
    default=[],
    placeholder="All vehicle types",
)

trail_types = st.sidebar.multiselect(
    "🌲 Trail Type",
    options=sorted(df["Trail_Type"].unique()),
    default=[],
    placeholder="All trail types",
)

# Apply filters (an empty selection means "no filter / show all")
filtered = df.copy()
if states:
    filtered = filtered[filtered["State"].isin(states)]
if difficulties:
    filtered = filtered[filtered["Difficulty"].isin(difficulties)]
if vehicles:
    filtered = filtered[filtered["Vehicle_Requirement"].isin(vehicles)]
if trail_types:
    filtered = filtered[filtered["Trail_Type"].isin(trail_types)]

st.sidebar.divider()
st.sidebar.metric("🚩 Trails matching filters", len(filtered))

if filtered.empty:
    st.warning("⚠️ No trails match the selected filters. Try widening your search.")
    st.stop()


# --------------------------------------------------------------------------- #
# Dashboard metrics
# --------------------------------------------------------------------------- #
st.subheader("📊 Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("🥾 Total Trails", f"{len(filtered):,}")
m2.metric("⭐ Average Rating", f"{filtered['Rating'].mean():.2f}")
m3.metric("🗺️ Number of States", filtered["State"].nunique())
m4.metric("🌄 Avg Scenic Score", f"{filtered['Scenic_Score'].mean():.1f}")

st.divider()


# --------------------------------------------------------------------------- #
# Charts
# --------------------------------------------------------------------------- #
st.subheader("📈 Visual Insights")

row1_left, row1_right = st.columns(2)

# --- Trails by State (bar) ---
with row1_left:
    st.markdown("##### 📍 Trails by State")
    by_state = (
        filtered["State"].value_counts().sort_values(ascending=True).reset_index()
    )
    by_state.columns = ["State", "Trails"]
    fig_state = px.bar(
        by_state,
        x="Trails",
        y="State",
        orientation="h",
        text="Trails",
        color="Trails",
        color_continuous_scale="Oranges",
        template=PLOT_TEMPLATE,
    )
    fig_state.update_layout(
        showlegend=False, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10), height=420,
    )
    fig_state.update_traces(textposition="outside")
    st.plotly_chart(fig_state, width="stretch")

# --- Difficulty Distribution (pie) ---
with row1_right:
    st.markdown("##### ⛰️ Difficulty Distribution")
    by_diff = filtered["Difficulty"].value_counts().reindex(DIFFICULTY_ORDER).dropna()
    fig_diff = px.pie(
        names=by_diff.index,
        values=by_diff.values,
        color=by_diff.index,
        color_discrete_map=DIFFICULTY_COLORS,
        hole=0.45,
        template=PLOT_TEMPLATE,
    )
    fig_diff.update_traces(textinfo="percent+label")
    fig_diff.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=420,
        legend_title_text="Difficulty",
    )
    st.plotly_chart(fig_diff, width="stretch")

row2_left, row2_right = st.columns(2)

# --- Top 10 Rated Trails (bar) ---
with row2_left:
    st.markdown("##### 🏆 Top 10 Rated Trails")
    top10 = filtered.sort_values(
        ["Rating", "Scenic_Score"], ascending=False
    ).head(10).sort_values("Rating", ascending=True)
    fig_top = px.bar(
        top10,
        x="Rating",
        y="Trail_Name",
        orientation="h",
        text="Rating",
        color="Rating",
        color_continuous_scale="YlOrRd",
        hover_data=["State", "Difficulty", "Trail_Type"],
        template=PLOT_TEMPLATE,
    )
    fig_top.update_layout(
        showlegend=False, coloraxis_showscale=False,
        margin=dict(l=10, r=10, t=10, b=10), height=420,
        yaxis_title=None,
    )
    fig_top.update_traces(textposition="outside")
    st.plotly_chart(fig_top, width="stretch")

# --- Scenic Score Distribution (histogram) ---
with row2_right:
    st.markdown("##### 🌄 Scenic Score Distribution")
    fig_scenic = px.histogram(
        filtered,
        x="Scenic_Score",
        nbins=20,
        color_discrete_sequence=[ACCENT],
        template=PLOT_TEMPLATE,
    )
    fig_scenic.update_layout(
        margin=dict(l=10, r=10, t=10, b=10), height=420,
        bargap=0.05, xaxis_title="Scenic Score", yaxis_title="Number of Trails",
    )
    st.plotly_chart(fig_scenic, width="stretch")

st.divider()


# --------------------------------------------------------------------------- #
# Searchable trail table
# --------------------------------------------------------------------------- #
st.subheader("🔍 Trail Explorer")

search = st.text_input(
    "Search trails",
    placeholder="🔎 Type a trail name, state, or trail type…",
    label_visibility="collapsed",
)

table = filtered
if search:
    mask = (
        table["Trail_Name"].str.contains(search, case=False, na=False)
        | table["State"].str.contains(search, case=False, na=False)
        | table["Trail_Type"].str.contains(search, case=False, na=False)
        | table["Vehicle_Requirement"].str.contains(search, case=False, na=False)
    )
    table = table[mask]

st.caption(f"Showing **{len(table)}** of **{len(df)}** trails. 🚙")

st.dataframe(
    table.sort_values("Rating", ascending=False),
    width="stretch",
    hide_index=True,
    column_config={
        "Trail_Name": "🥾 Trail Name",
        "State": "📍 State",
        "Difficulty": "⛰️ Difficulty",
        "Length_Miles": st.column_config.NumberColumn("📏 Length (mi)", format="%.1f"),
        "Elevation_Gain": st.column_config.NumberColumn("📈 Elevation (ft)", format="%d"),
        "Vehicle_Requirement": "🛻 Vehicle",
        "Rating": st.column_config.NumberColumn("⭐ Rating", format="%.1f"),
        "Trail_Type": "🌲 Type",
        "Estimated_Duration_Hours": st.column_config.NumberColumn("⏱️ Duration (hr)", format="%.1f"),
        "Scenic_Score": st.column_config.ProgressColumn(
            "🌄 Scenic", min_value=0, max_value=100, format="%d"
        ),
    },
)

# Download filtered results
st.download_button(
    "⬇️ Download filtered trails (CSV)",
    data=table.to_csv(index=False).encode("utf-8"),
    file_name="filtered_trails.csv",
    mime="text/csv",
)

st.divider()
st.caption("🚙 **JeepTrail AI** · Built with Streamlit & Plotly · Data: synthetic US off-road trails 🏔️")
