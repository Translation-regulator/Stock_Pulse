import pandas as pd
from datetime import timedelta
from sqlalchemy import text, Table, MetaData
from sqlalchemy.dialects.mysql import insert as mysql_insert
from crawler_utils.db import engine

def generate_twii_ohlc():
    with engine.connect() as conn:
        df = pd.read_sql("""
            SELECT date, open, high, low, close, volume, trade_count, change_point, amount
            FROM twii_daily
        """, conn)

    df['date'] = pd.to_datetime(df['date'])
    df.sort_values('date', inplace=True)

    # ========== 週線處理：以週五為週期結束 ========== #
    weekly_rows = []
    for _, group in df.groupby(pd.Grouper(key='date', freq='W-FRI')):
        if group.empty:
            continue
        weekly_rows.append({
            'date': group['date'].max().date(),
            'open': float(group.iloc[0]['open']),
            'high': float(group['high'].max()),
            'low': float(group['low'].min()),
            'close': float(group.iloc[-1]['close']),
            'volume': int(group['volume'].sum()),
            'trade_count': int(group['trade_count'].sum()),
            'amount': int(group['amount'].sum()),
            'change_point': float(group.iloc[-1]['change_point'])
        })

    # ========== 月線處理 ========== #
    df['month_id'] = df['date'].dt.to_period("M")
    monthly_rows = []
    for _, group in df.groupby('month_id'):
        monthly_rows.append({
            'date': group['date'].max().date(),
            'open': float(group.iloc[0]['open']),
            'high': float(group['high'].max()),
            'low': float(group['low'].min()),
            'close': float(group.iloc[-1]['close']),
            'volume': int(group['volume'].sum()),
            'trade_count': int(group['trade_count'].sum()),
            'amount': int(group['amount'].sum()),
            'change_point': float(group.iloc[-1]['change_point'])
        })

    metadata = MetaData()
    metadata.reflect(bind=engine)
    twii_weekly = Table("twii_weekly", metadata, autoload_with=engine)
    twii_monthly = Table("twii_monthly", metadata, autoload_with=engine)

    with engine.begin() as conn:
        if weekly_rows:
            min_week = min(row['date'] for row in weekly_rows)
            max_week = max(row['date'] for row in weekly_rows)
            conn.execute(text("""
                DELETE FROM twii_weekly WHERE date BETWEEN :min_date AND :max_date
            """), {"min_date": min_week, "max_date": max_week})

            for row in weekly_rows:
                stmt = mysql_insert(twii_weekly).values(**row)
                stmt = stmt.on_duplicate_key_update(**{k: stmt.inserted[k] for k in row if k != 'date'})
                conn.execute(stmt)

        if monthly_rows:
            min_month = min(row['date'] for row in monthly_rows)
            max_month = max(row['date'] for row in monthly_rows)
            conn.execute(text("""
                DELETE FROM twii_monthly WHERE date BETWEEN :min_date AND :max_date
            """), {"min_date": min_month, "max_date": max_month})

            for row in monthly_rows:
                stmt = mysql_insert(twii_monthly).values(**row)
                stmt = stmt.on_duplicate_key_update(**{k: stmt.inserted[k] for k in row if k != 'date'})
                conn.execute(stmt)

    print("✅ twii_weekly 與 twii_monthly 資料寫入完成")

if __name__ == "__main__":
    generate_twii_ohlc()
