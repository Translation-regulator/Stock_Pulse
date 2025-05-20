import pandas as pd
from utils.db import get_connection

def generate_twii_ohlc():
    conn = get_connection()
    df = pd.read_sql("SELECT date, open, high, low, close, volume, trade_count FROM twii_index", conn)
    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)

    # ========== 週線處理：以每週最後交易日為代表 ==========
    df['week_id'] = df['date'].dt.to_period("W").apply(lambda r: r.start_time)
    weekly_rows = []
    for _, group in df.groupby('week_id'):
        last_date = group['date'].max()
        weekly_rows.append({
            'date': last_date,
            'open': group.iloc[0]['open'],
            'high': group['high'].max(),
            'low': group['low'].min(),
            'close': group.iloc[-1]['close'],
            'volume': group['volume'].sum(),
            'trade_count': group['trade_count'].sum()
        })
    df_weekly = pd.DataFrame(weekly_rows)

    # ========== 月線處理：以每月最後交易日為代表 ==========
    df['month_id'] = df['date'].dt.to_period("M")
    monthly_rows = []
    for _, group in df.groupby('month_id'):
        last_date = group['date'].max()
        monthly_rows.append({
            'date': last_date,
            'open': group.iloc[0]['open'],
            'high': group['high'].max(),
            'low': group['low'].min(),
            'close': group.iloc[-1]['close'],
            'volume': group['volume'].sum(),
            'trade_count': group['trade_count'].sum()
        })
    df_monthly = pd.DataFrame(monthly_rows)

    # ========== 寫入資料庫（UPSERT 寫入） ==========
    cursor = conn.cursor()

    for _, row in df_weekly.iterrows():
        cursor.execute("""
            INSERT INTO twii_weekly (date, open, high, low, close, volume, trade_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open = VALUES(open),
                high = VALUES(high),
                low = VALUES(low),
                close = VALUES(close),
                volume = VALUES(volume),
                trade_count = VALUES(trade_count)
        """, (
            row['date'].date(),
            row['open'], row['high'], row['low'], row['close'],
            row['volume'], row['trade_count']
        ))

    for _, row in df_monthly.iterrows():
        cursor.execute("""
            INSERT INTO twii_monthly (date, open, high, low, close, volume, trade_count)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                open = VALUES(open),
                high = VALUES(high),
                low = VALUES(low),
                close = VALUES(close),
                volume = VALUES(volume),
                trade_count = VALUES(trade_count)
        """, (
            row['date'].date(),
            row['open'], row['high'], row['low'], row['close'],
            row['volume'], row['trade_count']
        ))

    conn.commit()
    cursor.close()
    conn.close()
    print("✅ twii_weekly 與 twii_monthly 寫入完成")

if __name__ == "__main__":
    generate_twii_ohlc()
