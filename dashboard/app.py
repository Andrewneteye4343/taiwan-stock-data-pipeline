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


stocks = load_stock_list()


selected_stock = st.selectbox(
    "Select Stock",
    stocks["symbol"].tolist(),
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