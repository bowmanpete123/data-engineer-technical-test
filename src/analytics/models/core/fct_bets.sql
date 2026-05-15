{#
Elevator Pitch: The central fact table recording every individual bet and its financial performance in USD.
Technical Detail: Grain is one row per bet. Joins twice to fx_rates to convert wager (on created_at) and winnings (on settled_at) to USD.
#}

{{ config(materialized='table') }}

with bets as (
    select * from {{ ref('stg_raw__bet') }}
),

users as (
    select user_id, currency_code, is_test_user from {{ ref('stg_raw__users') }}
),

fx_rates as (
    select * from {{ ref('stg_raw__fx_rates') }}
)

select
    b.bet_id,
    b.user_id,
    COALESCE(b.bet_outcome_id, -1) as bet_outcome_id,
    b.game_id,
    b.wager,
    b.winnings,
    b.created_at,
    b.settled_at,
    -- Currency Conversion to USD
    b.wager * COALESCE(wager_fx.to_usd_rate, 1.0) as wager_usd,
    b.winnings * COALESCE(winnings_fx.to_usd_rate, 1.0) as winnings_usd
from bets b
inner join users u on b.user_id = u.user_id
-- Join for wager rate (at creation)
left join fx_rates wager_fx 
    on b.created_at::DATE = wager_fx.rate_date
    and u.currency_code = wager_fx.currency_code
-- Join for winnings rate (at settlement)
left join fx_rates winnings_fx
    on b.settled_at::DATE = winnings_fx.rate_date
    and u.currency_code = winnings_fx.currency_code
-- Filter out test users so fct_bets represents real business activity
where not u.is_test_user