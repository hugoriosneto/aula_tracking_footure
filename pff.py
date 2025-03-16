# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.4
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %% [markdown]
# # PFF FC Tracking Data
# PFF FC released their broadcast tracking data from the FIFA Men's World Cup 2022. The datasets can be requested via [this link](https://www.blog.fc.pff.com/blog/pff-fc-release-2022-world-cup-data).
# ##### Key Data Points:
# - Tracking Data: The tracking data is stored separately per game: `{game_id}.jsonl.bz2`
# - Event Data: The event data for all games is stored in a single file: `events.json`
# - Metadata: The metadata (home team, away team, date of the game, etc.) information. Each game's metadata is stored seperately as `{game_id}.json`.
# - Rosters:  The rosters contain information on the team sheets. Each game's roster is stored seperately as `{game_id}.json`.
#
# ## Load local files
# To load the tracking data as a TrackingDataset use the `load_tracking()` function from the `pff` module.
#
# Required parameters are:
# - `meta_data`: Path containing metadata about the tracking data.
# - `players_meta_data`: Path containing roster metadata, such as player details.
# - `raw_data`: Path containing the raw tracking data.
#
# Optional parameters are:
# - `coordinates`: The coordinate system to use for the tracking data (e.g., "pff").
# - `sample_rate`: The sampling rate to downsample the data. If None, no downsampling is applied.
# - `limit`: The maximum number of records to process. If None, all records are processed.
# - `only_alive`: Whether to include only sequences when the ball is in play.

# %%
from kloppy import pff

dataset = pff.load_tracking(meta_data="data/pff_metadata_10517.json",
                     roster_meta_data="data/pff_rosters_10517.json",
                     raw_data="data/pff_10517.jsonl.bz2",
                     # Optional Parameters
                     coordinates="pff",
                     sample_rate=None,
                     limit=None)

dataset.to_df().head() 