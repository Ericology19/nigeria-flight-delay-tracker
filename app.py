"""Nigeria Domestic Flight Delay Tracker (Streamlit dashboard).

Run locally:  streamlit run app.py
"""
import pandas as pd
import plotly.express as px
import streamlit as st

from data_utils import (
    ALL, BUCKET_COLUMNS, BUCKET_LABELS,
    airline_periods, airline_ranking, august_buckets, key_findings, load_data, network_monthly,
)

PRIMARY = "#1D4ED8"
ACCENT = "#F97316"

st.set_page_config(page_title="Nigeria Domestic Flight Delay Tracker", page_icon="✈️", layout="wide")


def show(fig):
    """Display a Plotly chart at full width (works across Streamlit versions)."""
    fig.update_layout(template="plotly_white", margin=dict(l=10, r=10, t=30, b=10), font=dict(size=14))
    try:
        st.plotly_chart(fig, width="stretch")
    except TypeError:
        st.plotly_chart(fig, use_container_width=True)


def highlight_max(values):
    """Bar colours: accent for the highest value, primary for the rest."""
    top = max(values)
    return [ACCENT if v == top else PRIMARY for v in values]


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_data()


df = get_data()

st.title("✈️ Nigeria Domestic Flight Delay Tracker")
st.markdown(
    "How often do Nigerian domestic flights run late? An open dashboard built from the Nigerian Civil Aviation "
    "Authority's (NCAA) published flight-disruption summaries."
)

tab_overview, tab_airlines, tab_august, tab_notes = st.tabs(
    ["Overview", "Airlines", "August 2026 breakdown", "Data and limitations"]
)

# ---------------------------------------------------------------- Overview
with tab_overview:
    monthly = network_monthly(df)
    latest = monthly.iloc[-1]

    with st.container(border=True):
        st.markdown("**Key findings**")
        for line in key_findings(df):
            st.markdown(f"- {line}")

    st.subheader(f"Latest month in the data: {latest['label']}")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Flights operated", f"{int(latest['total_flights']):,}")
    c2.metric("Delayed over 1 hour", f"{latest['rate_over_1h']:.1%}", f"{int(latest['delayed_over_1h']):,} flights", delta_color="off")
    if pd.notna(latest["rate_over_15min"]):
        c3.metric("Delayed over 15 minutes", f"{latest['rate_over_15min']:.1%}", f"{int(latest['delayed_over_15min']):,} flights", delta_color="off")
    c4.metric("Cancelled", f"{int(latest['cancelled_flights'])}", f"{latest['cancel_rate']:.2%} of flights", delta_color="off")

    st.subheader("Share of flights delayed over 1 hour, by month")
    fig = px.bar(
        monthly, x="label", y="rate_over_1h", text="rate_over_1h",
        labels={"label": "Month", "rate_over_1h": "Flights delayed over 1 hour"},
    )
    fig.update_traces(texttemplate="%{y:.1%}", textposition="outside",
                      marker_color=highlight_max(monthly["rate_over_1h"].tolist()))
    fig.update_yaxes(tickformat=".0%", rangemode="tozero")
    fig.update_xaxes(type="category")
    show(fig)
    st.caption(
        "The highest month is highlighted. Months shown are those with published NCAA data in this dataset "
        "(July 2026 is not included). The one-hour measure is used because the NCAA's quarterly summaries only "
        "count delays above one hour."
    )

# ---------------------------------------------------------------- Airlines
with tab_airlines:
    st.subheader("Airline comparison")
    periods = airline_periods(df)
    left, mid, right = st.columns([2, 2, 2])
    label = left.selectbox("Period", periods, index=len(periods) - 1)
    measure = mid.radio("Measure", ["Delayed over 1 hour", "Delayed over 15 minutes (August only)"])
    min_flights = right.slider("Minimum flights operated", 0, 500, 100, step=50,
                               help="Airlines with few flights can show extreme rates by chance.")
    rate_col = "rate_over_1h" if measure.startswith("Delayed over 1 hour") else "rate_over_15min"
    count_col = "delayed_over_1h" if rate_col == "rate_over_1h" else "delayed_over_15min"

    ranking = airline_ranking(df, label, rate_col, min_flights)
    if ranking.empty:
        st.info("No data for this combination. The 15-minute measure is only reported for August 2026.")
    else:
        ordered = ranking.sort_values(rate_col)
        fig = px.bar(
            ordered, x=rate_col, y="airline", orientation="h", text=rate_col,
            hover_data={"total_flights": True, count_col: True},
            labels={rate_col: "Share of flights delayed", "airline": ""},
        )
        fig.update_traces(texttemplate="%{x:.1%}", textposition="outside",
                          marker_color=highlight_max(ordered[rate_col].tolist()))
        fig.update_xaxes(tickformat=".0%", rangemode="tozero")
        fig.update_layout(height=max(350, 40 * len(ranking)))
        show(fig)

        with st.expander("Do bigger airlines run later? Flights operated vs delay rate"):
            fig2 = px.scatter(
                ranking, x="total_flights", y=rate_col, size="total_flights", text="airline",
                labels={"total_flights": "Flights operated", rate_col: "Share of flights delayed"},
            )
            fig2.update_traces(textposition="top center", marker=dict(color=PRIMARY, opacity=0.7))
            fig2.update_yaxes(tickformat=".0%", rangemode="tozero")
            show(fig2)

        table = ranking[["airline", "total_flights", count_col, rate_col, "cancelled_flights"]].rename(columns={
            "airline": "Airline", "total_flights": "Flights", count_col: "Delayed flights",
            rate_col: "Delay rate", "cancelled_flights": "Cancelled",
        })
        table["Delay rate"] = table["Delay rate"].map(lambda v: f"{v:.1%}")
        st.dataframe(table, hide_index=True)
    st.caption(
        "Airlines have publicly disputed some NCAA figures. Rates here reflect the regulator's published data, "
        "not an independent audit."
    )

