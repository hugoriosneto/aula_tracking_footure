# Football Tracking Data Visualization

This repository contains utilities and examples for visualizing football (soccer) tracking data using the kloppy and mplsoccer packages. The focus is on PFF FC tracking data from the FIFA Men's World Cup 2022.

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/football-tracking-viz.git
cd football-tracking-viz
```

### 2. Create a Virtual Environment

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# For Windows:
venv\Scripts\activate
# For macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Automated Setup

For convenience, we've included automated setup scripts:

- **Linux/macOS**: Run `./setup_venv.sh`
- **Windows**: Run `setup_venv.bat`

These scripts will create a virtual environment, install dependencies, and download sample data.

## Data

This project uses PFF FC tracking data from the FIFA Men's World Cup 2022. The datasets can be requested via [this link](https://www.blog.fc.pff.com/blog/pff-fc-release-2022-world-cup-data).

The main data components include:
- **Tracking Data**: Contains player and ball positions, stored separately per game as `{game_id}.jsonl.bz2`
- **Event Data**: Contains match events for all games stored in a single file: `events.json`
- **Metadata**: Contains game information (teams, date, etc.) stored as `{game_id}.json`
- **Rosters**: Contains team sheets information stored as `{game_id}.json`

You can download sample data for testing by running:

```bash
python download_sample_data.py
```

## Notebooks and Scripts

This repository contains both Jupyter notebooks and Python scripts for visualization:

### Python Scripts (with jupytext)

We use [jupytext](https://jupytext.readthedocs.io/) to store notebooks as version-control-friendly Python scripts:

- `pff.py`: Basic loading of PFF tracking data
- `tracking_visualization.py`: Comprehensive visualization examples including frames and animations

These `.py` files can be used in two ways:

1. **Open directly as notebooks in JupyterLab/Jupyter Notebook**:  
   If you have jupytext installed, these Python scripts will automatically open as notebooks.

2. **Convert to .ipynb format**:  
   ```bash
   jupytext --to notebook pff.py
   jupytext --to notebook tracking_visualization.py
   ```

3. **Sync changes between .py and .ipynb**:  
   ```bash
   jupytext --sync tracking_visualization.ipynb  # Syncs with tracking_visualization.py
   ```

### Examples

The scripts/notebooks include examples of:
- Loading and processing tracking data using kloppy
- Visualizing single frames of match situations
- Creating animations of player movements
- Exporting visualizations as GIFs, MP4 videos, or interactive HTML

## License

This repository is licensed under the MIT License - see the LICENSE file for details. 