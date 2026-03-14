# Implied Volatility Smile Spillovers — AP-33
### A Self-Directed Empirical Exercise in Quantitative Finance
**University of Amsterdam — Amsterdam Business School**

| | |
|---|---|
| **Author** | Başar Hacımustafaoğlu |
| **Student Number** | 14866196 |
| **Programme** | BSc Economics and Business Economics (Finance) |
| **Course** | 6013B0520Y — Bachelor Thesis Finance |
| **Topic Code** | AP-33 — Implied Volatility Smile Spillovers |
| **Academic Year** | 2025/26, Semester 2 |

---

## ⚠️ Important Disclaimer — Please Read First

**This repository does not represent my assigned bachelor thesis.**

AP-33 (Implied Volatility Smile Spillovers) was a topic I considered during the thesis allocation process but was ultimately not assigned to. After receiving my actual thesis assignment, I had already built a significant amount of infrastructure for AP-33 and decided to keep going with it — not as a thesis, but as a **self-directed learning project** to get hands-on experience with options data, the OptionMetrics / WRDS environment, and empirical time series econometrics.

Everything in this repository is **exploratory and educational**. It is not submitted for assessment, does not represent my actual thesis work, and does not conflict with any UvA academic integrity requirements. My actual thesis is conducted and submitted separately under its assigned topic code.

In short: this is me teaching myself how to build a quantitative finance data pipeline from scratch, using a research question I found genuinely interesting. The results are not generalisable (see limitations below), and that was never the point.

---

## What This Project Is About

The core question is simple: **does the shape of the implied volatility smile in the US options market on day *t* tell us anything useful about the shape of the IV smile in the European options market on day *t+1*?**

This is called a *spillover* — the idea that information or risk premia from one market travel to another with a time delay. The one-day lag here is not arbitrary. It comes directly from market structure: European equity markets close roughly 4.5 hours before US markets on the same calendar day. So by the time the US smile is fully priced in, European markets have already shut. Whatever the US market "decides" that day — in terms of how investors price tail risk, skew, and convexity — the European market can only react the next morning.

The implied volatility smile itself is parameterised following **Malz (1997)** using three scalar quantities read off the OptionMetrics volatility surface at fixed delta nodes:

| Parameter | Formula | What it measures |
|---|---|---|
| **ATM IV** | IV at Δ = 50 (call) | The overall level of implied volatility |
| **Skew** | IV(put Δ25) − IV(call Δ75) | How asymmetric the smile is — reflects fear of downside moves |
| **Curvature** | IV(put Δ25) + IV(call Δ75) − 2 × ATM | How "smiling" the smile is — reflects demand for wing options |

These three numbers compress the entire smile surface into something regression-friendly, per day, per maturity node. The idea of using standardised delta-based nodes comes from **Tompkins (2001)**, who showed that this approach produces comparable smile surfaces across markets and through time.

---

## The Papers Behind This

This project is grounded in a specific set of papers. They are worth understanding because they shaped every design decision made here.

**Malz (1997) — the smile parameterisation**
Malz proposed using options at fixed delta strikes (25Δ, 50Δ, 75Δ) to measure risk reversals and butterfly spreads in currency options markets. This project adapts the exact same parameterisation to equity options: skew = −risk reversal, curvature = 2 × butterfly spread. The sign and scale differences from Malz's original notation are documented explicitly in the code.

**Tompkins (2001) — cross-market smile comparison**
Tompkins studied implied volatility surfaces across multiple markets (equity, bonds, currencies, energy) and asked whether smiles show consistent patterns across markets and time. The key methodological contribution for this project is his use of *standardised* maturity and delta nodes to make smiles comparable — exactly what the delta-based Malz approach achieves. Tompkins also provided early evidence of commonality in smile shapes across markets, which is the empirical prior motivating the spillover hypothesis here.

**Chen, Han, Ryu and Tang (2022) — the direct motivation**
This is the most direct ancestor of this project. Chen et al. built a network model of implied volatility spillovers across 18 global index option markets and found significant directional transmission — particularly from the US (VIX) outward. The US → Europe direction was one of the strongest links in their network. This project attempts a simplified version of the same question: one US stock, one EU stock, one regression, three smile parameters. Their paper also motivated the inclusion of ΔVIX as a control variable, since it captures the global volatility shock component that would confound a purely bilateral regression.

