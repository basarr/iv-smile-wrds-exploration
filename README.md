# Implied Volatility Smile Spillovers
### Preliminary Data Infrastructure — Bachelor Thesis
**University of Amsterdam — Amsterdam Business School**

| | |
|---|---|
| **Author** | Başar Hacımustafaoğlu |
| **Student Number** | 1******6 |
| **Programme** | BSc Economics and Business Economics (Finance) |
| **Course** | 6013B0520Y — Bachelor Thesis Finance |
| **Topic Code** | AP-33 — Implied Volatility Smile Spillovers |
| **Academic Year** | 2025/26, Semester 2 |
| **Supervisor** | TBC |

---

## 1. Research Question

> *Does a change in the implied volatility smile of the US equity options market have predictive power for the implied volatility smile of the European equity options market?*

The empirical strategy exploits the institutional time-zone lead–lag between US and European markets. European equity markets (e.g., Xetra) close approximately 4.5 hours before US markets (NYSE/NASDAQ) on the same calendar day. This creates a natural one-day lag structure: US smile parameters observed on day *t* can be examined for predictive power over European smile parameters on day *t+1*, without requiring intraday data.

This question falls within the third research slot defined in the AP-33 topic brief: *"Does a change in the volatility smile have predictive power in other markets?"* The methodology follows the regression-based framework advocated in the starting literature, applied to a cross-regional pair of equity index option markets.

---

## 2. Theoretical Background

The Black–Scholes–Merton model (Black and Scholes, 1973; Merton, 1973) implies that all options on the same underlying asset should have identical implied volatilities regardless of strike price or maturity. In practice, this is violated: implied volatility varies systematically across strikes and maturities, producing patterns known as the *volatility smile* or *volatility smirk*. This violation is well-documented across asset classes and geographies (Rubinstein, 1994; Peña, Rubio and Serna, 1999; Tompkins, 2001).

This project parameterises the smile using three scalar quantities per market per day, following the delta-based convention of Malz (1997):

| Parameter | Formula | Interpretation |
|---|---|---|
| ATM IV | IV of call at Δ = 50 | Level of implied volatility |
| Skew | IV of put(Δ=25) − IV of call(Δ=75) | Asymmetry of the smile; equals −*rr* in Malz (1997) notation |
| Curvature | IV of put(Δ=25) + IV of call(Δ=75) − 2 × ATM | Convexity of the smile; equals 2×*str* in Malz (1997) notation |

**Note on sign and scale conventions:** Malz (1997) defines the risk reversal as *rr* = call(Δ=0.25) − call(Δ=0.75) and the strangle as *str* = [call(Δ=0.25) + call(Δ=0.75)]/2 − ATM. Our skew equals −*rr* (sign reversed) and our curvature equals 2×*str* (scaled by two). These differences are notational; the economic content is identical. They are documented here to ensure reproducibility.

The broader empirical framework — standardised smile surfaces, cross-market comparison, and regression-based stability testing — follows Tompkins (2001). The spillover motivation follows Chen et al. (2022), who document a network structure of implied volatility spillovers across global index option markets.

---

## 3. Starting Literature

The following references constitute the anchor literature for this thesis, as specified in the AP-33 topic brief:

- Black, F. and Scholes, M. (1973). The pricing of options and corporate liabilities. *Journal of Political Economy*, 81(3), 637–654.
- Chen, J., Han, Q., Ryu, D. and Tang, J. (2022). Does the world smile together? A network analysis of global index option implied volatilities. *Journal of International Financial Markets, Institutions and Money*, 77, 101497.
- Chen, D., Guo, B. and Zhou, G. (2023). Firm fundamentals and the cross-section of implied volatility shapes. *Journal of Financial Markets*, 63, 100771.
- Hull, J. (2021). *Options, Futures and Other Derivative Securities* (11th ed.). Pearson Education.
- Malz, A.M. (1997). Estimating the probability distribution of the future exchange rate from option prices. *Journal of Derivatives*, 5(2), 18–36.
- Merton, R.C. (1973). Theory of rational option pricing. *Bell Journal of Economics*, 4(1), 141–183.
- Peña, I., Rubio, G. and Serna, G. (1999). Why do we smile? On the determinants of the implied volatility function. *Journal of Banking and Finance*, 23(8), 1151–1179.
- Rubinstein, M. (1994). Implied binomial trees. *Journal of Finance*, 49(3), 771–818.
- Tompkins, R.G. (2001). Implied volatility surfaces: Uncovering regularities for options on financial futures. *European Journal of Finance*, 7(3), 198–230.

