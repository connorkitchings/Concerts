# Data Directory

This directory contains all canonical output data for JamBandNerd. Subfolders are organized by band and data type.

## Structure

- `collected/` — Raw and processed outputs from each band pipeline (CSV, JSON)
- `processed/` — Cleaned or feature-engineered data for analytics/ML
- `predictions/` — Model outputs (CK+, Notebook, etc.)

Each band (Phish, Goose, UM, WSP) has its own subdirectory under `data/` for modularity and reproducibility.

Example:
```
data/
├── phish/
│   └── collected/
├── goose/
│   └── collected/
├── um/
│   └── collected/
├── wsp/
│   └── collected/
```

See each band pipeline README for details on output files and formats.