**Peña, Rubio and Serna (1999) — smile determinants**
Peña et al. studied why the volatility smile exists and what macroeconomic variables drive its shape in the Spanish market. This paper is in the AP-33 starting literature and shaped the thinking around control variables: interest rate differentials, trading volume, and market-wide fear proxies all matter for the smile level, not just the lagged value of the smile itself. ΔVIX in our specification is a direct response to this insight.

**Newey and West (1994) — the standard error correction**
Implied volatility smile parameters are persistent time series — today's smile predicts tomorrow's smile. This means OLS residuals in any regression involving smile parameters will be autocorrelated, and standard OLS standard errors will be too small (giving spuriously significant t-statistics). Newey and West (1994) proposed an automatic procedure for selecting how many lags of autocorrelation to correct for, using the formula n = ⌊4(T/100)^(2/9)⌋ for the Bartlett kernel. This is implemented exactly in the regression notebook.

---

## What Was Actually Built

### The Data Pipeline

The full pipeline runs across seven numbered Jupyter notebooks:

```
00 — WRDS connection test and subscription audit
01 — Full OptionMetrics database inspection
02 — Targeted sample pulls for both markets
03a — EU smile pipeline (Adidas AG, Q1 2013)
03b — US smile pipeline (Apple Inc., Q1 2014)
04 — Merge and align EU + US panels (zero-row output — see below)
05 — Spillover regression (validation mode only)
```

The pipeline enforces a strict read-only raw data policy throughout. Raw CSVs from WRDS are never touched after download. Every transformation produces a new object, every filter step logs row counts before and after, and every output is timestamped to prevent overwrites.

### What the Smile Construction Actually Does

For each (date × maturity node) combination, the EU and US pipelines pull three numbers off the OptionMetrics volatility surface — the implied volatility at the 25Δ put, the 50Δ call (ATM), and the 75Δ call — and compute ATM IV, Skew, and Curvature. This sounds simple, but there are several non-obvious data handling issues that required careful attention:

**Delta sign conventions differ between IvyDB US and IvyDB Europe.** In IvyDB Europe, put deltas are stored as negative numbers (−25 for a 25Δ put). In IvyDB US, all deltas are stored as positive numbers, and puts are identified via a separate `cp_flag` column. Getting this wrong produces silently incorrect smile parameters — the 25Δ put gets confused with a 25Δ call, and the skew flips sign. Both pipelines handle this explicitly.

**OptionMetrics encodes failed IV inversions as −99.** When Black-Scholes cannot be inverted (e.g., for deep in-the-money options or when bid-ask spreads are too wide), OptionMetrics records the implied volatility as −99 rather than NaN. These sentinel values must be filtered before computing any smile parameter. If even one is missed, it contaminates the curvature calculation.

**The EUR/USD exchange rate is not directly available in the WRDS student sample.** It was reconstructed from GBP/USD and GBP/EUR pairs from Compustat Global via triangular arithmetic: EUR/USD = GBP/USD ÷ GBP/EUR. The constructed rate was validated against known Q1 2013 levels (1.28–1.37).

### The Regression Specification

Three separate OLS regressions, one per smile parameter:

$$Y^{EU}_{t+1} = \alpha + \beta_1 Y^{US}_t + \beta_2 \Delta\text{VIX}_t + \beta_3 Y^{EU}_t + \varepsilon_{t+1}$$

where *Y* is ATM IV, Skew, or Curvature respectively, and all standard errors are Newey-West HAC corrected (Bartlett kernel, automatic lag selection following Newey and West (1994)).

The coefficient of interest is β₁. If β₁ > 0 and statistically significant, the US smile parameter on day *t* predicts the EU smile parameter on day *t+1*, after controlling for the EU market's own persistence (β₃) and global volatility shocks (β₂).

The same three models were run at five maturity nodes (30, 60, 91, 182, 365 days), with the 30-day node as the primary specification (highest liquidity, VIX construction maturity, primary node in Chen et al. 2022) and the remaining four as robustness checks.

### What the Time Series Looks Like

