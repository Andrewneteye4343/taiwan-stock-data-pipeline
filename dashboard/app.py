import os

import pandas as pd
import streamlit as st

from sqlalchemy import create_engine


DATABASE_URL = os.getenv(
    "DATABASE_URL"
)

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


st.set_page_config(
    page_title="Taiwan Stock Dashboard",
    page_icon="📈",
    layout="wide",
)


st.title(
    "📈 Taiwan Stock Market Dashboard"
)


@st.cache_data(ttl=300)
def load_stock_list():

    query = """
        SELECT
            symbol,
            name
        FROM stock_master
        ORDER BY symbol
    """

    return pd.read_sql(
        query,
        engine,
    )


def get_stock_options():
    stocks = load_stock_list()

    return stocks[
        ["symbol", "name"]
    ].to_dict(
        orient="records"
    )

stock_options = get_stock_options()


selected_stock = st.selectbox(
    "Select Stock",
    [
        item["symbol"]
        for item in stock_options
    ],
)

query = """
    SELECT
        sm.symbol,
        sm.name,
        dp.trade_date,
        dp.open,
        dp.high,
        dp.low,
        dp.close,
        dp.volume
    FROM daily_price dp
    JOIN stock_master sm
        ON dp.stock_id = sm.stock_id
    WHERE sm.symbol = %(symbol)s
    ORDER BY dp.trade_date
"""


df = pd.read_sql(
    query,
    engine,
    params={
        "symbol": selected_stock
    },
)


if df.empty:

    st.warning(
        "No stock data available."
    )

    st.stop()


latest = df.iloc[-1]


col1, col2, col3, col4 = st.columns(4)


col1.metric(
    "Close",
    f"{latest['close']:,.2f}",
)


col2.metric(
    "Open",
    f"{latest['open']:,.2f}",
)


col3.metric(
    "High",
    f"{latest['high']:,.2f}",
)


col4.metric(
    "Low",
    f"{latest['low']:,.2f}",
)


st.subheader(
    f"{selected_stock} Price"
)


chart_df = df.set_index(
    "trade_date"
)


st.line_chart(
    chart_df["close"]
)


st.subheader(
    "Trading Volume"
)


st.bar_chart(
    chart_df["volume"]
)


st.subheader(
    "Raw Data"
)


st.dataframe(
    df.tail(30),
    use_container_width=True,
)

def calculate_price_change(
    previous_close,
    current_close,
):
    if previous_close == 0:
        return {
            "change": None,
            "change_pct": None,
        }

    change = current_close - previous_close

    change_pct = (
        change
        / previous_close
        * 100
    )

    return {
        "change": change,
        "change_pct": change_pct,
    }

def get_latest_price_summary(df):
    if len(df) < 2:
        return None

    df = df.sort_values(
        "trade_date"
    ).reset_index(
        drop=True
    )

    previous = df.iloc[-2]
    latest = df.iloc[-1]

    price_change = calculate_price_change(
        previous["close"],
        latest["close"],
    )

    return {
        "trade_date": latest["trade_date"],
        "open": latest["open"],
        "high": latest["high"],
        "low": latest["low"],
        "close": latest["close"],
        "volume": latest["volume"],
        "change": price_change["change"],
        "change_pct": price_change["change_pct"],
    }