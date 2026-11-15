# MESORA national prototype

Run `python3 mesora-site/model/train_national.py` from the extracted archive root.
Requires Python 3 and NumPy. Frozen inputs are in work/data/national and work/data/water.csv.
The output directory mesora-site/dist/data must exist. The script creates it if its parent exists.

Source catalog: USDA NASS public records via ProductOfAmerica/usda-county-yields,
pinned commit 9aac7d9d76921af42d94a828d3460da9c0a12a07. Data snapshot October 17, 2026.
NASA POWER: 2015–2025 monthly weather at county centroids.
USGS: county water-use estimates for 2015, version 2.0, DOI 10.5066/F7TB15V5.
Census: 2026 TIGERweb county boundaries, simplified for display.

Training: 2016–2023. Hyperparameter tuning: train through 2021, validate 2022–2023.
Held-out evaluation: 2024–2025. No synthetic labels. Models are not rotation trials.
County historical crop means are computed using training-year values only.
National map coverage does not imply available training data for every crop/county.

The browser engine.js reproduces the ridge regression and applies explicit ranking
and water-budget scenario assumptions. Data-center effects are sensitivity scenarios,
not learned causal effects. See the live Data & model page for the full equations.

## ML rotation planner release

The planner loads `public/data/ml-model.json`: three gradient-boosted tree models fitted to observed USDA county yields and NASA POWER weather. Install `model/requirements-ml.txt`, then run `python model/train-weather-ml.py` from the repository root to regenerate it from the included frozen NASA/USDA files. Nine exported Python predictions are checked against browser inference by `npm test`. Training includes the Union County frozen daily NASA record, aggregated to monthly crop-year inputs.

2016–2021 early training; 2022–2023 hyperparameter validation; final fit 2016–2023; untouched evaluation 2024–2025. No test-year labels enter fitting or hyperparameter selection. Geographic transfer outside training counties is flagged as unvalidated. Source snapshots and crop-specific errors are included in the model artifact.

The constrained sequence search uses the learned yield predictions relative to county history plus estimated irrigation and crop-family preferences. Every planning slot uses a different historical NASA weather analog. These are conditional scenarios, not future weather forecasts. Data Center consumption affects only the explicitly assumed farm water budget; causal yield losses are not learned or claimed. Cotton and sorghum have no labels in this release and are excluded from ML ranking.
