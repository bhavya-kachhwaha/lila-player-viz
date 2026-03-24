# LILA BLACK — Player Journey Visualizer

A browser-based tool for Level Designers to explore player behavior 
across LILA BLACK's three maps using 5 days of production gameplay data.

## Live Demo
https://lila-player-viz-8zxz8y4jxrt99gq7xbvv4v.streamlit.app

## Features
- Player movement paths on minimap (humans vs bots visually distinct)
- Kill, death, loot, and storm death event markers
- Filter by map, day, and match
- Heatmaps for kill zones, death zones, traffic, and storm deaths
- Timeline scrubber to replay a match from start to finish

## Tech Stack
- Python 3.13
- Streamlit
- Pandas + PyArrow (Parquet reading)
- Plotly (interactive charts)

## Run Locally

**1. Clone the repo**
```bash
git clone https://github.com/bhavya-kachhwaha/lila-player-viz.git
cd lila-player-viz
```

**2. Create virtual environment**
```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Run the app**
```bash
streamlit run app.py
```

App opens at http://localhost:8501

## Project Structure
```
lila-player-viz/
├── app.py              # Main application
├── requirements.txt    # Dependencies
├── ARCHITECTURE.md     # Tech decisions and data flow
├── INSIGHTS.md         # Three game insights from the data
├── player_data/        # Raw gameplay data (Parquet files)
│   ├── February_10/
│   ├── February_11/
│   ├── February_12/
│   ├── February_13/
│   ├── February_14/
│   └── minimaps/
```

## No Environment Variables Required
The app reads data directly from the local player_data folder.
No API keys or external services needed.
