import streamlit as st
import pandas as pd
import pyarrow.parquet as pq
import plotly.graph_objects as go
import os
import base64
from pathlib import Path

# ── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LILA BLACK - Player Journey Visualizer",
    page_icon="🎮",
    layout="wide"
)

st.title("🎮 LILA BLACK — Player Journey Visualizer")
st.caption("Level Design Tool | 5 days of production gameplay data")

# ── MAP CONFIGURATION ─────────────────────────────────────────────────────────
# These values come directly from the README
# They tell us how to convert world coordinates to minimap pixel positions
MAP_CONFIG = {
    "AmbroseValley": {"scale": 900,  "origin_x": -370, "origin_z": -473},
    "GrandRift":     {"scale": 581,  "origin_x": -290, "origin_z": -290},
    "Lockdown":      {"scale": 1000, "origin_x": -500, "origin_z": -500},
}

MINIMAP_FILES = {
    "AmbroseValley": "player_data/minimaps/AmbroseValley_Minimap.png",
    "GrandRift":     "player_data/minimaps/GrandRift_Minimap.png",
    "Lockdown":      "player_data/minimaps/Lockdown_Minimap.jpg",
}

# ── COORDINATE CONVERSION ────────────────────────────────────────────────────
# Converts a world (x, z) coordinate to a pixel position on the 1024x1024 minimap
def world_to_pixel(x, z, map_name):
    cfg = MAP_CONFIG[map_name]
    u = (x - cfg["origin_x"]) / cfg["scale"]
    v = (z - cfg["origin_z"]) / cfg["scale"]
    pixel_x = u * 1024
    pixel_y = (1 - v) * 1024   # Y is flipped because image origin is top-left
    return pixel_x, pixel_y

# ── DATA LOADING ─────────────────────────────────────────────────────────────
# Load all parquet files from all days into one big DataFrame
# We cache this so it only runs once -- not every time you click something
@st.cache_data
def load_all_data():
    days = ["February_10", "February_11", "February_12", "February_13", "February_14"]
    frames = []
    for day in days:
        folder = f"player_data/{day}"
        if not os.path.exists(folder):
            continue
        for fname in os.listdir(folder):
            fpath = os.path.join(folder, fname)
            try:
                df = pq.read_table(fpath).to_pandas()
                # Decode event from bytes to string
                df['event'] = df['event'].apply(
                    lambda x: x.decode('utf-8') if isinstance(x, bytes) else x
                )
                # Add the day as a column so we can filter by it later
                df['day'] = day
                # Detect human vs bot from user_id
                # Bots have short numeric IDs, humans have UUIDs (longer, with dashes)
                df['is_bot'] = df['user_id'].apply(
                    lambda uid: not (len(str(uid)) > 10 and '-' in str(uid))
                )
                frames.append(df)
            except Exception:
                continue
    if not frames:
        return pd.DataFrame()
    all_data = pd.concat(frames, ignore_index=True)
    return all_data

# Show a loading spinner while data loads
with st.spinner("Loading 5 days of match data... (this takes ~15 seconds the first time)"):
    df_all = load_all_data()

st.success(f"Loaded {len(df_all):,} events across {df_all['match_id'].nunique()} matches")

# ── SIDEBAR FILTERS ───────────────────────────────────────────────────────────
st.sidebar.header("Filters")

# Map selector
map_choice = st.sidebar.selectbox(
    "Select Map",
    options=["AmbroseValley", "GrandRift", "Lockdown"]
)

# Day selector
day_choice = st.sidebar.selectbox(
    "Select Day",
    options=["All Days", "February_10", "February_11", "February_12", "February_13", "February_14"]
)

# Filter data by map and day
df_filtered = df_all[df_all['map_id'] == map_choice].copy()
if day_choice != "All Days":
    df_filtered = df_filtered[df_filtered['day'] == day_choice]

