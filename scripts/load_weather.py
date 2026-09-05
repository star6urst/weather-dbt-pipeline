"""
Fetch 1 year of historical daily weather data from Open-Meteo for 5 cities
and load it into a BigQuery table in the weather_raw dataset.
"""

import requests
import pandas as pd
from google.cloud import bigquery

# ---- Config ----

PROJECT_ID = "project-256beac9-89c1-4aed-ab4" 
DATASET = "weather_raw"
TABLE = "daily_weather"

CITIES = {
    "Reykjavik": {"lat": 64.1466, "lon": -21.9426},
    "Phoenix": {"lat": 33.4484, "lon": -112.0740},
    "Singapore": {"lat": 1.3521, "lon": 103.8198},
    "Mumbai": {"lat": 19.0760, "lon": 72.8777},
    "London": {"lat": 51.5072, "lon": -0.1276},
}

START_DATE = "2025-01-01"
END_DATE = "2025-12-31"

DAILY_VARS = [
    "temperature_2m_max",
    "temperature_2m_min",
    "temperature_2m_mean",
    "precipitation_sum",
    "windspeed_10m_max",
    "relative_humidity_2m_mean",
    "uv_index_max",
    "surface_pressure_mean",
]

BASE_URL = "https://archive-api.open-meteo.com/v1/archive"


def fetch_city_data(city_name, lat, lon):
    """Fetch historical daily weather for one city, return as a DataFrame."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": START_DATE,
        "end_date": END_DATE,
        "daily": ",".join(DAILY_VARS),
        "timezone": "auto",
    }
    resp = requests.get(BASE_URL, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    df = pd.DataFrame(data["daily"])
    df["city"] = city_name
    df["latitude"] = lat
    df["longitude"] = lon
    return df


def main():
    print("Fetching data for all cities...")
    all_dfs = []
    for city, coords in CITIES.items():
        print(f"  - {city}")
        df = fetch_city_data(city, coords["lat"], coords["lon"])
        all_dfs.append(df)

    full_df = pd.concat(all_dfs, ignore_index=True)
    full_df["time"] = pd.to_datetime(full_df["time"])

    print(f"Total rows: {len(full_df)}")
    print(full_df.head())

    # ---- Load into BigQuery ----
    client = bigquery.Client(project=PROJECT_ID)
    table_ref = f"{PROJECT_ID}.{DATASET}.{TABLE}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # overwrite each run; fine while iterating
        autodetect=True,
    )

    print(f"Loading into {table_ref} ...")
    load_job = client.load_table_from_dataframe(full_df, table_ref, job_config=job_config)
    load_job.result()  # wait for the job to finish

    table = client.get_table(table_ref)
    print(f"Loaded {table.num_rows} rows into {table_ref}")


if __name__ == "__main__":
    main()
