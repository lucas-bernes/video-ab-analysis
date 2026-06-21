"""
A/B Comparison Engine: Compares variants and generates insights.

This module handles:
1. Comparing Variant A vs B across KPIs
2. Computing metric lifts and deltas
3. Determining winners
4. Detecting metadata differences
5. Returning structured comparison results
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
import pandas as pd

from app.services.normalizer import NormalizedABData
from app.config import DEFAULT_KPI, AVAILABLE_KPIS


@dataclass
class MetricComparison:
    """Comparison of a single metric between variants."""

    metric_name: str
    variant_a_value: Optional[float]
    variant_b_value: Optional[float]
    delta: Optional[float] = None
    lift_percent: Optional[float] = None
    winner: Optional[str] = None

    def __post_init__(self):
        """Compute delta and lift after initialization."""
        if self.variant_a_value is not None and self.variant_b_value is not None:
            self.delta = self.variant_b_value - self.variant_a_value

            # Compute percent lift
            if self.variant_a_value != 0:
                self.lift_percent = (self.delta / self.variant_a_value) * 100
            else:
                self.lift_percent = None

            # Determine winner (higher is better for most metrics)
            if self.variant_b_value > self.variant_a_value:
                self.winner = "B"
            elif self.variant_b_value < self.variant_a_value:
                self.winner = "A"
            else:
                self.winner = None

    def summary(self) -> str:
        """Generate a text summary of the comparison."""
        if self.lift_percent is None:
            return f"{self.metric_name}: A={self.variant_a_value}, B={self.variant_b_value}"

        direction = "↑" if self.lift_percent > 0 else "↓"
        return (
            f"{self.metric_name}: {direction} {abs(self.lift_percent):.1f}% "
            f"(A={self.variant_a_value:.4g}, B={self.variant_b_value:.4g})"
        )


@dataclass
class ExperimentComparison:
    """Result of comparing one A/B experiment."""

    experiment_id: str
    experiment_name: str
    platform: str
    primary_kpi: str
    primary_kpi_value_a: Optional[float]
    primary_kpi_value_b: Optional[float]
    primary_kpi_lift_percent: Optional[float]
    winner_variant: Optional[str]

    # Detailed metric comparisons
    metric_comparisons: Dict[str, MetricComparison] = field(
        default_factory=dict)

    # Metadata differences
    metadata_differences: List[str] = field(default_factory=list)

    # Summary and recommendation
    recommendation: str = ""

    def summary(self) -> str:
        """Generate a concise text summary of the experiment."""
        if self.winner_variant is None:
            return f"{self.experiment_id}: No clear winner on {self.primary_kpi}"

        direction = "wins" if self.primary_kpi_lift_percent >= 0 else "loses"
        lift_abs = abs(
            self.primary_kpi_lift_percent) if self.primary_kpi_lift_percent else 0
        return (
            f"{self.experiment_id}: Variant {self.winner_variant} {direction} "
            f"on {self.primary_kpi} by {lift_abs:.1f}%"
        )

    def detailed_summary(self) -> str:
        """Generate a detailed summary with multiple KPIs."""
        lines = [
            f"\n{'='*60}",
            f"Experiment: {self.experiment_id} ({self.experiment_name})",
            f"Platform: {self.platform}",
            f"{'='*60}",
            f"\nPrimary KPI: {self.primary_kpi}",
            f"  Winner: Variant {self.winner_variant}",
            f"  Lift: {self.primary_kpi_lift_percent:+.1f}%",
            f"\nMetric Details:",
        ]

        for metric_name, comparison in sorted(self.metric_comparisons.items()):
            lines.append(f"  {comparison.summary()}")

        if self.metadata_differences:
            lines.append(f"\nMetadata Differences:")
            for diff in self.metadata_differences:
                lines.append(f"  - {diff}")

        if self.recommendation:
            lines.append(f"\nRecommendation:\n  {self.recommendation}")

        lines.append(f"{'='*60}\n")

        return "\n".join(lines)


class ABComparator:
    """Engine for comparing A/B experiment variants."""

    # Metrics to compare by default
    COMPARISON_METRICS = [
        "impressions",
        "clicks",
        "ctr",
        "conversions",
        "conversion_rate",
        "spend",
        "revenue",
        "cost_per_click",
        "cost_per_conversion",
        "roas",
    ]

    def __init__(self, primary_kpi: str = DEFAULT_KPI):
        """
        Initialize comparator.

        Args:
            primary_kpi: KPI to use for determining winner (default: 'ctr')
        """
        if primary_kpi not in AVAILABLE_KPIS:
            raise ValueError(
                f"Unknown KPI: {primary_kpi}. Available: {AVAILABLE_KPIS}")

        self.primary_kpi = primary_kpi

    def compare(self, normalized_data: NormalizedABData) -> List[ExperimentComparison]:
        """
        Compare all experiments in normalized data.

        Args:
            normalized_data: NormalizedABData from normalizer module

        Returns:
            List of ExperimentComparison results
        """
        results = []

        # Get experiments metadata
        exp_metadata = normalized_data.experiments_df.set_index(
            "experiment_id").to_dict("index")

        # Group metrics by experiment
        metrics_df = normalized_data.metrics_df
        metrics_grouped = metrics_df.groupby("experiment_id")

        for exp_id, exp_metrics in metrics_grouped:
            result = self._compare_experiment(
                exp_id,
                exp_metrics,
                exp_metadata.get(exp_id, {}),
                normalized_data,
            )
            results.append(result)

        return results

    def _compare_experiment(
        self,
        exp_id: str,
        metrics_data: pd.DataFrame,
        exp_metadata: Dict[str, Any],
        normalized_data: NormalizedABData,
    ) -> ExperimentComparison:
        """
        Compare a single experiment's A vs B variants.

        Args:
            exp_id: Experiment ID
            metrics_data: DataFrame rows for this experiment (variant A and B)
            exp_metadata: Metadata dict from experiments_df
            normalized_data: Full normalized data (for metadata diff lookup)

        Returns:
            ExperimentComparison result
        """
        # Split A and B metrics
        variant_a_row = metrics_data[metrics_data["variant"] == "A"]
        variant_b_row = metrics_data[metrics_data["variant"] == "B"]

        variant_a_metrics = variant_a_row.iloc[0].to_dict() if len(
            variant_a_row) > 0 else {}
        variant_b_metrics = variant_b_row.iloc[0].to_dict() if len(
            variant_b_row) > 0 else {}

        # Get primary KPI values
        primary_a = variant_a_metrics.get(self.primary_kpi)
        primary_b = variant_b_metrics.get(self.primary_kpi)

        # Compute primary KPI lift
        primary_lift = None
        winner = None
        if primary_a is not None and primary_b is not None and primary_a != 0:
            primary_lift = ((primary_b - primary_a) / primary_a) * 100
            winner = "B" if primary_b > primary_a else "A"

        # Compare all metrics
        metric_comparisons = self._compare_metrics(
            variant_a_metrics,
            variant_b_metrics,
        )

        # Find metadata differences
        metadata_diffs = self._compare_metadata(exp_id, normalized_data)

        # Generate recommendation
        recommendation = self._generate_recommendation(
            winner,
            primary_lift,
            metric_comparisons,
        )

        return ExperimentComparison(
            experiment_id=exp_id,
            experiment_name=exp_metadata.get("campaign_name", "Unnamed"),
            platform=exp_metadata.get("platform", "Unknown"),
            primary_kpi=self.primary_kpi,
            primary_kpi_value_a=primary_a,
            primary_kpi_value_b=primary_b,
            primary_kpi_lift_percent=primary_lift,
            winner_variant=winner,
            metric_comparisons=metric_comparisons,
            metadata_differences=metadata_diffs,
            recommendation=recommendation,
        )

    def _compare_metrics(
        self,
        variant_a: Dict[str, Any],
        variant_b: Dict[str, Any],
    ) -> Dict[str, MetricComparison]:
        """
        Compare metrics between variants.

        Args:
            variant_a: Variant A metrics dict
            variant_b: Variant B metrics dict

        Returns:
            Dict of metric_name -> MetricComparison
        """
        comparisons = {}

        for metric in self.COMPARISON_METRICS:
            value_a = variant_a.get(metric)
            value_b = variant_b.get(metric)

            # Skip if both are None
            if value_a is None and value_b is None:
                continue

            comparison = MetricComparison(
                metric_name=metric,
                variant_a_value=value_a,
                variant_b_value=value_b,
            )
            comparisons[metric] = comparison

        return comparisons

    def _compare_metadata(
        self,
        exp_id: str,
        normalized_data: NormalizedABData,
    ) -> List[str]:
        """
        Detect metadata differences between variants.

        Args:
            exp_id: Experiment ID
            normalized_data: NormalizedABData

        Returns:
            List of difference descriptions
        """
        differences = []

        # Get metadata for this experiment
        metadata_df = normalized_data.metadata_df
        exp_metadata = metadata_df[metadata_df["experiment_id"] == exp_id]

        if len(exp_metadata) < 2:
            return differences

        variant_a = exp_metadata[exp_metadata["variant"]
                                 == "A"].iloc[0].to_dict()
        variant_b = exp_metadata[exp_metadata["variant"]
                                 == "B"].iloc[0].to_dict()

        # Compare interesting fields
        fields_to_compare = [
            "video_duration_seconds",
            "platform",
            "target_audience",
            "creative_type",
        ]

        for field in fields_to_compare:
            val_a = variant_a.get(field)
            val_b = variant_b.get(field)

            if val_a != val_b and val_a is not None and val_b is not None:
                differences.append(
                    f"{field}: A={val_a}, B={val_b}"
                )

        return differences

    def _generate_recommendation(
        self,
        winner: Optional[str],
        primary_lift: Optional[float],
        metric_comparisons: Dict[str, MetricComparison],
    ) -> str:
        """
        Generate a business recommendation based on comparison.

        Args:
            winner: Winning variant ('A' or 'B')
            primary_lift: Percent lift on primary KPI
            metric_comparisons: Dict of all metric comparisons

        Returns:
            Recommendation text
        """
        if winner is None or primary_lift is None:
            return "Insufficient data for recommendation."

        lift_threshold = 5.0  # Consider >5% lift meaningful

        if abs(primary_lift) < lift_threshold:
            return (
                f"No significant difference on {self.primary_kpi}. "
                f"Consider analyzing secondary metrics or running longer."
            )

        if primary_lift > 0:
            return (
                f"Variant {winner} shows {primary_lift:+.1f}% improvement on {self.primary_kpi}. "
                f"Recommend scaling Variant {winner}."
            )
        else:
            return (
                f"Variant {winner} shows {primary_lift:+.1f}% decline on {self.primary_kpi}. "
                f"Recommend pausing Variant {winner} or investigating causes."
            )


def compare_experiments(
    normalized_data: NormalizedABData,
    primary_kpi: str = DEFAULT_KPI,
) -> List[ExperimentComparison]:
    """
    Convenience function: Compare all experiments with default settings.

    Args:
        normalized_data: NormalizedABData from normalizer
        primary_kpi: Primary KPI for comparison (default: 'ctr')

    Returns:
        List of ExperimentComparison results
    """
    comparator = ABComparator(primary_kpi=primary_kpi)
    return comparator.compare(normalized_data)