# Match selector -- only shows matches from the filtered data
match_ids = sorted(df_filtered['match_id'].unique())
match_choice = st.sidebar.selectbox(
    "Select Match",
    options=match_ids,
    format_func=lambda x: x[:18] + "..."   # Shorten the long UUID for display
)

# Filter down to just the selected match
df_match = df_filtered[df_filtered['match_id'] == match_choice].copy()

# Show/hide options
st.sidebar.subheader("Display Options")
show_humans  = st.sidebar.checkbox("Show Human Players", value=True)
show_bots    = st.sidebar.checkbox("Show Bots", value=True)
show_kills   = st.sidebar.checkbox("Show Kills", value=True)
show_deaths  = st.sidebar.checkbox("Show Deaths", value=True)
show_loot    = st.sidebar.checkbox("Show Loot", value=True)
show_storm   = st.sidebar.checkbox("Show Storm Deaths", value=True)

# ── VIEW TABS ─────────────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["🗺️ Player Paths", "🔥 Heatmaps", "⏱️ Timeline"])

# ── HELPER: Load minimap image as base64 for Plotly background ────────────────
def get_image_base64(path):
    with open(path, "rb") as f:
        data = f.read()
    ext = Path(path).suffix.lstrip('.')
    if ext == 'jpg':
        ext = 'jpeg'
    return f"data:image/{ext};base64,{base64.b64encode(data).decode()}"

# ── EVENT COLORS AND SYMBOLS ──────────────────────────────────────────────────
EVENT_STYLE = {
    "Kill":          {"color": "red",        "symbol": "x",              "size": 12},
    "Killed":        {"color": "gray",       "symbol": "x",              "size": 12},
    "BotKill":       {"color": "orange",     "symbol": "x",              "size": 10},
    "BotKilled":     {"color": "lightgray",  "symbol": "x",              "size": 10},
    "KilledByStorm": {"color": "purple",     "symbol": "diamond",        "size": 12},
    "Loot":          {"color": "lime",       "symbol": "triangle-up",    "size": 10},
}

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 1: PLAYER PATHS
# ═══════════════════════════════════════════════════════════════════════════════
with tab1:
    st.subheader(f"Player Paths — {map_choice} — Match {match_choice[:18]}...")

    # Match stats summary
    n_humans = df_match[~df_match['is_bot']]['user_id'].nunique()
    n_bots   = df_match[df_match['is_bot']]['user_id'].nunique()
    n_kills  = len(df_match[df_match['event'] == 'Kill'])
    n_loot   = len(df_match[df_match['event'] == 'Loot'])
    n_storm  = len(df_match[df_match['event'] == 'KilledByStorm'])

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Human Players", n_humans)
    col2.metric("Bots", n_bots)
    col3.metric("PvP Kills", n_kills)
    col4.metric("Loot Events", n_loot)
    col5.metric("Storm Deaths", n_storm)

    # Build Plotly figure with minimap as background
    fig = go.Figure()

    # Add minimap image as background
    img_b64 = get_image_base64(MINIMAP_FILES[map_choice])
    fig.add_layout_image(
        source=img_b64,
        x=0, y=1024,
        xref="x", yref="y",
        sizex=1024, sizey=1024,
        sizing="stretch",
        layer="below"
    )

    # Plot movement paths for each player
    position_events = {"Position", "BotPosition"}
    df_pos = df_match[df_match['event'].isin(position_events)].copy()

    for uid, group in df_pos.groupby('user_id'):
        is_bot = group['is_bot'].iloc[0]

        if is_bot and not show_bots:
            continue
        if not is_bot and not show_humans:
            continue

        # Sort by timestamp to get the path in order
        group = group.sort_values('ts')

        # Convert world coordinates to pixel coordinates
        px, py = zip(*[world_to_pixel(row.x, row.z, map_choice)
                       for row in group.itertuples()])

        color = "rgba(100,149,237,0.5)" if not is_bot else "rgba(255,165,0,0.3)"
        label = f"Human: {str(uid)[:8]}" if not is_bot else f"Bot: {uid}"

        fig.add_trace(go.Scatter(
            x=list(px), y=list(py),
            mode='lines',
            line=dict(color=color, width=1.5),
            name=label,
            hoverinfo='name'
        ))

    # Plot discrete events (kills, deaths, loot, storm)
    event_filters = []
    if show_kills:   event_filters += ["Kill", "BotKill"]
    if show_deaths:  event_filters += ["Killed", "BotKilled"]
    if show_loot:    event_filters += ["Loot"]
    if show_storm:   event_filters += ["KilledByStorm"]

    for evt in event_filters:
        df_evt = df_match[df_match['event'] == evt]
        if df_evt.empty:
            continue
        style = EVENT_STYLE.get(evt, {"color": "white", "symbol": "circle", "size": 8})
        px_list, py_list = zip(*[world_to_pixel(row.x, row.z, map_choice)
                                  for row in df_evt.itertuples()])
        fig.add_trace(go.Scatter(
            x=list(px_list), y=list(py_list),
            mode='markers',
            marker=dict(color=style["color"], symbol=style["symbol"],
                        size=style["size"], line=dict(width=1, color='black')),
            name=evt
        ))

    fig.update_layout(
        xaxis=dict(range=[0, 1024], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 1024], showgrid=False, zeroline=False, showticklabels=False,
                   scaleanchor='x'),
        height=700,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='#1a1a2e',
        plot_bgcolor='#1a1a2e',
        legend=dict(bgcolor='rgba(0,0,0,0.5)', font=dict(color='white'))
    )

    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 2: HEATMAPS
