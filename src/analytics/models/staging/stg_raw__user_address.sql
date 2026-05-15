{{ config(materialized='view') }}

select
    user_id,
    address,
    country_code
from {{ source('raw', 'user_address') }}