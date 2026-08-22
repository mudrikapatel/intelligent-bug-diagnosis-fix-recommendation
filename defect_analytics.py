import os

import pandas as pd
import streamlit as st
import plotly.express as px

# =========================================================
# CONFIGURATION
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

DATA_FILE = os.path.join(
    BASE_DIR,
    "submitted_bugs.csv"
)


# =========================================================
# SAVE ANALYSIS
# =========================================================

def save_bug_analysis(data):

    triage = data.get(
        "triage",
        {}
    )

    root = data.get(
        "root_cause",
        {}
    )

    log = data.get(
        "log_analysis",
        {}
    )

    remediation = data.get(
        "remediation",
        {}
    )

    row = {

        "date":
            pd.Timestamp.now(),

        "bug_id":
            data.get(
                "bug_id",
                "BUG-" +
                pd.Timestamp.now().strftime(
                    "%Y%m%d%H%M%S%f"
                )
            ),

        "severity":
            triage.get(
                "severity",
                log.get(
                    "severity",
                    "Unknown"
                )
            ),

        "priority":
            triage.get(
                "priority",
                "Unknown"
            ),

        "component":
            triage.get(
                "component",
                "Unknown"
            ),

        "category":
            triage.get(
                "category",
                "Unknown"
            ),

        "root_cause":
            root.get(
                "cause",
                log.get(
                    "root_cause",
                    "Unknown"
                )
            ),

        "root_cause_confidence":
            root.get(
                "confidence",
                0
            ),

        "duplicate_count":
            len(
                data.get(
                    "duplicates",
                    []
                )
            ),

        "recommendation_available":
            bool(
                remediation.get(
                    "recommended_fix",
                    []
                )
            )
    }

    new_df = pd.DataFrame(
        [row]
    )

    if os.path.exists(
        DATA_FILE
    ):

        try:

            old_df = pd.read_csv(
                DATA_FILE
            )

            df = pd.concat(
                [
                    old_df,
                    new_df
                ],
                ignore_index=True
            )

        except Exception:

            df = new_df

    else:

        df = new_df

    df.to_csv(
        DATA_FILE,
        index=False
    )


# =========================================================
# LOAD DATA
# =========================================================

def load_analytics_data():

    columns = [

        "date",
        "bug_id",
        "severity",
        "priority",
        "component",
        "category",
        "root_cause",
        "root_cause_confidence",
        "duplicate_count",
        "recommendation_available"
    ]

    if not os.path.exists(
        DATA_FILE
    ):

        return pd.DataFrame(
            columns=columns
        )

    try:

        df = pd.read_csv(
            DATA_FILE
        )

    except Exception:

        return pd.DataFrame(
            columns=columns
        )

    for column in columns:

        if column not in df.columns:

            df[column] = ""

    if "date" in df.columns:

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

    return df


# =========================================================
# ANALYTICS DASHBOARD
# =========================================================

