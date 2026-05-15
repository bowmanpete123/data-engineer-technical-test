{{ config(materialized='view') }}

select
    id as bet_outcome_id,
    outcome
from {{ source('raw', 'bet_outcome') }}