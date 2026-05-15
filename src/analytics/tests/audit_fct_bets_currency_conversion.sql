-- This test ensures that every bet with a wager has a successful currency conversion to USD.
-- If wager_usd is 0 but wager was not, it means the FX join failed (missing rate).

select
    bet_id,
    wager,
    wager_usd
from {{ ref('fct_bets') }}
where wager > 0 and (wager_usd = 0 or wager_usd is null)