def analytics_dashboard():

    st.title(
        "📊 Defect Pattern Analytics Dashboard"
    )

    df = load_analytics_data()

    if df.empty:

        st.info(
            "No submitted bugs available yet. "
            "Analyze bug reports from the Bug Analyzer page."
        )

        return

    # =====================================================
    # CLEAN DATA
    # =====================================================

    for column in [
        "severity",
        "priority",
        "component",
        "category",
        "root_cause"
    ]:

        df[column] = (
            df[column]
            .fillna("Unknown")
            .astype(str)
            .replace(
                "",
                "Unknown"
            )
        )

    # =====================================================
    # KPI
    # =====================================================

    total_bugs = len(df)

    high_severity = int(
        df["severity"]
        .str.lower()
        .isin(
            [
                "high",
                "critical",
                "blocker"
            ]
        )
        .sum()
    )

    components_count = (
        df["component"]
        .nunique()
    )

    root_cause_count = (
        df["root_cause"]
        .nunique()
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:

        st.metric(
            "🐞 Total Bugs",
            total_bugs
        )

    with c2:

        st.metric(
            "🔥 High/Critical",
            high_severity
        )

    with c3:

        st.metric(
            "🧩 Components",
            components_count
        )

    with c4:

        st.metric(
            "🧠 Root Cause Types",
            root_cause_count
        )

    st.divider()


    # =====================================================
    # SEVERITY + PRIORITY
    # =====================================================

    col1, col2 = st.columns(2)

    with col1:

        st.subheader(
            "🔥 Severity Distribution"
        )

        severity = (
            df["severity"]
            .value_counts()
        )

        st.bar_chart(
            severity
        )

    with col2:

        st.subheader(
            "⚡ Priority Distribution"
        )

        priority = (
            df["priority"]
            .value_counts()
        )

        st.bar_chart(
            priority
        )

    st.divider()


    # =====================================================
    # COMPONENT FREQUENCY
    # =====================================================

    st.subheader(
        "🧩 Frequently Affected Components"
    )

    components = (
        df["component"]
        .value_counts()
        .head(10)
    )

    st.bar_chart(
        components
    )

    st.divider()


    # =====================================================
    # ROOT CAUSES
    # =====================================================

    st.subheader(
        "🧠 Most Frequent Root Causes"
    )

    root_causes = (
        df["root_cause"]
        .value_counts()
        .head(10)
    )

    st.bar_chart(
        root_causes
    )

    st.divider()


    # =====================================================
    # CATEGORIES
    # =====================================================

    st.subheader(
        "🔁 Recurring Bug Categories"
    )

    categories = (
        df["category"]
        .value_counts()
        .head(10)
    )

    st.bar_chart(
        categories
    )

    st.divider()


    # =====================================================
    # RECURRING DEFECT PATTERNS
    # =====================================================

    st.subheader(
        "🔄 Recurring Defect Patterns"
    )

    pattern_df = (
        df[
            [
                "component",
                "category",
                "root_cause"
            ]
        ]
        .fillna("Unknown")
        .astype(str)
    )

    pattern_counts = (
        pattern_df
        .value_counts()
        .reset_index(
            name="Occurrences"
        )
    )

    if not pattern_counts.empty:

        st.dataframe(
            pattern_counts.head(15),
            use_container_width=True
        )

    else:

        st.info(
            "No recurring defect patterns found."
        )

    st.divider()


    # =========================================================
    # SYSTEMIC ISSUE TREND
    # =========================================================

    st.subheader("📈 Systemic Issue Trend")

    try:

        trend_df = df.copy()

        trend_df["date"] = pd.to_datetime(
            trend_df["date"],
            errors="coerce"
        )

        trend_df = trend_df[
            trend_df["date"].notna()
        ].copy()

        if trend_df.empty:

            st.warning(
                "⚠️ No valid dates available for Systemic Issue Trend."
            )

        else:

            trend_df["Month"] = (
                trend_df["date"]
                .dt.to_period("M")
                .dt.to_timestamp()
            )

            monthly = (
                trend_df
                .groupby("Month")
                .size()
                .reset_index(
                    name="Bug Count"
                )
            )

            fig = px.line(
                monthly,
                x="Month",
                y="Bug Count",
                markers=True,
                title="Monthly Defect Trend"
            )

            fig.update_traces(
                line=dict(
                    color="#6366F1",
                    width=4
                ),
                marker=dict(
                    size=10,
                    color="#4F46E5"
                )
            )

            fig.update_layout(
                height=450,

                paper_bgcolor="rgba(0,0,0,0)",

                plot_bgcolor="rgba(0,0,0,0)",

                margin=dict(
                    l=40,
                    r=30,
                    t=70,
                    b=50
                ),

                xaxis=dict(
                    title="Month",
                    showgrid=False
                ),

                yaxis=dict(
                    title="Number of Bugs",
                    rangemode="tozero",
                    showgrid=True,
                    gridcolor="rgba(128,128,128,0.2)"
                ),

                hovermode="x unified"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

    except Exception as e:

        st.error(
            f"❌ Systemic Trend Error: {e}"
        )


    st.divider()


    # =========================================================
    # DUPLICATE TREND
    # =========================================================

    st.subheader(
        "🔎 Duplicate Detection Trend"
    )

    duplicate_total = int(
        pd.to_numeric(
            df["duplicate_count"],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )

    recommendation_total = int(
        df["recommendation_available"]
        .astype(str)
        .str.lower()
        .isin(
            [
                "true",
                "1",
                "yes"
            ]
        )
        .sum()
    )

    d1, d2 = st.columns(2)

    with d1:

        st.metric(
            "Total Duplicate Matches",
            duplicate_total
        )

    with d2:

        st.metric(
            "Bugs With Recommendations",
            recommendation_total
        )

    st.divider()


    # =========================================================
    # RAW DATA
    # =========================================================

    with st.expander(
        "📋 View Submitted Bug Dataset"
    ):

        st.dataframe(
            df,
            use_container_width=True
        )
        )
