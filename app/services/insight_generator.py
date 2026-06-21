"""
Insight Generator: Creates business-facing narratives from A/B comparison results.

This module transforms structured comparison data into human-readable insights
that frame findings as hypotheses rather than causal certainties.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any

from app.services.comparator import ExperimentComparison, MetricComparison


@dataclass
class InsightResult:
    """Result of insight generation for an experiment."""

    experiment_id: str
    experiment_name: str
    platform: str

    # Core finding
    headline: str

    # Narrative paragraph
    summary: str

    # Detailed findings
    findings: List[str]

    # Confidence (low, medium, high) based on data richness
    confidence: str

    def __str__(self) -> str:
        """Format for printing."""
        result = f"\n{'='*70}\n"
        result += f"📊 {self.experiment_id}: {self.experiment_name}\n"
        result += f"Platform: {self.platform} | Confidence: {self.confidence}\n"
        result += f"{'='*70}\n"
        result += f"\n{self.headline}\n"
        result += f"\n{self.summary}\n"

        if self.findings:
            result += f"\nKey Findings:\n"
            for finding in self.findings:
                result += f"  • {finding}\n"

        result += f"\n{'='*70}\n"
        return result


class InsightGenerator:
    """Rule-based engine for generating business insights from A/B comparisons."""

    # Thresholds for determining insight confidence
    STRONG_LIFT_THRESHOLD = 10.0      # >10% is strong
    MODERATE_LIFT_THRESHOLD = 5.0     # >5% is moderate
    WEAK_LIFT_THRESHOLD = 2.0         # >2% is weak

    # Secondary metrics to monitor
    SECONDARY_METRICS = ["conversion_rate", "cost_per_click", "roas"]
    ENGAGEMENT_METRICS = ["avg_watch_time", "views"]

    def generate(self, comparison: ExperimentComparison) -> InsightResult:
        """
        Generate insights for a single comparison result.

        Args:
            comparison: ExperimentComparison result

        Returns:
            InsightResult with headline, summary, and findings
        """
        # Generate headline
        headline = self._generate_headline(comparison)

        # Analyze performance
        performance_insights = self._analyze_performance(comparison)

        # Analyze secondary metrics
        secondary_insights = self._analyze_secondary_metrics(comparison)

        # Analyze metadata relationships
        metadata_insights = self._analyze_metadata(comparison)

        # Combine all findings
        all_findings = (
            performance_insights +
            secondary_insights +
            metadata_insights
        )

        # Generate narrative summary
        summary = self._generate_narrative(
            comparison,
            performance_insights,
            secondary_insights,
            metadata_insights,
        )

        # Determine confidence
        confidence = self._assess_confidence(comparison, all_findings)

        return InsightResult(
            experiment_id=comparison.experiment_id,
            experiment_name=comparison.experiment_name,
            platform=comparison.platform,
            headline=headline,
            summary=summary,
            findings=all_findings,
            confidence=confidence,
        )

    def _generate_headline(self, comparison: ExperimentComparison) -> str:
        """Generate a concise headline for the result."""
        if comparison.winner_variant is None:
            return (
                f"No clear winner on {comparison.primary_kpi}. "
                f"Consider analyzing other metrics."
            )

        lift_abs = abs(comparison.primary_kpi_lift_percent)
        primary_kpi_friendly = comparison.primary_kpi.upper().replace("_", " ")

        if lift_abs > self.STRONG_LIFT_THRESHOLD:
            intensity = "significantly"
        elif lift_abs > self.MODERATE_LIFT_THRESHOLD:
            intensity = "meaningfully"
        else:
            intensity = "slightly"

        direction = "outperformed" if comparison.primary_kpi_lift_percent > 0 else "underperformed"

        return (
            f"Variant {comparison.winner_variant} {intensity} {direction} Variant "
            f"{'A' if comparison.winner_variant == 'B' else 'B'} "
            f"on {primary_kpi_friendly} ({lift_abs:.1f}% {'increase' if comparison.primary_kpi_lift_percent > 0 else 'decrease'})."
        )

    def _analyze_performance(self, comparison: ExperimentComparison) -> List[str]:
        """Analyze primary and key secondary performance metrics."""
        findings = []

        # Primary KPI
        if comparison.primary_kpi_lift_percent is not None:
            lift = comparison.primary_kpi_lift_percent
            variant_winner = comparison.winner_variant

            if variant_winner:
                findings.append(
                    f"Variant {variant_winner} achieved {abs(lift):.1f}% "
                    f"{'higher' if lift > 0 else 'lower'} {comparison.primary_kpi.upper()} "
                    f"({comparison.primary_kpi_value_a:.4g} → {comparison.primary_kpi_value_b:.4g})."
                )

        return findings

    def _analyze_secondary_metrics(self, comparison: ExperimentComparison) -> List[str]:
        """Analyze secondary metrics that support the primary finding."""
        findings = []

        metrics_to_check = comparison.metric_comparisons

        # Check conversion rate
        if "conversion_rate" in metrics_to_check:
            conv_comp = metrics_to_check["conversion_rate"]
            if conv_comp.lift_percent is not None and abs(conv_comp.lift_percent) > self.WEAK_LIFT_THRESHOLD:
                findings.append(
                    f"Conversion rate also improved, suggesting better downstream engagement "
                    f"({conv_comp.lift_percent:+.1f}%)."
                )

        # Check cost efficiency
        if "cost_per_click" in metrics_to_check:
            cpc_comp = metrics_to_check["cost_per_click"]
            if cpc_comp.lift_percent is not None and cpc_comp.lift_percent < -self.WEAK_LIFT_THRESHOLD:
                findings.append(
                    f"Cost per click decreased by {abs(cpc_comp.lift_percent):.1f}%, "
                    f"indicating improved efficiency."
                )

        # Check ROAS
        if "roas" in metrics_to_check:
            roas_comp = metrics_to_check["roas"]
            if roas_comp.lift_percent is not None and roas_comp.lift_percent > self.WEAK_LIFT_THRESHOLD:
                findings.append(
                    f"Return on ad spend improved by {roas_comp.lift_percent:.1f}%, "
                    f"suggesting better overall business impact."
                )

        return findings

    def _analyze_metadata(self, comparison: ExperimentComparison) -> List[str]:
        """Generate hypotheses based on metadata differences."""
        findings = []

        if not comparison.metadata_differences:
            return findings

        # Parse metadata differences
        for diff in comparison.metadata_differences:
            insight = self._generate_metadata_hypothesis(diff, comparison)
            if insight:
                findings.append(insight)

        return findings

    def _generate_metadata_hypothesis(
        self,
        metadata_diff: str,
        comparison: ExperimentComparison,
    ) -> Optional[str]:
        """
        Convert a metadata difference into a business hypothesis.

        Args:
            metadata_diff: Difference description (e.g., "video_duration_seconds: A=15, B=30")
            comparison: Full comparison for context

        Returns:
            Hypothesis string or None
        """
        # Parse the difference
        if "video_duration_seconds:" in metadata_diff:
            parts = metadata_diff.split("A=")[1].split(", B=")
            try:
                duration_a = int(parts[0])
                duration_b = int(parts[1])

                winning_duration = (
                    duration_b if comparison.winner_variant == "B" else duration_a
                )
                losing_duration = (
                    duration_a if comparison.winner_variant == "B" else duration_b
                )

                if comparison.primary_kpi_lift_percent and comparison.primary_kpi_lift_percent > 0:
                    if winning_duration < losing_duration:
                        return (
                            f"The winning variant's shorter duration ({winning_duration}s vs {losing_duration}s) "
                            f"may have contributed to faster value communication and higher engagement."
                        )
                    else:
                        return (
                            f"The winning variant's longer duration ({winning_duration}s vs {losing_duration}s) "
                            f"may have provided more context and storytelling, boosting viewer confidence."
                        )
            except (ValueError, IndexError):
                pass

        if "creative_type:" in metadata_diff:
            return (
                f"Creative type differs between variants: {metadata_diff}. "
                f"This may explain differences in engagement patterns."
            )

        # Generic fallback
        return f"Note: {metadata_diff}"

    def _generate_narrative(
        self,
        comparison: ExperimentComparison,
        performance_insights: List[str],
        secondary_insights: List[str],
        metadata_insights: List[str],
    ) -> str:
        """Generate a cohesive narrative paragraph."""
        if comparison.winner_variant is None:
            return (
                f"The experiment did not produce a clear winner on {comparison.primary_kpi}. "
                f"Both variants showed similar performance. Consider running the test longer "
                f"or analyzing secondary metrics for insights."
            )

        lines = []

        # Opening
        variant_winner = comparison.winner_variant
        lift = abs(comparison.primary_kpi_lift_percent)
        lines.append(
            f"Variant {variant_winner} outperformed Variant {'A' if variant_winner == 'B' else 'B'} "
            f"with a {lift:.1f}% higher {comparison.primary_kpi.upper()}."
        )

        # Secondary metrics context
        if secondary_insights:
            lines.append(" " + secondary_insights[0])

        # Metadata hypotheses
        if metadata_insights:
            hypothesis_text = " ".join(
                metadata_insights[:2])  # First 1-2 hypotheses
            lines.append(f" This may be because {hypothesis_text.lower()}")

        # Closing recommendation
        if lift > self.STRONG_LIFT_THRESHOLD:
            lines.append(
                f" The results are compelling enough to consider scaling Variant {variant_winner}."
            )
        elif lift > self.MODERATE_LIFT_THRESHOLD:
            lines.append(
                f" These results warrant further testing before full-scale deployment."
            )
        else:
            lines.append(
                f" Monitor additional metrics before making a final decision."
            )

        narrative = "".join(lines)
        # Clean up spacing and capitalization
        narrative = narrative.replace("  ", " ").replace(" .", ".").strip()

        return narrative

    def _assess_confidence(
        self,
        comparison: ExperimentComparison,
        findings: List[str],
    ) -> str:
        """
        Assess confidence level based on data completeness and consistency.

        Returns: "low", "medium", or "high"
        """
        signals = 0

        # Signal 1: Primary KPI has strong lift
        if (comparison.primary_kpi_lift_percent and
                abs(comparison.primary_kpi_lift_percent) > self.STRONG_LIFT_THRESHOLD):
            signals += 2
        elif (comparison.primary_kpi_lift_percent and
              abs(comparison.primary_kpi_lift_percent) > self.MODERATE_LIFT_THRESHOLD):
            signals += 1

        # Signal 2: Secondary metrics align
        if len(findings) > 2:
            signals += 1

        # Signal 3: Metadata differences explain variance
        if comparison.metadata_differences:
            signals += 1

        # Signal 4: Multiple metrics available
        if len(comparison.metric_comparisons) > 5:
            signals += 1

        if signals >= 4:
            return "HIGH"
        elif signals >= 2:
            return "MEDIUM"
        else:
            return "LOW"


def generate_insight(comparison: ExperimentComparison) -> InsightResult:
    """
    Convenience function: Generate insight from a comparison result.

    Args:
        comparison: ExperimentComparison result

    Returns:
        InsightResult
    """
    generator = InsightGenerator()
    return generator.generate(comparison)
