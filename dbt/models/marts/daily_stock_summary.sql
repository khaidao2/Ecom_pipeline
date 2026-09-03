-- Mart model for daily stock summary
-- models/marts/daily_stock_summary.sql

with daily_prices as (
    select
        symbol,
        trade_date,
        open_price,
        high_price,
        low_price,
        close_price,
        volume,
        round(
            (close_price - lag(close_price) over (
                partition by symbol 
                order by trade_date
            )) / lag(close_price) over (
                partition by symbol 
                order by trade_date
            ) * 100, 
            2
        ) as daily_return_pct,
        -- Calculate moving averages
        round(avg(close_price) over (
            partition by symbol 
            order by trade_date 
            rows between 19 preceding and current row
        ), 2) as ma_20,
        round(avg(close_price) over (
            partition by symbol 
            order by trade_date 
            rows between 49 preceding and current row
        ), 2) as ma_50
    from {{ ref('stg_stock_prices') }}
)

select
    symbol,
    trade_date,
    open_price,
    high_price,
    low_price,
    close_price,
    volume,
    daily_return_pct,
    ma_20,
    ma_50,
    case 
        when ma_20 > ma_50 then 'BUY'
        when ma_20 < ma_50 then 'SELL'
        else 'HOLD'
    end as signal,
    current_timestamp() as processed_at
from daily_prices
