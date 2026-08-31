-- Staging model for raw stock prices
-- models/staging/stg_stock_prices.sql

with source as (
    select * from {{ source('raw', 'stock_prices') }}
),

renamed as (
    select
        symbol,
        trade_date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        cast(created_at as timestamp) as loaded_at
    from source
)

select * from renamed
