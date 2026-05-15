{{ config(materialized='view') }}

select
    date as rate_date,
    currency_code,
    rate as to_usd_rate
from {{ source('raw', 'fx_rates') }}