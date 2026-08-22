import os
import altair as alt
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from sqlalchemy import create_engine

from dashboard.components.realtime import (
    get_refresh_options,
    load_realtime_quote,
    normalize_refresh_interval,
)

from src.services.fundamental_service import (
    calculate_latest_fundamentals,
    get_fundamental_history,
)


# ============================================================
# Database
# ============================================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured")

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
)


# ============================================================
# Streamlit configuration
# ============================================================

st.set_page_config(
    page_title="Taiwan Stock Dashboard",
    page_icon="📈",
    layout="wide",
)

st.title("📈 Taiwan Stock Market Dashboard")


# ============================================================
# Stock list
# ============================================================

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


if not stock_options:
    st.error("目前沒有股票資料。")
    st.stop()


# ============================================================
# Stock selector
# ============================================================

selected_stock = st.selectbox(
    "Select Stock",
    [
        item["symbol"]
        for item in stock_options
    ],
    format_func=lambda symbol: next(
        (
            item["name"]
            for item in stock_options
            if item["symbol"] == symbol
        ),
        symbol,
    ),
)


selected_stock_name = next(
    (
        item["name"]
        for item in stock_options
        if item["symbol"] == selected_stock
    ),
    selected_stock,
)


# ============================================================
# Stock title
# ============================================================

st.header(
    f"{selected_stock} {selected_stock_name}"
)


# ============================================================
# Realtime refresh setting
# ============================================================

refresh_options = get_refresh_options()

selected_refresh_label = st.selectbox(
    "Realtime Refresh",
    list(refresh_options.keys()),
    index=1,
)

refresh_interval = normalize_refresh_interval(
    refresh_options[selected_refresh_label]
)

# Keep refresh_interval available for realtime component.
_ = refresh_interval


# ============================================================
# Historical price data
# ============================================================

