# MESORA

Where agriculture meets the age of AI.

MESORA examines how climate and expanding infrastructure may affect agricultural water resources, then translates evidence and clearly defined risks into adaptive rotation strategies.

## Deploy a public website

**Vercel:** import this repository with framework preset Other. The included `vercel.json` publishes `public/` and rewrites `/api/*` into `api/data.mjs`. Deployment runs `npm test` before publishing. This API route is required for locations outside the saved reference area.

[Deploy MESORA to Netlify](https://app.netlify.com/start/deploy?repository=https://github.com/cozmikchaos/mesora)

Connect this repository with your Netlify account. The included `netlify.toml` publishes `public/` and routes the data endpoints through a serverless function. The host assigns a public `*.netlify.app` address; viewers do not need accounts. A custom domain can be connected later. The site is not live on a new hosting address merely because this code is on GitHub.

Cloudflare alternatives:

- **Pages:** import this repository, choose no framework and no build command, and set the output directory to `public`. The `functions/api/[[path]].js` endpoint handles external data requests. The resulting address is `*.pages.dev`.
- **Workers:** use the included `wrangler.jsonc`; the worker serves `public` assets and `/api/*`. Deployment requires your own Cloudflare account.

GitHub Pages alone cannot run the included server endpoints. Use one of the server-capable configurations above for the full application.

## Run locally

Requires Node.js 22 or newer. No application dependencies are needed for the local server.

```sh
npm start
```

Open http://127.0.0.1:8765/#explore. The Union County, NC reference point loads frozen, sourced observations. Other points query the public source services. Map imagery remains remotely hosted.

```sh
npm test
```

## Application

- Farm selection on satellite imagery, boundary drawing/upload, and approximate area.
- NASA SMAP, IMERG, temperature and historical Landsat imagery; USDA cropland; USGS watershed/aquifer context; drought and monitoring layers.
- Water-quality station observations with units, dates, qualifiers and trends.
- NASA daily-weather-based reference evapotranspiration and multiyear rotation screening.
- Explicit climate and infrastructure simulations with shared-supply gating.
- Source and method documentation and downloadable plans.

See [the implementation report](public/data/v2/implementation-report.md) for tested integrations and remaining limitations.

## Scientific scope

The rotation engine is transparent, rule-based planning, not a field-validated prediction of the best crop rotation. Numerical SMAP time series are not connected; soil-moisture map images do not become numeric farm measurements. Crop calendars and coefficients require local review. No verified connection between the demonstration farm and a data-center water supply has been established. Scenario allocation effects require an explicit user assumption.

NASA POWER daily inputs, NRCS SSURGO, USGS monitoring, and Water Quality Portal samples are real sourced data. Some records are frozen snapshots and are labeled with their dates. The 70% effective-rainfall fraction and scoring indicators are model assumptions. Software tests do not establish agronomic accuracy.

## Files

- `public/`: browser application, branding, and sourced snapshots.
- `source/server.mjs`: allowlisted public-data request endpoints.
- `netlify/functions/`: Netlify route adapter.
- `functions/api/`: Cloudflare Pages route adapter.
- `worker/` and `wrangler.jsonc`: Cloudflare Workers deployment.
- `model/`: retained experimental yield-model scripts, separate from the rotation engine.
- `tests/`: planning and hosting checks.

No API credentials are included. Current public endpoints work without credentials at their tested access level; agencies may impose rate limits. Higher-volume USGS use can require a key. Never commit provider secrets.

## Attribution

Public Evidence Project / Compute Atlas by Edward Kubiak, CC BY 4.0, provides source-linked infrastructure records. These are not a definitive operating-facility inventory. Google environmental reports provide operator-reported locality totals. Federal source data retain their source-specific attribution. Esri imagery and OpenStreetMap search are requested from their services with attribution. Leaflet and Leaflet.VectorGrid retain their package notices. The MESORA logo is the user-supplied brand asset.
