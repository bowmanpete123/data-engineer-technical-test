{#
Elevator Pitch: This dimension tracks the possible outcomes of a bet (e.g., Won, Lost) and includes a 'Pending' status.
Technical Detail: Unions stg_raw__bet_outcome with a synthetic row (id: -1) to handle un-settled bets in fact tables.
#}

{{ config(materialized='table') }}

select
    bet_outcome_id,
    outcome
from {{ ref('stg_raw__bet_outcome') }}

UNION ALL

select
    -1 as bet_outcome_id,
    'pending' as outcome