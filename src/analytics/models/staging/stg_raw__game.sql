{{ config(materialized='view') }}

select
    id as game_id,
    "name" as game_name,
    vertical,
    created_at
from {{ source('raw', 'game') }}