# ═══════════════════════════════════════════════════════════════════════════════
with tab2:
    st.subheader(f"Heatmaps — {map_choice}")

    heatmap_type = st.radio(
        "Heatmap Type",
        ["Kill Zones", "Death Zones", "High Traffic Areas", "Storm Death Zones"],
        horizontal=True
    )

    type_map = {
        "Kill Zones":          ["Kill", "BotKill"],
        "Death Zones":         ["Killed", "BotKilled"],
        "High Traffic Areas":  ["Position", "BotPosition"],
        "Storm Death Zones":   ["KilledByStorm"],
    }

    selected_events = type_map[heatmap_type]

    # Use ALL matches for the selected map/day -- more data = better heatmap
    df_heat = df_filtered[df_filtered['event'].isin(selected_events)].copy()

    if df_heat.empty:
        st.warning("No events of this type found for the current filters.")
    else:
        px_list, py_list = zip(*[world_to_pixel(row.x, row.z, map_choice)
                                  for row in df_heat.itertuples()])

        fig2 = go.Figure()

        img_b64 = get_image_base64(MINIMAP_FILES[map_choice])
        fig2.add_layout_image(
            source=img_b64,
            x=0, y=1024,
            xref="x", yref="y",
            sizex=1024, sizey=1024,
            sizing="stretch",
            layer="below"
        )

        fig2.add_trace(go.Histogram2dContour(
            x=list(px_list),
            y=list(py_list),
            colorscale="Hot",
            reversescale=False,
            showscale=True,
            opacity=0.6,
            contours=dict(showlines=False),
            ncontours=20,
        ))

        fig2.update_layout(
            xaxis=dict(range=[0, 1024], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 1024], showgrid=False, zeroline=False, showticklabels=False,
                       scaleanchor='x'),
            height=700,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#1a1a2e',
        )

        st.plotly_chart(fig2, use_container_width=True)
        st.caption(f"Based on {len(df_heat):,} events across {df_filtered['match_id'].nunique()} matches")

