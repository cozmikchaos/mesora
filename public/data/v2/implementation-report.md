# MESORA implementation and verification

Updated November 15, 2026.

## Working application

- Satellite map with address/place search, point selection, polygon drawing, GeoJSON boundary upload, approximate area, and county lookup. A vector circle marks the analysis point, eliminating the missing marker-image dependency.
- One selected farm shared by Explore, Water Intelligence, Climate Analysis, Rotation Planner, Compare, and Sources & Methods.
- Map overlays: USDA 2024 cropland, NASA SMAP L4, GPM IMERG, MODIS temperature, historical Landsat WELD, USGS HUC12 watershed, regional aquifer extents, groundwater stations, water-quality stations, and official November 10, 2026 drought polygons. Date, source, spatial scale, units or categorical meaning appear with each layer. No numeric soil-moisture measurements are decoded from colors.
- Server endpoints for NASA daily weather, NRCS soil attributes, USGS observations and monitoring locations, watershed intersection, Water Quality Portal stations/samples, and submitted place searches. Inputs are bounded and external hosts are fixed.
- Water-quality station selection, parameter/unit/sample-fraction selection, dated sample tables, qualified results and comparable-observation charts.
- NASA annual and monthly weather views, selectable historical windows, descriptive trend slopes, and derived reference evapotranspiration.
- Rule-based crop-rotation optimization with five field crops, optional rye cover, 2–4 harvest years, previous crop, area, crop exclusions, pH, drainage, irrigation constraints, and weighted priorities. At least three distinct strategies appear when feasible. No candidates are fabricated when constraints eliminate them. Earlier crop history and supply notes are retained for review; the most recent crop drives the immediate-repeat exclusion.
- Scenario comparison: historical reference, explicitly simulated climate stress, and combined stress. Shared supply must be explicitly assumed before any infrastructure demand reduces farm allocation. Scenario changes do not alter observations.
- Plan download with farm inputs, formulas, water estimates, scoring components, and limitations.

## Real data

The reproducible Union County reference point is 34.98°N, 80.55°W. Its frozen inputs include NASA POWER daily 2015–2025 weather, SSURGO component horizons, USGS HUC12 geometry, USGS regional observations and monitoring locations, 409 Water Quality Portal station records, and 761 selected measured water-quality results dated January 6, 2022 through December 10, 2025. Retrieval date is November 15, 2026. Samples are regional context; no farm-supply relationship is presumed. Source queries and dates are retained in the JSON files.

Public Evidence Project / Compute Atlas records are source-linked infrastructure evidence with varying location precision, not a definitive operating-facility inventory. Attribution: Public Evidence Project / Compute Atlas by Edward Kubiak, CC BY 4.0. Existing Google operator-reported 2025 water totals remain locality reports. No facility water use is invented.

## Estimates and simulations

Reference ETo uses FAO-56 Penman–Monteith with NASA temperature, radiation, humidity, wind and elevation. Declared solar units are checked. Monthly estimates use averages of daily maximum/minimum temperatures. Mean relative humidity and zero soil heat flux are approximations. Crop coefficients and North Carolina reference calendars, plus a 70% effective-rainfall assumption, produce indicative monthly supplementary irrigation. Excess rainfall is not carried between months. No field-calibrated soil-water balance, effective rooting depth, irrigation efficiency, or dry-spell model is implied.

The score is a transparent preference-weighted heuristic. Soil scores are diversity/cover proxies, resilience uses reference drought tolerance, and readiness uses pH/drainage review flags. Scores do not represent probabilities, economic returns, measured soil improvement, or predicted yields. The cover-crop coefficients use a disclosed small-grain proxy. Winter crops belong to harvest-year cycles and start in the preceding autumn. Local seedbed temperatures, cultivars, pest history, markets and soil tests need review.

Infrastructure simulator: annual demand × (1 − cooling savings) × (1 − reclaimed share) × seasonal fraction. Only an explicit shared-supply assumption allows the entered farm allocation share to become a budget reduction, converted using 1 mm·ha = 10 m³. This is a simulation, not a measured or inferred loss.

## Verification performed

- Browser: satellite imagery and vector marker; drawn polygon area and selected county; water-quality station records; climate graph; rotation generation; changing inputs and scenario comparison; no console errors in the tested workflow.
- Data access: HTTP 200 from NASA POWER monthly and daily APIs, GIBS capabilities and SMAP tile, SSURGO POST query, USGS latest/monitoring OGC requests, Water Quality Portal station/results queries, USDA image service/export metadata, HUC12 query, official drought archive, and official-viewer aquifer tile.
- Server: geocode and soil endpoints return real source data; malformed coordinates and station IDs return HTTP 400.
- Algorithm: source solar-unit conversion equivalence, rejection of missing daily values, deterministic ranking, water-budget rejection, crop exclusions, no consecutive repeats, calendar conflict screening, drainage restriction, regional-calendar confirmation, zero-weight validation, m³/mm conversion, scenario isolation, shared-supply gating, polygon closure/coordinate/self-intersection validation, CSV quoted-field parsing, and rejection of empty numeric samples.
- Union reference fixture: 114 modeled candidates meet the default 300 mm/year water budget; the interface selects three diverse candidates. This is software verification, not field validation.

## Remaining limits and credentials

No credentials are required for the tested public endpoints at their current access level. USGS may require an API key for higher rate limits. Numeric SMAP time-series extraction and quantitative IMERG trend extraction are not connected; public imagery is available. NASA Earthdata-authenticated numerical workflows would require a separately verified data-access integration. The numeric climate analysis currently uses NASA POWER.

The existing three-crop ridge yield experiment is retained separately; it is not the rotation optimizer. No learned rotation model or field-validated best-rotation claim is made. No documented shared supply between the Union reference farm and a listed data center has been established. Facility cooling/source fields remain unknown where evidence is missing. Water-quality observations are not used as direct farm constraints without a documented supply link.

The North Carolina calendar is the demo reference. Nationwide map selection is supported, with explicit local-calendar confirmation required outside NC. All external sources may be unavailable or incomplete; the application shows missing-data messages and does not replace missing observations with fabricated samples.

## Reproduce locally

From the mesora-site checkout: `node source/dev.mjs`, then open `http://127.0.0.1:8765/#explore`. The Union snapshot loads without external data calls; basemap/overlay tiles still use public remote services. To build the deployment worker: `python3 source/build.py`. Tests are in the workspace's `work/v2/test-rotation.cjs`.

## Vercel submission repair

The Vercel deployment now includes a Node API entry point and explicit `/api/*` rewrites. The previous portable release lacked this Vercel adapter, causing new-location requests to return an HTML missing-page response. The client checks response formats and can recover through a public read-only data bridge. Weather readiness is updated independently of slower monitoring requests, so an unrelated missing source does not block rotation calculations.

Live Vercel checks: Berkeley County SC, Story County IA, and Fresno County CA each returned 4,018 daily NASA weather dates and station CSV responses. Soil requests returned mapped horizons in Berkeley/Fresno and no mapped rows at the tested Story point; absent coverage is not fabricated. Browser checks confirmed Berkeley crop-rotation generation and dated water-quality samples, and infrastructure scenarios using both entered demand and reported operator water totals.

The Data centers view exposes source-linked records and operator-reported locality water totals. Report-derived demand can seed an explicitly labeled growth scenario. Sources is now a dataset-only view. Drawing a crossed click sequence can be repaired to an outer boundary with a review message; this area is approximate and must be checked on the map. Numerical inputs accept report-derived demand values rather than silently blocking form submission on integer-step validation.
