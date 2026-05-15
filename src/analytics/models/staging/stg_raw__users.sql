{{ config(materialized='view') }}

select
    id as user_id,
    "Name" as user_name,
    "IsTestUser" as is_test_user,
    "CurrencyCode" as currency_code,
    "CreatedAt" as created_at
from {{ source('raw', 'users') }}