---

## 4. Repository Structure

```
.
├── data/
│   ├── raw/                        # Immutable. Never modified after download.
│   │   ├── window_eu_2013/         # EU sample pull: 2013-01-01 to 2013-04-30
│   │   └── window_us_2014/         # US sample pull: 2014-01-01 to 2014-04-30
│   ├── intermediate/               # Cleaned, standardised, not yet merged.
│   │   ├── eu2013_analysis_ready__<timestamp>.csv
│   │   └── us2014_analysis_ready__<timestamp>.csv
│   ├── analysis_ready/             # Final merged dataset (not yet built).
│   └── outputs/                    # Tables, figures, regression results.
│
├── notebooks/                     # Jupyter notebooks — must be run in order.
│   ├── 00_wrds_setup_test.ipynb   # WRDS connection and subscription audit      ✅
│   ├── 01_data_pull_inspect.ipynb # Full database inspection and pull log       ✅
│   ├── 02_window_pulls.ipynb      # Targeted sample pulls for both markets      ✅
|   ├── 03a_pipeline_eu_2013.ipynb # EU smile pipeline (Adidas options)          ✅
|   ├── 03b_pipeline_us_2014.ipynb # US smile pipeline (Apple options)           ✅
|   ├── 04_merge_align.ipynb       # Merge EU + US panels, build lag structure   ✅
|   └── 05_regression.ipynb        # Spillover regression analysis               ✅
│
├── logs/                           # Timestamped query logs and validation reports
│
├── docs/                           # Notes, data dictionaries, literature summaries
│
├── requirements.txt
├── .env.example                    # Template for WRDS credentials (never commit .env)
└── .gitignore
```

---

## 5. Data Sources

| Database | Provider | Variable | Access Status |
|---|---|---|---|
| IvyDB US (`optionmsamp`) | OptionMetrics / WRDS | Apple option IV surface | Sample only |
| IvyDB Europe (`optionmsamp_europe`) | OptionMetrics / WRDS | Adidas option IV surface | Sample only |
| CBOE Indexes (`cboe_all`) | CBOE / WRDS | VIX daily index | Full access |
| Federal Reserve Board (`frb_all`) | Federal Reserve / WRDS | US risk-free rates | Full access |
| Compustat Global (`comp.g_exrt_dly`) | S&P / WRDS | GBP/USD, GBP/EUR exchange rates | Full access |
| Fama–French (`ff_all`) | Ken French / WRDS | Market factors | Full access |

> **Data access constraint:** Full OptionMetrics subscriptions (`optionm_all`, `optionm_europe_all`) are unavailable to students via WRDS. All analysis currently uses sample data — Apple (US) and Adidas (EU) options only — for pipeline development and structural validation. Results are not generalisable until full data access is obtained.

### EUR/USD Construction

The EUR/USD exchange rate is not directly available in the WRDS sample. It is constructed via triangular arithmetic using GBP-based pairs from `comp.g_exrt_dly` (annual rate, `exrattpd = 'AR'`, `fromcurd = 'GBP'`):

$$\text{EUR/USD} = \frac{\text{GBP/USD}}{\text{GBP/EUR}}$$

This construction is validated against known EUR/USD levels for the sample periods (Q1 2013: 1.28–1.37; Q1 2014: 1.35–1.39).

---

## 6. Pipeline Description

### 6.1 Data Pipeline Layers

This project enforces a strict read-only raw data policy. All transformations are applied in separate layers:

| Layer | Location | Description |
|---|---|---|
| Raw | `data/raw/` | Downloaded from WRDS. Never modified. |
| Intermediate | `data/intermediate/` | Cleaned, filtered, smile parameters computed. |
| Analysis-ready | `data/analysis_ready/` | Merged EU + US panel, aligned by date. *(Not yet built.)* |
| Outputs | `data/outputs/` | Tables and figures only. No data files. |

### 6.2 Smile Construction (Notebooks 03a and 03b)

For each (date × days-to-maturity) observation, three scalar smile parameters are computed from the OptionMetrics implied volatility surface (`vsurface` table), following Malz (1997):

**ATM IV** — implied volatility of the call option at Δ = 50.

**Skew** — difference between the implied volatility of the 25-delta put and the 75-delta call:

$$\text{Skew}_{t,\tau} = \sigma_{\text{put},25} - \sigma_{\text{call},75}$$

**Curvature** — butterfly spread constructed from the two wing options and ATM:

$$\text{Curvature}_{t,\tau} = \sigma_{\text{put},25} + \sigma_{\text{call},75} - 2 \times \sigma_{\text{ATM}}$$

### 6.3 Delta Sign Conventions

OptionMetrics IvyDB Europe and IvyDB US store delta values differently. This is a non-obvious data quirk that must be handled explicitly:

| Database | Call delta | Put delta | Put identification |
|---|---|---|---|
| IvyDB Europe | +20 to +80 | −20 to −80 | Sign of delta (negative = put) |
| IvyDB US | +20 to +80 | +20 to +80 | `cp_flag` column (`'P'` = put) |

In the EU pipeline (03a), the 25-delta put is retrieved at `delta = −25`. In the US pipeline (03b), it is retrieved at `delta = 25` with `cp_flag == 'P'`. Both yield the same economic instrument; the lookup logic differs only in how puts are identified.

### 6.4 Sentinel Value Filtering

OptionMetrics encodes failed IV inversions as `−99`. These are filtered before any smile parameter computation. Additionally, all non-positive implied volatilities are removed. Row counts before and after filtering are logged for auditability.

---

## 7. Validation Standards

Every notebook includes the following checks before writing output files:

- Row count before and after each filter step
- Missingness check on all columns in the final panel
- Key uniqueness check (date × days-to-maturity)
- Date coverage validation (first date, last date, number of trading days)
- Summary statistics for all smile parameters
- Sanity check against known market levels for the sample period

All validation results are written to timestamped JSON log files in `logs/`.

---

## 8. Current Status

| Notebook | Status | Output |
|---|---|---|
| 00 — WRDS setup | ✅ Complete | Connection verified |
| 01 — Data inspection | ✅ Complete | Pull log saved |
| 02 — Window pulls | ✅ Complete | Raw CSVs in `data/raw/` |
| 03a — EU pipeline | ✅ Complete | `eu2013_analysis_ready__<timestamp>.csv` |
| 03b — US pipeline | ✅ Complete | `us2014_analysis_ready__<timestamp>.csv` |
| 04 — Merge and align | 🔲 Not started | — |
| 05 — Regression | 🔲 Not started | — |

---

## 9. Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/basarr/iv-smile-wrds-exploration.git
cd iv-smile-wrds-exploration
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure WRDS credentials
```bash
cp .env.example .env
# Edit .env and enter your WRDS username
```

### 4. Run notebooks in order
Begin with `00_wrds_setup_test.ipynb` to verify your WRDS connection before running any data pulls.

---

## 10. Reproducibility Statement

All notebooks are numbered and must be run in order. Given the same WRDS credentials and sample database access, running notebooks 00 through 03b in sequence will reproduce all intermediate files exactly. Outputs are timestamped to prevent accidental overwrites. Raw data files are never modified.

No raw or processed data is committed to this repository. All data is subject to WRDS and OptionMetrics licence restrictions.

---

## 11. Disclaimer

This repository contains preliminary infrastructure code for a bachelor thesis in progress. All results are based on sample data (single underlying per region) and are intended for pipeline development only. No conclusions about implied volatility spillovers should be drawn from the current outputs.