# ═══════════════════════════════════════════════════════════════════════════════
# TAB 3: TIMELINE
# ═══════════════════════════════════════════════════════════════════════════════
with tab3:
    st.subheader(f"Match Timeline — {match_choice[:18]}...")

    # Sort match data by timestamp
    df_timeline = df_match.sort_values('ts').copy()

    if df_timeline.empty:
        st.warning("No data for this match.")
    else:
        # Convert timestamp to seconds elapsed
        ts_min = df_timeline['ts'].min()
        df_timeline['elapsed_ms'] = (df_timeline['ts'] - ts_min).dt.total_seconds() * 1000
        max_ms = int(df_timeline['elapsed_ms'].max())

        st.write("**Use the slider to scrub through the match timeline:**")
        time_pct = st.slider("Match Progress", 0, 100, 50, step=1, format="%d%%")

        # Show events up to the selected time point
        cutoff_ms = (time_pct / 100) * max_ms
        df_snap = df_timeline[df_timeline['elapsed_ms'] <= cutoff_ms]

        elapsed_sec = cutoff_ms / 1000
        st.caption(f"Showing first {elapsed_sec:.0f} seconds of match ({len(df_snap):,} events)")

        # Rebuild the path figure up to this time point
        fig3 = go.Figure()

        img_b64 = get_image_base64(MINIMAP_FILES[map_choice])
        fig3.add_layout_image(
            source=img_b64,
            x=0, y=1024,
            xref="x", yref="y",
            sizex=1024, sizey=1024,
            sizing="stretch",
            layer="below"
        )

        df_pos_snap = df_snap[df_snap['event'].isin({"Position", "BotPosition"})]
        for uid, group in df_pos_snap.groupby('user_id'):
            is_bot = group['is_bot'].iloc[0]
            group = group.sort_values('ts')
            px, py = zip(*[world_to_pixel(row.x, row.z, map_choice)
                            for row in group.itertuples()])
            color = "rgba(100,149,237,0.7)" if not is_bot else "rgba(255,165,0,0.4)"
            fig3.add_trace(go.Scatter(
                x=list(px), y=list(py),
                mode='lines+markers',
                line=dict(color=color, width=1.5),
                marker=dict(size=3),
                name=f"{'Human' if not is_bot else 'Bot'}: {str(uid)[:8]}",
                hoverinfo='name'
            ))

        # Show events up to this point
        for evt in ["Kill", "Killed", "Loot", "KilledByStorm", "BotKill", "BotKilled"]:
            df_e = df_snap[df_snap['event'] == evt]
            if df_e.empty:
                continue
            style = EVENT_STYLE.get(evt, {"color": "white", "symbol": "circle", "size": 8})
            px_e, py_e = zip(*[world_to_pixel(row.x, row.z, map_choice)
                                for row in df_e.itertuples()])
            fig3.add_trace(go.Scatter(
                x=list(px_e), y=list(py_e),
                mode='markers',
                marker=dict(color=style["color"], symbol=style["symbol"],
                            size=style["size"], line=dict(width=1, color='black')),
                name=evt
            ))

        fig3.update_layout(
            xaxis=dict(range=[0, 1024], showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(range=[0, 1024], showgrid=False, zeroline=False, showticklabels=False,
                       scaleanchor='x'),
            height=700,
            margin=dict(l=0, r=0, t=0, b=0),
            paper_bgcolor='#1a1a2e',
            plot_bgcolor='#1a1a2e',
            legend=dict(bgcolor='rgba(0,0,0,0.5)', font=dict(color='white'))
        )

        st.plotly_chart(fig3, use_container_width=True)

        # Event log below the map
        st.subheader("Event Log")
        df_events_only = df_snap[~df_snap['event'].isin({'Position', 'BotPosition'})].copy()
        df_events_only['elapsed_sec'] = df_events_only['elapsed_ms'] / 1000
        st.dataframe(
            df_events_only[['elapsed_sec', 'user_id', 'event', 'x', 'z', 'is_bot']]
            .sort_values('elapsed_sec')
            .reset_index(drop=True),
            use_container_width=True,
            height=200
        )