price_query = """
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
    price_query,
    engine,
    params={
        "symbol": selected_stock,
    },
)


if df.empty:
    st.warning(
        f"{selected_stock} {selected_stock_name} "
        "目前沒有歷史行情資料。"
    )
    st.stop()


# Ensure trade_date is datetime.
df["trade_date"] = pd.to_datetime(
    df["trade_date"],
    errors="coerce",
)


# Remove rows with invalid trade dates.
df = df.dropna(
    subset=["trade_date"]
).copy()


if df.empty:
    st.warning(
        f"{selected_stock} {selected_stock_name} "
        "目前沒有有效的交易日期資料。"
    )
    st.stop()


# Sort historical data by trade date.
df = df.sort_values(
    "trade_date"
).reset_index(
    drop=True
)


# Convert numerical columns safely.
numeric_columns = [
    "open",
    "high",
    "low",
    "close",
    "volume",
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce",
    )


# ============================================================
# Latest historical price
# ============================================================

latest = df.iloc[-1]

latest_trade_date = latest["trade_date"].strftime(
    "%Y-%m-%d"
)

st.caption(
    f"最新交易日：{latest_trade_date}"
)


# ============================================================
# 1. Realtime Quote
# ============================================================

st.subheader("2️⃣ 即時行情")

realtime_quote = load_realtime_quote(
    selected_stock
)

if realtime_quote is None:

    st.info(
        "目前無法取得即時行情資料。"
    )

else:

    realtime_col1, realtime_col2, realtime_col3, realtime_col4 = (
        st.columns(4)
    )

    # --------------------------------------------------------
    # Current price
    # --------------------------------------------------------

    last_price = realtime_quote.get(
        "last_price"
    )

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

    # --------------------------------------------------------
    # Price change
    # --------------------------------------------------------

    change = realtime_quote.get(
        "change"
    )

    change_pct = realtime_quote.get(
        "change_pct"
    )

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

    # --------------------------------------------------------
    # Volume
    # --------------------------------------------------------

    volume = realtime_quote.get(
        "volume"
    )

    realtime_col3.metric(
        "成交量",
        (
            f"{volume:,}"
            if volume is not None
            else "暫無資料"
        ),
    )

    # --------------------------------------------------------
    # Realtime data time
    # --------------------------------------------------------

    trade_time = realtime_quote.get(
        "trade_time"
    )

    realtime_col4.metric(
        "資料時間",
        (
            trade_time
            if trade_time is not None
            else "暫無資料"
        ),
    )


# ============================================================
# 2. Latest historical price
# ============================================================

st.subheader("3️⃣ 最新歷史行情")

price_col1, price_col2, price_col3, price_col4 = (
    st.columns(4)
)


price_col1.metric(
    "收盤價",
    f"{latest['close']:,.2f}",
)


price_col2.metric(
    "開盤價",
    f"{latest['open']:,.2f}",
)


price_col3.metric(
    "最高價",
    f"{latest['high']:,.2f}",
)


price_col4.metric(
    "最低價",
    f"{latest['low']:,.2f}",
)


st.caption(
    f"資料日期：{latest_trade_date}"
)


# ============================================================
# 3. Price chart
# ============================================================

st.subheader("4️⃣ 股價圖")

price_chart_df = df.copy()

price_chart_df["trade_date"] = pd.to_datetime(
    price_chart_df["trade_date"],
    errors="coerce",
)

price_chart_df["close"] = pd.to_numeric(
    price_chart_df["close"],
    errors="coerce",
)

price_chart_df = (
    price_chart_df
    .dropna(
        subset=[
            "trade_date",
            "close",
        ]
    )
    .sort_values("trade_date")
)

price_chart = (
    alt.Chart(price_chart_df)
    .mark_line()
    .encode(
        x=alt.X(
            "trade_date:T",
            title="交易日期",
        ),
        y=alt.Y(
            "close:Q",
            title="股價（元）",
            axis=alt.Axis(
                titlePadding=10,
            ),
        ),
        tooltip=[
            alt.Tooltip(
                "trade_date:T",
                title="交易日期",
                format="%Y-%m-%d",
            ),
            alt.Tooltip(
                "close:Q",
                title="收盤價（元）",
                format=",.2f",
            ),
        ],
    )
    .properties(
        height=400,
    )
)

st.altair_chart(
    price_chart,
    use_container_width=True,
)


# ============================================================
# 4. Trading volume chart
# ============================================================

st.subheader("5️⃣ 成交量圖")

volume_chart_df = df[
    [
        "trade_date",
        "volume",
    ]
].copy()

volume_chart_df["volume"] = pd.to_numeric(
    volume_chart_df["volume"],
    errors="coerce",
)

# Compare volume with the previous trading day.
volume_chart_df["previous_volume"] = (
    volume_chart_df["volume"].shift(1)
)


def get_volume_color(row):
    """
    Determine volume bar color.

    Taiwan stock market style:
    - Red   : volume increased
    - Green : volume decreased
    - Gray  : first record / no comparison
    """

    if pd.isna(row["previous_volume"]):
        return "#808080"

    if row["volume"] > row["previous_volume"]:
        return "#d60000"

    if row["volume"] < row["previous_volume"]:
        return "#008000"

    return "#808080"


volume_chart_df["volume_color"] = (
    volume_chart_df.apply(
        get_volume_color,
        axis=1,
    )
)


fig = go.Figure()

fig.add_trace(
    go.Bar(
        x=volume_chart_df["trade_date"],
        y=volume_chart_df["volume"],
        marker=dict(
            color=volume_chart_df["volume_color"],
        ),

        # Narrower bars
        width=100,

        hovertemplate=(
            "日期：%{x|%Y-%m-%d}<br>"
            "成交量：%{y:,}<extra></extra>"
        ),
    )
)


fig.update_layout(
    height=350,

    margin=dict(
        l=20,
        r=20,
        t=20,
        b=20,
    ),

    xaxis=dict(
        title=None,
        showgrid=False,
    ),

    yaxis=dict(
        title="成交量",
        showgrid=True,
    ),

    # Increase spacing between bars.
    bargap=0.01,

    showlegend=False,
)


st.plotly_chart(
    fig,
    use_container_width=True,
)


# ============================================================
# 5. Quarterly financial data
# ============================================================

st.subheader("6️⃣ 季度財務資料")

fundamental_history = get_fundamental_history(
    selected_stock
)


if fundamental_history.empty:

    st.info(
        "目前沒有財務季報資料。"
    )

else:

    financial_display = (
        fundamental_history.copy()
    )


    financial_display["quarter"] = (
        financial_display["report_year"].astype(str)
        + " Q"
        + financial_display["report_quarter"].astype(str)
    )


    financial_columns = [
        "quarter",
        "eps",
        "eps_ytd",
        "bvps",
        "dps",
    ]


    available_columns = [
        column
        for column in financial_columns
        if column in financial_display.columns
    ]


    financial_display = financial_display[
        available_columns
    ]


    column_names = {
        "quarter": "季度",
        "eps": "EPS",
        "eps_ytd": "累計 EPS",
        "bvps": "BVPS",
        "dps": "DPS",
    }


    financial_display = financial_display.rename(
        columns=column_names
    )


    st.dataframe(
        financial_display,
        use_container_width=True,
        hide_index=True,
    )


    latest_fundamental = (
        fundamental_history.iloc[0]
    )


    latest_report_period = (
        f"{latest_fundamental['report_year']} 年 "
        f"Q{latest_fundamental['report_quarter']}"
    )


    st.caption(
        f"最新財報期間：{latest_report_period}"
    )


# ============================================================
# 6. EPS trend
# ============================================================

st.subheader("7️⃣ EPS Trend")

if fundamental_history.empty:

    st.info(
        "目前沒有 EPS 資料。"
    )

else:

    eps_chart_df = fundamental_history.copy()

    eps_chart_df["quarter"] = (
        eps_chart_df["report_year"].astype(str)
        + " Q"
        + eps_chart_df["report_quarter"].astype(str)
    )

    eps_chart_df["eps"] = pd.to_numeric(
        eps_chart_df["eps"],
        errors="coerce",
    )

    eps_chart_df = (
        eps_chart_df[
            [
                "quarter",
                "eps",
            ]
        ]
        .dropna(subset=["eps"])
        .sort_values(
            [
                "quarter",
            ]
        )
        .reset_index(drop=True)
    )

    if eps_chart_df.empty:

        st.info(
            "目前沒有可用的 EPS 資料。"
        )

    else:

        eps_chart = (
            alt.Chart(eps_chart_df)
            .mark_line(
                point=True,
            )
            .encode(
                x=alt.X(
                    "quarter:N",
                    title="財報季度",
                    sort=eps_chart_df[
                        "quarter"
                    ].tolist(),
                ),
                y=alt.Y(
                    "eps:Q",
                    title="EPS（元）",
                ),
                tooltip=[
                    alt.Tooltip(
                        "quarter:N",
                        title="季度",
                    ),
                    alt.Tooltip(
                        "eps:Q",
                        title="EPS（元）",
                        format=",.2f",
                    ),
                ],
            )
            .properties(
                height=350,
            )
        )

        st.altair_chart(
            eps_chart,
            use_container_width=True,
        )


# ============================================================
# 7. Fundamental indicators
# ============================================================

st.subheader("📊 估值與獲利指標")


latest_fundamentals = (
    calculate_latest_fundamentals(
        selected_stock
    )
)


if latest_fundamentals.empty:

    st.info(
        "目前沒有足夠的基本面資料可以計算指標。"
    )

else:

    latest_indicator = (
        latest_fundamentals.iloc[0]
    )


    # --------------------------------------------------------
    # Convert numeric values safely
    # --------------------------------------------------------

    def numeric_value(value):

        try:

            if pd.isna(value):
                return None

            return float(value)

        except (
            TypeError,
            ValueError,
        ):

            return None


    gross_margin = numeric_value(
        latest_indicator.get(
            "gross_margin"
        )
    )


    operating_margin = numeric_value(
        latest_indicator.get(
            "operating_margin"
        )
    )


    net_margin = numeric_value(
        latest_indicator.get(
            "net_margin"
        )
    )


    pe = numeric_value(
        latest_indicator.get(
            "pe"
        )
    )


    pb = numeric_value(
        latest_indicator.get(
            "pb"
        )
    )


    dividend_yield = numeric_value(
        latest_indicator.get(
            "dividend_yield"
        )
    )


    # --------------------------------------------------------
    # Row 1: profitability
    # --------------------------------------------------------

    margin_col1, margin_col2, margin_col3 = (
        st.columns(3)
    )


    margin_col1.metric(
        "8️⃣ 毛利率",
        (
            f"{gross_margin:.2f}%"
            if gross_margin is not None
            else "N/A"
        ),
    )


    margin_col2.metric(
        "9️⃣ 營業利益率",
        (
            f"{operating_margin:.2f}%"
            if operating_margin is not None
            else "N/A"
        ),
    )


    margin_col3.metric(
        "🔟 淨利率",
        (
            f"{net_margin:.2f}%"
            if net_margin is not None
            else "N/A"
        ),
    )


    # --------------------------------------------------------
    # Row 2: valuation
    # --------------------------------------------------------

    valuation_col1, valuation_col2, valuation_col3 = (
        st.columns(3)
    )


    valuation_col1.metric(
        "1️⃣1️⃣ PE",
        (
            f"{pe:.2f}"
            if pe is not None
            else "N/A"
        ),
    )


    valuation_col2.metric(
        "1️⃣2️⃣ PB",
        (
            f"{pb:.2f}"
            if pb is not None
            else "N/A"
        ),
    )


    valuation_col3.metric(
        "1️⃣3️⃣ 殖利率",
        (
            f"{dividend_yield:.2f}%"
            if dividend_yield is not None
            else "N/A"
        ),
    )


    latest_indicator_period = (
        f"{latest_indicator['report_year']} 年 "
        f"Q{latest_indicator['report_quarter']}"
    )


    st.caption(
        f"基本面資料期間：{latest_indicator_period}"
    )


# ============================================================
# Raw data
# ============================================================

with st.expander("Raw Data"):

    raw_display = df.copy()


    raw_display["trade_date"] = (
        raw_display["trade_date"]
        .dt.strftime("%Y-%m-%d")
    )


    st.dataframe(
        raw_display.tail(30),
        use_container_width=True,
        hide_index=True,
    )