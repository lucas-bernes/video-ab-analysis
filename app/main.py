"""
Streamlit app for A/B Creative Analytics Prototype.

Main dashboard for exploring A/B experiment data, comparisons, and insights.
"""

import streamlit as st
from pathlib import Path

from app.services import (
    normalize_from_file,
    compare_experiments,
    generate_insight,
)
from app.config import DEFAULT_KPI, AVAILABLE_KPIS


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="A/B Creative Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS for better styling
st.markdown("""
<style>
    .metric-card {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #f0f2f6;
        margin: 0.5rem 0;
    }
    .winner-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
        font-size: 0.9rem;
    }
    .winner-a {
        background-color: #90EE90;
        color: #1f1f1f;
    }
    .winner-b {
        background-color: #87CEEB;
        color: #1f1f1f;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================================
# Helper Functions
# ============================================================================

@st.cache_resource
def load_data(file_path: str):
    """Load and normalize data from file."""
    return normalize_from_file(file_path)


def display_dataframe_section(title: str, df, height: int = 300):
    """Display a DataFrame in an expandable section."""
    with st.expander(f"📋 {title}", expanded=False):
        st.dataframe(df, height=height, use_container_width=True)


def render_metric_comparison_card(comparison):
    """Render a single metric comparison in a card format."""
    metric = comparison.metric_comparisons

    cols = st.columns(3)

    # Metric 1: CTR
    with cols[0]:
        if "ctr" in metric:
            ctr_comp = metric["ctr"]
            st.metric(
                label="CTR",
                value=f"{ctr_comp.variant_b_value:.2%}",
                delta=f"{ctr_comp.lift_percent:+.1f}%",
                delta_color="normal"
            )

    # Metric 2: Conversion Rate
    with cols[1]:
        if "conversion_rate" in metric:
            conv_comp = metric["conversion_rate"]
            st.metric(
                label="Conversion Rate",
                value=f"{conv_comp.variant_b_value:.2%}",
                delta=f"{conv_comp.lift_percent:+.1f}%",
                delta_color="normal"
            )

    # Metric 3: ROAS
    with cols[2]:
        if "roas" in metric:
            roas_comp = metric["roas"]
            st.metric(
                label="ROAS",
                value=f"{roas_comp.variant_b_value:.2f}x",
                delta=f"{roas_comp.lift_percent:+.1f}%",
                delta_color="normal"
            )


def render_experiment_comparison(comparison, primary_kpi: str):
    """Render A/B comparison for one experiment."""
    with st.container():
        # Header with winner badge
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(f"🧪 {comparison.experiment_id}")
            st.write(
                f"**Campaign:** {comparison.experiment_name} | **Platform:** {comparison.platform}")

        with col2:
            if comparison.winner_variant:
                winner_class = "winner-a" if comparison.winner_variant == "A" else "winner-b"
                st.markdown(
                    f"<div class='winner-badge {winner_class}'>Winner: Variant {comparison.winner_variant}</div>",
                    unsafe_allow_html=True
                )

        # Primary KPI highlight
        st.markdown("---")
        st.write(f"**Primary KPI ({primary_kpi.upper()}):**")

        metric_cols = st.columns(3)
        with metric_cols[0]:
            st.metric(
                label="Variant A",
                value=f"{comparison.primary_kpi_value_a:.4g}",
            )
        with metric_cols[1]:
            st.metric(
                label="Variant B",
                value=f"{comparison.primary_kpi_value_b:.4g}",
            )
        with metric_cols[2]:
            st.metric(
                label="Lift",
                value=f"{comparison.primary_kpi_lift_percent:+.1f}%",
                delta_color="normal"
            )

        # Secondary metrics
        st.write("**Secondary Metrics:**")
        render_metric_comparison_card(comparison)

        # Metadata differences
        if comparison.metadata_differences:
            st.write("**Creative Differences:**")
            for diff in comparison.metadata_differences:
                st.write(f"• {diff}")

        # Recommendation
        if comparison.recommendation:
            st.info(f"💡 **Recommendation:** {comparison.recommendation}")

        st.markdown("---")


def render_insight_section(insight):
    """Render generated insight for one experiment."""
    with st.container():
        # Headline
        st.subheader(f"💭 {insight.experiment_id}")
        st.write(f"**Confidence:** {insight.confidence}")

        # Main narrative
        st.markdown(f"### {insight.headline}")
        st.write(insight.summary)

        # Key findings
        if insight.findings:
            st.write("**Key Findings:**")
            for finding in insight.findings:
                st.write(f"• {finding}")

        st.markdown("---")


# ============================================================================
# Main App
# ============================================================================

def main():
    """Main Streamlit app."""

    # Title and description
    st.title("📊 A/B Creative Analytics Prototype")
    st.write(
        """
        Compare video ad creatives using API data. This prototype normalizes A/B experiment data,
        compares variant performance across KPIs, and generates business-facing insights.
        
        **Note:** This MVP uses mocked API data and does not process raw video files.
        """
    )

    # Sidebar: Configuration
    st.sidebar.title("⚙️ Configuration")
    primary_kpi = st.sidebar.selectbox(
        "Select Primary KPI",
        AVAILABLE_KPIS,
        index=AVAILABLE_KPIS.index(DEFAULT_KPI),
        help="KPI used to determine the winning variant"
    )

    # Data loading
    st.sidebar.markdown("---")
    st.sidebar.write("**Data Loading:**")

    # Define sample data path
    sample_data_path = Path("app/data/sample_api_response.json")

    if st.sidebar.button("🔄 Load Sample Data"):
        st.session_state.data_loaded = True
        st.session_state.normalized_data = load_data(str(sample_data_path))
        st.success("✅ Sample data loaded!")

    # Initialize session state
    if "data_loaded" not in st.session_state:
        st.session_state.data_loaded = False
        st.session_state.normalized_data = None

    # Auto-load if not already loaded
    if not st.session_state.data_loaded:
        if sample_data_path.exists():
            st.info(
                "📂 Click 'Load Sample Data' to get started, or use your own API payload.")
        else:
            st.error(f"❌ Sample data not found at {sample_data_path}")
            return

    # If data is loaded, display results
    if st.session_state.data_loaded and st.session_state.normalized_data:
        normalized_data = st.session_state.normalized_data

        # ====================================================================
        # Section 1: Normalized DataFrames
        # ====================================================================

        st.markdown("---")
        st.header("📋 Normalized Data")

        col1, col2 = st.columns(2)
        with col1:
            display_dataframe_section(
                "Experiments Overview",
                normalized_data.experiments_df,
                height=200
            )
        with col2:
            display_dataframe_section(
                "Creative Metadata",
                normalized_data.metadata_df,
                height=200
            )

        display_dataframe_section(
            "Performance Metrics",
            normalized_data.metrics_df,
            height=300
        )

        # ====================================================================
        # Section 2: A/B Comparison Results
        # ====================================================================

        st.markdown("---")
        st.header("🔍 A/B Comparison Results")

        # Run comparisons
        comparisons = compare_experiments(
            normalized_data, primary_kpi=primary_kpi)

        st.write(
            f"Comparing {len(comparisons)} experiment(s) on **{primary_kpi.upper()}**")
        st.write("")

        # Display each comparison
        for i, comparison in enumerate(comparisons, 1):
            render_experiment_comparison(comparison, primary_kpi)

        # ====================================================================
        # Section 3: Generated Insights
        # ====================================================================

        st.markdown("---")
        st.header("💡 Generated Insights")

        st.write(
            "Rule-based insights generated from comparison data. "
            "Findings are framed as hypotheses, not causal certainties."
        )
        st.write("")

        # Generate and display insights
        for i, comparison in enumerate(comparisons, 1):
            insight = generate_insight(comparison)
            render_insight_section(insight)

        # ====================================================================
        # Footer
        # ====================================================================

        st.markdown("---")
        st.caption(
            "A/B Creative Analytics Prototype v0.1.0 | "
            "Data visualization for API-driven A/B experiment analysis"
        )


if __name__ == "__main__":
    main()
