select
    city,
    latitude,
    longitude,
    cast(time as date) as observation_date,
    temperature_2m_max as temp_max_c,
    temperature_2m_min as temp_min_c,
    temperature_2m_mean as temp_mean_c,
    precipitation_sum as precip_mm,
    windspeed_10m_max as windspeed_max,
    relative_humidity_2m_mean as humidity_mean_pct,
    uv_index_max as uv_index_max,
    surface_pressure_mean as pressure_mean

from {{ source('weather_raw', 'daily_weather') }}