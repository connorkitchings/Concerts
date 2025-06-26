# JamBandNerd

## Project Overview (updated 06/25/2025)
JamBandNerd is a modular data science platform for collecting, processing, and predicting jam band setlists. It supports robust, parallelized data pipelines and predictive analytics for:
- **Widespread Panic (WSP)**
- **Phish**
- **Umphrey's McGee (UM)**
- **Goose**

### Key Features
- **Automated data collection** from APIs and web scraping
- **Parallel pipeline orchestration** with unified, timestamped logging
- **Standardized data outputs** for analytics and ML
- **Multiple prediction models** (CK+, Notebook)
- **Modern, reproducible project structure**

---

## Directory Structure
```text
JamBandNerd/
├── data/                  # Canonical output data (collected, processed, predictions)
├── logs/                  # All band and pipeline logs
├── scripts/               # Orchestration and runner scripts
├── src/
│   └── jambandnerd/
│       ├── data_collection/
│       │   ├── phish/
│       │   ├── goose/
│       │   ├── um/
│       │   └── wsp/
│       └── predictions/
│           ├── ckplus_model/
│           └── notebook_model/
├── requirements.txt
├── README.md              # This file
└── ...
```

---

## Data Collection Pipelines
Each band has a dedicated, fully documented pipeline:
- **Phish**: Uses phish.net API (API key required in `.env`).
- **Goose**: Uses elgoose.net API (no key required).
- **UM**: Scrapes allthings.umphreys.com.
- **WSP**: Scrapes everydaycompanion.com.

See each band’s README for details and usage. Outputs are saved to `data/<band>/collected/`.

### Orchestration
- Run all pipelines in parallel:
  ```bash
  python3 scripts/run_all_pipelines.py
  ```
- Logs are unified under `logs/` with `[MM-DD-YYYY HH:MM:SS] LEVEL: message` format.

---

## Prediction Models
- **CK+ (gap-based statistical)**: `src/jambandnerd/predictions/ckplus_model/`
- **Notebook (rotation-based)**: `src/jambandnerd/predictions/notebook_model/`

Each model has its own README and can be run for all bands or individually.

---

## Development & Contribution
- Python 3.9+
- Install dependencies:
  ```bash
  pip install -r requirements.txt
  ```
- See [CONTRIBUTING.md] (if available) for guidelines.

---

## License
MIT

---

## References
- [phish.net](https://phish.net/)
- [elgoose.net](https://elgoose.net/)
- [allthings.umphreys.com](https://allthings.umphreys.com/)
- [everydaycompanion.com](http://www.everydaycompanion.com/)
