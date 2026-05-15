{#
Elevator Pitch: This dimension provides a single, conformed view of all real users and their addresses.
Technical Detail: Joins stg_raw__users and stg_raw__user_address on user_id, filtering out internal test users.
#}

{{ config(materialized='table') }}

with users as (
    select * from {{ ref('stg_raw__users') }}
    where not is_test_user
),

addresses as (
    select * from {{ ref('stg_raw__user_address') }}
)

select
    u.user_id,
    u.user_name,
    u.currency_code,
    u.created_at,
    a.address,
    a.country_code
from users u
left join addresses a on u.user_id = a.user_id