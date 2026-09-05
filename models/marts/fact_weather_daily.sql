select
    stg.observation_date,
    dc.city,
    stg.temp_max_c,
    stg.temp_min_c,
    stg.temp_mean_c,
    stg.precip_mm,
    stg.windspeed_max,
    stg.humidity_mean_pct,
    stg.uv_index_max,
    stg.pressure_mean

from {{ ref('stg_daily_weather') }} as stg

left join {{ ref('dim_city') }} as dc
    on stg.city = dc.city

left join {{ ref('dim_date') }} as dd
    on stg.observation_date = dd.observation_date