The plot below shows EU (blue, solid) and US (orange, dashed) smile parameters over the sample period at the 30-day maturity node. Note: this is **validation-mode output only** — the EU and US windows do not overlap in calendar time, so Adidas data is used as a proxy for both sides during pipeline testing. This is not a thesis result.

![Smile parameters time series](data/outputs/figures/smile_params_timeseries__20260314_160035.png)

Even in validation mode, the plot is useful for checking that the pipeline produces structurally sensible numbers: ATM IV around 20%, skew negative (consistent with put demand exceeding call demand for a single stock), and curvature positive (consistent with wings being bid up relative to ATM).

---

## The Big Problem: Non-Overlapping Samples

The most significant limitation of this project, and the reason no actual spillover results exist, is that **the EU sample (Q1 2013) and the US sample (Q1 2014) cover completely different calendar periods**. When notebook 04 attempts to merge them on a date key — EU date *t+1* matched to US date *t* — zero rows are returned. The panel is structurally correct and fully schema-validated, but it is empty.

This happened because of a data access constraint. The full OptionMetrics subscriptions on WRDS (`optionm_all` and `optionm_europe_all`) are not available to students — only sample versions are, which cover restricted time windows per security. The Q1 2013 EU sample and Q1 2014 US sample were the only windows accessible for Adidas and Apple respectively. They do not overlap.

**The fix is straightforward in principle:** obtain full OptionMetrics access (via the university library or an alternative source such as Refinitiv Eikon, which is available at the UvA Roeterseiland campus), pull both markets for a common sample period, and re-run notebooks 04 and 05. The pipeline is built to handle this exactly — the merge logic, lag construction, regression specification, and output formatting are all complete and validated.

---

## Limitations — Full Accounting

This section is important. The limitations here are structural, not incidental.

**1. Single-stock data, not index options.**
The EU proxy is Adidas AG; the US proxy is Apple Inc. Neither is an equity index. The implied volatility smile of an individual stock is noisier, more idiosyncratic, and more sensitive to earnings announcements and firm-specific events than the smile of a broad index like EURO STOXX 50 or S&P 500. Chen et al. (2022), who this project draws most directly from, use index options throughout. Generalising from single-stock results to cross-market index-level spillovers is not valid. This is the primary reason the results should be treated as structural/pipeline validation rather than empirical findings.

**2. The EU and US samples do not overlap.**
Described in detail above. All regression output in notebook 05 is produced in "validation mode" — the regression runs EU data against itself (Adidas at *t* predicting Adidas at *t+1*) to confirm the pipeline works, not to test the spillover hypothesis. This is clearly labelled throughout.

**3. T = 9 observations per regression.**
Even in validation mode, the usable sample per maturity node after lag construction is 9 trading days — well below any reasonable threshold for OLS inference. All regressions are correctly skipped by a T < 10 guard in the code. The Newey-West correction requires a meaningful number of observations to estimate autocorrelation structure; with T = 9 and 4 regressors, there are only 5 degrees of freedom.

**4. No causal identification.**
The one-day lag structure provides a natural ordering (US closes after EU on the same day), but this does not identify a causal spillover. Overnight macro announcements, earnings releases, and common global factors (e.g., a Fed statement released after EU close) could produce a correlation between US *t* and EU *t+1* with no direct market-to-market transmission. The lag structure is suggestive, not causal.

**5. OLS assumes a linear, constant relationship.**
The regression specification assumes that the spillover — if it exists — is linear in the smile parameters and constant through time. In reality, spillovers are likely regime-dependent: stronger during high-volatility periods or market stress, weaker during calm periods. A more complete analysis would test for time variation (rolling regressions) or asymmetry (separate estimation for high and low VIX regimes). None of this is implemented here.

**6. The Newey-West lag is a simplified rule.**
The formula n = ⌊4(T/100)^(2/9)⌋ from Newey and West (1994) is passed directly as the HAC bandwidth rather than implementing their full two-step data-dependent procedure. This is standard in applied empirical finance and is explicitly documented in the code, but it introduces some arbitrariness in the standard error correction that a full implementation would resolve.

**7. EUR/USD is constructed, not directly observed.**
The EUR/USD rate used in the EU pipeline is computed from GBP-based pairs via triangular arithmetic. This construction introduces a potential compounding of measurement error from two separate exchange rate series. For a research paper, this would warrant a robustness check against a directly observed EUR/USD series.

