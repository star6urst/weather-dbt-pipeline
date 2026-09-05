select distinct
    city,
    latitude,
    longitude

from {{ ref('stg_daily_weather') }}