# ---------------------------------------------------------------- August breakdown
with tab_august:
    st.subheader("How long were August 2026 delays?")
    buckets = august_buckets(df)
    network = df[(df["airline"] == ALL) & df[BUCKET_COLUMNS].notna().any(axis=1)]
    if buckets.empty or network.empty:
        st.info("No delay-length data available.")
    else:
        net = network.iloc[0]
        overall = pd.DataFrame({
            "Delay length": [BUCKET_LABELS[c] for c in BUCKET_COLUMNS],
            "Flights": [net[c] for c in BUCKET_COLUMNS],
        })
        overall["Share of delayed flights"] = overall["Flights"] / overall["Flights"].sum()
        fig = px.bar(overall, x="Delay length", y="Flights", text="Share of delayed flights")
        fig.update_traces(texttemplate="%{text:.0%}", textposition="outside", marker_color=PRIMARY)
        show(fig)

        st.subheader("By airline")
        long = buckets.melt(id_vars=["airline", "delayed_over_15min"], value_vars=BUCKET_COLUMNS,
                            var_name="bucket", value_name="flights")
        long["Delay length"] = long["bucket"].map(BUCKET_LABELS)
        long["flights"] = long["flights"].fillna(0)
        order = buckets.sort_values("delayed_over_15min")["airline"].tolist()
        fig = px.bar(long, x="flights", y="airline", color="Delay length", orientation="h",
                     category_orders={"airline": order, "Delay length": list(BUCKET_LABELS.values())},
                     color_discrete_sequence=["#93C5FD", "#3B82F6", "#1D4ED8", ACCENT],
                     labels={"flights": "Delayed flights", "airline": ""})
        fig.update_layout(height=max(400, 35 * len(order)))
        show(fig)
    st.caption("Source: NCAA Summary of Domestic Airline Flight Disruption Operations, August 2026.")

# ---------------------------------------------------------------- Data and limitations
with tab_notes:
    st.subheader("Definitions")
    st.markdown(
        """
- **Delayed over 1 hour:** the measure used in the NCAA quarterly executive summaries (Q1 and Q2 2026). For August it is the sum of the 1 to 2 hour, 2 to 3 hour and 3 hour-plus buckets, so months and quarters can be compared.
- **Delayed over 15 minutes:** the measure in the NCAA August 2026 monthly summary. It is **not** comparable with the quarterly figures.
- **Cancelled:** flights recorded as cancelled by the NCAA.
"""
    )
    st.subheader("Limitations")
    st.markdown(
        """
- The NCAA publishes airline-level totals, not flight-by-flight records.
- Airlines have publicly disputed some NCAA figures.
- Some source tables are inconsistent. Where the document shows which figure reconciles, that figure is used and flagged below.
- The August 2026 figures were entered from an image of the NCAA table.
- Not every month is covered (July 2026 is missing) and Q3 2026 is not yet included.
"""
    )
    flagged = df[df["notes"] != ""][["period", "period_type", "airline", "notes"]]
    st.subheader(f"Rows with notes ({len(flagged)})")
    st.dataframe(flagged, hide_index=True)
    st.download_button(
        "Download the dataset (CSV)",
        df.drop(columns=["label", "rate_over_1h", "rate_over_15min", "cancel_rate"]).to_csv(index=False),
        file_name="ncaa_disruptions.csv", mime="text/csv",
    )

st.divider()
st.caption(
    "Built by Eric Allagoa. Data: Nigerian Civil Aviation Authority (NCAA) published summaries. "
    "Independent project, not affiliated with the NCAA or any airline."
)
