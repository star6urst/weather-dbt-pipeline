# Weather dbt Pipeline

An end-to-end analytics engineering project: raw weather data flows from a public API into BigQuery, then gets transformed into a tested, dimensional data model using dbt. A GitHub Actions CI pipeline runs the full build and test suite on every push, authenticating to Google Cloud with Workload Identity Federation instead of a static key.

## Architecture

```
Open-Meteo API
      │
      ▼
Python loader (scripts/load_weather.py)
      │
      ▼
BigQuery: weather_raw.daily_weather   (raw landing table)
      │
      ▼
dbt staging model: stg_daily_weather   (cleaned, renamed, typed)
      │
      ├──▶ dim_city
      ├──▶ dim_date
      │
      ▼
fact_weather_daily   (joined to both dimensions)
```

## Data

Daily historical weather observations for five cities chosen for climate contrast: Reykjavik, Phoenix, Singapore, Mumbai, and London. Covers one full calendar year (2025), sourced from the [Open-Meteo](https://open-meteo.com/) historical archive API. Variables include max/min/mean temperature, precipitation, wind speed, humidity, UV index, and surface pressure.

## Stack

- **Ingestion**: Python (`requests`, `pandas`) → BigQuery, via `google-cloud-bigquery`
- **Transformation**: dbt Core, `dbt-bigquery` adapter
- **Warehouse**: Google BigQuery
- **Testing**: dbt schema tests (`not_null`, `unique`, `relationships`)
- **CI/CD**: GitHub Actions, authenticating via Workload Identity Federation (no service account keys)

## Project structure

```
models/
├── staging/
│   ├── sources.yml           # declares the raw BigQuery source table
│   ├── stg_daily_weather.sql
│   └── stg_daily_weather.yml # tests for the staging model
└── marts/
    ├── dim_city.sql
    ├── dim_date.sql
    ├── fact_weather_daily.sql
    └── dim_city.yml          # tests for all three marts models
scripts/
└── load_weather.py           # fetches from Open-Meteo, loads into weather_raw
.github/workflows/
└── ci.yml                    # runs dbt build on every push via WIF
```

## Running it locally

1. Create a Python virtual environment and install dependencies:
   ```bash
   pip install dbt-bigquery google-cloud-bigquery pandas requests
   ```
2. Authenticate to Google Cloud (this project uses oauth/ADC, not a key file):
   ```bash
   gcloud auth application-default login
   ```
3. Load raw data into BigQuery:
   ```bash
   python scripts/load_weather.py
   ```
4. Install dbt packages and run the models:
   ```bash
   dbt deps
   dbt build
   ```

## Why Workload Identity Federation

This GCP project has an org policy (`iam.disableServiceAccountKeyCreation`) that blocks static service account keys outright. Rather than treat that as a blocker, this project uses it as an opportunity to set up the more modern, more secure authentication pattern: GitHub Actions exchanges a short-lived OIDC token for GCP credentials at runtime, scoped to this exact repository, with no long-lived secret stored anywhere.

## Notes

This is a portfolio/learning project built to practice analytics engineering fundamentals: warehouse design, dimensional modeling, automated testing, and CI for data pipelines. It replaces an earlier version of this same pipeline that ran locally on DuckDB, without dbt or CI.
