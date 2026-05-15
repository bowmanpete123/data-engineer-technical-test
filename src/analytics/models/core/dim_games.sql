{#
Elevator Pitch: This dimension lists all games and their associated business verticals.
Technical Detail: Clean representation of the stg_raw__game model.
#}

{{ config(materialized='table') }}

select
    game_id,
    game_name,
    vertical,
    created_at
from {{ ref('stg_raw__game') }}