---

## Repository Structure

```
.
├── data/
│   ├── raw/                          # Immutable. Never modified after download.
│   │   ├── window_eu_2013/           # EU sample: Adidas AG, Q1 2013
│   │   └── window_us_2014/           # US sample: Apple Inc., Q1 2014
│   ├── intermediate/                 # Cleaned, smile parameters computed.
│   │   ├── eu2013_analysis_ready__<timestamp>.csv
│   │   └── us2014_analysis_ready__<timestamp>.csv
│   ├── analysis_ready/               # Merged panel (zero-row; correct schema).
│   └── outputs/
│       └── figures/                  # Time series and diagnostic plots.
│
├── notebooks/
│   ├── 00_wrds_setup_test.ipynb      # WRDS connection and access audit       ✅
│   ├── 01_data_pull_inspect.ipynb    # Database schema inspection             ✅
│   ├── 02_window_pulls.ipynb         # Sample pulls for both markets          ✅
│   ├── 03a_pipeline_eu_2013.ipynb    # EU smile construction (Adidas)         ✅
│   ├── 03b_pipeline_us_2014.ipynb    # US smile construction (Apple)          ✅
│   ├── 04_merge_align.ipynb          # Merge + lag structure (zero-row out)   ✅
│   └── 05_regression.ipynb           # Regression (validation mode only)      ✅
│
├── logs/                             # Timestamped JSON logs from each run
├── docs/                             # Notes and literature summaries
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Data Sources

| Database | Provider | Content | Access |
|---|---|---|---|
| IvyDB US (`optionmsamp`) | OptionMetrics / WRDS | Apple option IV surface | Sample only |
| IvyDB Europe (`optionmsamp_europe`) | OptionMetrics / WRDS | Adidas option IV surface | Sample only |
| CBOE Indexes (`cboe_all`) | CBOE / WRDS | VIX daily index | Full |
| Federal Reserve (`frb_all`) | Federal Reserve / WRDS | US risk-free rates | Full |
| Compustat Global (`comp.g_exrt_dly`) | S&P / WRDS | GBP/USD, GBP/EUR FX rates | Full |
| Fama–French (`ff_all`) | Ken French / WRDS | Market factors | Full |

No raw or processed data is committed to this repository. All data is subject to WRDS and OptionMetrics licence restrictions.

---

## Setup

```bash
git clone https://github.com/basarr/iv-smile-wrds-exploration.git
cd iv-smile-wrds-exploration
pip install -r requirements.txt
cp .env.example .env        # add your WRDS username
```

Run notebooks in order starting from `00`. A WRDS account with OptionMetrics sample access is required for notebooks 02 onward.

---

## References

- Black, F. and Scholes, M. (1973). The pricing of options and corporate liabilities. *Journal of Political Economy*, 81(3), 637–654.
- Chen, J., Han, Q., Ryu, D. and Tang, J. (2022). Does the world smile together? A network analysis of global index option implied volatilities. *Journal of International Financial Markets, Institutions and Money*, 77, 101497.
- Chen, D., Guo, B. and Zhou, G. (2023). Firm fundamentals and the cross-section of implied volatility shapes. *Journal of Financial Markets*, 63, 100771.
- Hull, J. (2021). *Options, Futures and Other Derivative Securities* (11th ed.). Pearson Education.
- Malz, A.M. (1997). Estimating the probability distribution of the future exchange rate from option prices. *Journal of Derivatives*, 5(2), 18–36.
- Merton, R.C. (1973). Theory of rational option pricing. *Bell Journal of Economics*, 4(1), 141–183.
- Newey, W.K. and West, K.D. (1994). Automatic lag selection in covariance matrix estimation. *Review of Economic Studies*, 61(4), 631–653.
- Peña, I., Rubio, G. and Serna, G. (1999). Why do we smile? On the determinants of the implied volatility function. *Journal of Banking and Finance*, 23(8), 1151–1179.
- Tompkins, R.G. (2001). Implied volatility surfaces: Uncovering regularities for options on financial futures. *European Journal of Finance*, 7(3), 198–230.
