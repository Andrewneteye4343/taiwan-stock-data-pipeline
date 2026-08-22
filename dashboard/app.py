import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine

from dashboard.components.realtime import (
    get_refresh_options,
    load_realtime_quote,
    normalize_refresh_interval,
)

from src.services.fundamental_service import (
    get_fundamental_history,
)

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
refresh_options = get_refresh_options()

selected_refresh_label = st.selectbox(
    "Realtime Refresh",
    list(refresh_options.keys()),
    index=1,
)

refresh_interval = normalize_refresh_interval(
    refresh_options[selected_refresh_label]
)

realtime_quote = load_realtime_quote(
    selected_stock
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

st.subheader("Realtime Quote")

st.subheader("📊 Quarterly Financials")

fundamental_history = get_fundamental_history(
    selected_stock
)

if fundamental_history.empty:

    st.info(
        "目前沒有財務季報資料。"
    )

else:

    financial_display = fundamental_history.copy()

    financial_display["quarter"] = (
        financial_display["report_year"].astype(str)
        + " Q"
        + financial_display["report_quarter"].astype(str)
    )

    financial_display = financial_display[
        [
            "quarter",
            "eps",
            "eps_ytd",
            "bvps",
            "dps",
        ]
    ]

    financial_display.columns = [
        "季度",
        "EPS",
        "累計 EPS",
        "BVPS",
        "DPS",
    ]

    st.dataframe(
        financial_display,
        use_container_width=True,
        hide_index=True,
    )

st.subheader("📈 EPS Trend")

eps_chart_df = fundamental_history.copy()

eps_chart_df["quarter"] = (
    eps_chart_df["report_year"].astype(str)
    + " Q"
    + eps_chart_df["report_quarter"].astype(str)
)

eps_chart_df = eps_chart_df[
    [
        "quarter",
        "eps",
    ]
].set_index("quarter")

st.line_chart(
    eps_chart_df["eps"]
)

if realtime_quote is None:

    st.warning(
        "目前無法取得即時行情資料。"
    )

else:
    realtime_col1, realtime_col2, realtime_col3, realtime_col4 = (
        st.columns(4)
    )

    last_price = realtime_quote["last_price"]

    if last_price is None:
        realtime_col1.metric(
            "即時價格",
            "暫無成交",
        )
    else:
        realtime_col1.metric(
            "即時價格",
            f"{last_price:,.2f}",
        )

    change = realtime_quote["change"]
change_pct = realtime_quote["change_pct"]

if change is None or change_pct is None:
    realtime_col2.metric(
        "漲跌",
        "暫無資料",
    )
else:
    if change > 0:
        change_color = "#d60000"
    elif change < 0:
        change_color = "#008000"
    else:
        change_color = "#666666"

    realtime_col2.markdown(
        f"""
        <div>
            <div style="font-size: 14px;">
                漲跌
            </div>
            <div style="
                font-size: 28px;
                font-weight: 600;
                color: {change_color};
            ">
                {change:,.2f}
            </div>
            <div style="
                font-size: 14px;
                color: {change_color};
            ">
                {change_pct:.2f}%
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    volume = realtime_quote["volume"]

    realtime_col3.metric(
        "成交量",
        f"{volume:,}" if volume is not None else "暫無資料",
    )

    realtime_col4.metric(
        "資料時間",
        realtime_quote["trade_time"],
    )

    open_price = realtime_quote["open"]
    high = realtime_quote["high"]
    low = realtime_quote["low"]

    st.caption(
        f"開盤 {open_price:,.2f}　"
        f"最高 {high:,.2f}　"
        f"最低 {low:,.2f}"
    )


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