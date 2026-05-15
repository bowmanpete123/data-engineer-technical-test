{{ config(materialized='view') }}

select
    id as bet_id,
    user_id,
    bet_outcome_id,
    game_id,
    wager,
    is_cash_wager,
    -- Handling potential data quality issues: zero out negative winnings and ensure NULLs are handled
    GREATEST(0, winnings) as winnings,
    created_at,
    settled_at
from {{ source('raw', 'bet') }}