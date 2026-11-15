# MESORA model notes and validation

This is an exploratory prototype, not a field-validated planting recommendation.

## Observed test performance

Ridge-regression models fitted through 2023 and evaluated on held-out 2024–2025 observations. Mean absolute error (MAE) is in bushels per acre. Baseline repeats the county/crop training-period mean.

| Crop | Train rows | Test rows | Model MAE | Baseline MAE |
|---|---:|---:|---:|---:|
| corn | 2499 | 553 | 17.55 | 19.27 |
| soybeans | 2203 | 490 | 5.29 | 5.16 |
| wheat | 1569 | 191 | 8.71 | 9.31 |

Soybeans did not outperform the baseline. These tests do not validate three-season rotations, data-center causal impacts, individual farms, or transfer to all unsampled counties.

## What is measured and what is assumed

NASA weather and USDA crop-yield labels are observations/derived public data. USGS water features are historical 2015 county withdrawals. Google water consumption is operator-reported for 2025. None is a direct measurement of water available to a selected farm.

The 20-crop planner uses indicative FAO water-demand ranges. Only corn, soybeans and winter wheat have trained yield models. Other crops have water-planning estimates only.

Supplementary water need = max(0, FAO demand × (1 + 0.04 × warming °C) − 0.7 × rainfall in the selected window). The 4% temperature adjustment and 70% effective-rainfall fraction are uncalibrated assumptions. The displayed water range is not a confidence interval. Rice excludes paddy seepage/establishment losses.

Rotation score = mean(predicted yield / county crop training mean) − 0.5 × summed shortfall / summed reference demand + 0.03 × (distinct crops − 1). Consecutive repeats are excluded in automatic ranking. Soil, pests, prices, yield benefits from rotation, and local crop suitability are not learned.

Data-center sensitivity: added demand = nearby reported annual consumption × growth fraction. Irrigation-budget reduction fraction = min(1, added demand / ((2015 county irrigation MGD + public-supply MGD) × 365) × assumed shared-water fraction). This is a dated-data sensitivity scenario, not a basin water balance or a measured farm impact. Unknown facility water use is not assumed to be zero.

## Training

400 sampled weather counties; crop-specific model states and record counts are in model.json. Alpha was selected on 2022–2023 after fitting 2016–2021; models were refit through 2023, then tested on 2024–2025. Features include 12 monthly rainfall totals, 12 monthly temperatures, coordinates, historical water withdrawals, county training-mean yield, and year trend. All-production-practice labels mix irrigated and rainfed yields.

The website uses historical or user-modified weather scenarios, not future weather forecasts.

## Reproduction

Download source-pipeline.zip and model.json from the Sources page. The frozen NASA and USDA-derived inputs, source commit, training script, and browser prediction engine are included.
## Simple crop-water framework

The main planner compares all 20 library crops using NASA rainfall in the selected window, FAO indicative demand ranges, the disclosed 70% effective-rainfall assumption and 4% per °C demand adjustment. Fit means the upper irrigation estimate is within budget; borderline means only the lower estimate is within budget; short means even the lower estimate exceeds budget. These categories are deterministic scenario checks, not calibrated probabilities. Options are sorted by category, then upper irrigation need. County-supported crops are shown first; a county yield record is not proof of suitability for an individual field. Previous crop is excluded from the featured next-crop cards only. No automatically alternating rotation is presented as an optimal recommendation.

## Current interface audit — November 15, 2026

The primary planner now uses recorded weather without invented warmer/drier adjustments. The data-center consumption subtotal is contextual only: the interface does not infer shared water or reduce a farm budget from geographical proximity. Previous crop and irrigation budget are supplied by the user. No automatic rotation score is presented or exported.

All 20 demand ranges were checked against FAO Chapter 3, Table 14. These are indicative growing-period values, not locally calibrated evapotranspiration. The 70% usable-rainfall fraction and broad growing windows remain explicitly labeled assumptions. Monthly totals do not resolve dry spells, growth-stage stress, soil storage, conveyance losses, or crop suitability. Zero calculated supplementary irrigation is not a guarantee that irrigation will be unnecessary.

Yield MAE was recomputed from the 1,234 held-out observed labels and the deployed prediction function. This confirms the reported model error, not rotation accuracy. Soybean regression remains experimental and underperformed the historical-average baseline.

Earlier scenario formulas above document the legacy experimental engine; warming, rainfall-change, and shared-water adjustments are fixed to zero in the current interface.
