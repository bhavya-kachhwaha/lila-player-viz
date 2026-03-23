# Architecture Document — LILA BLACK Player Journey Visualizer

## Tech Stack

| Component | Choice | Reason |
|-----------|--------|--------|
| Frontend + Backend | Streamlit | Single Python file, no frontend code needed, deploys in minutes |
| Data reading | PyArrow + Pandas | PyArrow reads Parquet natively and fast; Pandas for filtering |
| Visualization | Plotly | Interactive charts, supports image backgrounds, runs in browser |
| Hosting | Streamlit Cloud | Free, deploys directly from GitHub, shareable URL |

## Data Flow

1. On startup, all .nakama-0 files across 5 folders are read as Parquet
2. Event column decoded from bytes to UTF-8 string
3. Bot vs human detected from user_id (UUID = human, numeric = bot)
4. All data cached in memory via @st.cache_data
5. User filters (map, day, match) applied on the cached DataFrame
6. Filtered data passed to Plotly figures with minimap as background image

## Coordinate Mapping

World coordinates (x, z) converted to 1024x1024 pixel space:
```
u = (x - origin_x) / scale
v = (z - origin_z) / scale
pixel_x = u * 1024
pixel_y = (1 - v) * 1024  ← Y flipped because image origin is top-left
```

Each map has different scale and origin values per the README spec.
The y column (elevation) is ignored for 2D minimap plotting.

## Assumptions

- Timestamp (ts) represents elapsed match time, not wall-clock time
- Files with no valid Parquet structure are silently skipped
- February 14 treated as partial day as noted in README

## Trade-offs

| Decision | Trade-off |
|----------|-----------|
| Load all data at startup | Slow first load (~15s) but instant filtering after |
| Streamlit over React | Faster to build, less customisable UI |
| Plotly contour heatmap | Smooth visuals but slower than raw pixel binning |

## What I'd Do With More Time

- Add animation frame-by-frame playback instead of a slider
- Pre-aggregate heatmap data into a grid for faster rendering
- Add player comparison view (two players side by side)
- Extract storm path direction from KilledByStorm event clusters