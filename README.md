# Implied Volatility Smile Spillovers
### Preliminary Research for Bachelor Thesis — University of Amsterdam
**Author:** Başar Hacımustafaoğlu  
**Student Number:** 1******6  
**Program:** BSc Economics and Business Economics (Finance)  
**Course:** 6013B0520Y — Bachelor Thesis Finance  
**Academic Year:** 2025/26, Semester 2  
**Topic:** AP-33 — Implied Volatility Smile Spillovers  

---

## Research Question

Does a change in the implied volatility smile of the US equity options market have predictive power for the implied volatility smile of the European equity options market?

The empirical strategy exploits the institutional time-zone lead–lag between the US (S&P 500 / SPX options) and European (Euro Stoxx 50 / OESX options) markets. US markets close approximately 4.5 hours after European markets on the same calendar day, providing a natural one-day lag structure for a spillover regression.

---

## Repository Structure

```
.
├── data/
│   ├── raw/                  # Immutable. Never modified after download.
│   ├── intermediate/         # Cleaned, standardized, not yet merged.
│   ├── analysis_ready/       # Final merged dataset ready for regression.
│   └── outputs/              # Tables, figures, regression results.
│
├── notebooks/                # Jupyter notebooks (numbered, ordered)
│   ├── 00_wrds_setup_test.ipynb
│   └── 01_data_pull_inspect.ipynb
│
├── src/                      # Reusable Python functions/modules
│   └── wrds_utils.py
│
├── logs/                     # Query logs, validation reports
│
├── docs/                     # Notes, literature summaries, data dictionaries
│
├── requirements.txt
├── .env.example              # Template for credentials (never commit .env)
└── .gitignore
```

---

## Data Sources

| Database | Provider | Coverage | Status |
|---|---|---|---|
| IvyDB US (optionmsamp_us) | OptionMetrics / WRDS | SPX options — sample | Sample access |
| IvyDB Europe (optionmsamp_europe) | OptionMetrics / WRDS | OESX options — sample | Sample access |
| VIX Daily (cboe_all) | CBOE / WRDS | VIX index | Full access |
| Fed Rates (frb_all) | Federal Reserve / WRDS | US risk-free rates | Full access |
| Fama-French (ff_all) | Ken French / WRDS | Market factors | Full access |
| CRSP Sample (crspsamp_all) | CRSP / WRDS | US equity prices | Sample access |
| Penn World Tables (pwt_all) | PWT / WRDS | Macro / international | Full access |

> **Note:** Full OptionMetrics access (optionm_all, optionm_europe) is pending confirmation from WRDS library services. All analysis in this repository currently uses sample data for structural **exploration** only.

---

## Pipeline Layers

This project follows a strict read-only raw data policy:

1. **Raw** — Downloaded directly from WRDS. Never modified.
2. **Intermediate** — Cleaned, filtered, standardized. One file per source.
3. **Analysis-ready** — Merged, aligned by date, final dataset for regression.
4. **Outputs** — Tables and figures only. No data files.

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/iv-smile-spillovers.git
cd iv-smile-spillovers
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure WRDS credentials
```bash
cp .env.example .env
# Edit .env and add your WRDS username
```

### 4. Run notebooks in order
Start with `notebooks/00_wrds_setup_test.ipynb` to verify your WRDS connection.

---

## Reproducibility

All notebooks are numbered and must be run in order. Every data pull includes:
- Row count before and after filtering
- Missingness checks
- Date coverage validation
- Summary statistics

---

## License

This repository contains code only. No raw or processed data is included or will ever be committed. All data is subject to WRDS/OptionMetrics license restrictions.
