"""
Domain models for business logic.

These models represent normalized, business-ready data with computed properties
and methods for analysis.
"""

from typing import Optional, Dict, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, validator


class VariantEnum(str, Enum):
    """Supported variant labels."""
    A = "A"
    B = "B"


class CreativeMetrics(BaseModel):
    """Normalized performance metrics for business analysis."""

    impressions: int = Field(..., description="Number of impressions")
    clicks: int = Field(..., description="Number of clicks")
    conversions: int = Field(..., description="Number of conversions")
    views: int = Field(..., description="Number of video views")
    vtr: float = Field(..., description="View-Through Rate (0-1)")
    ctr: float = Field(..., description="Click-Through Rate (0-1)")
    conversion_rate: float = Field(..., description="Conversion Rate (0-1)")
    spend: float = Field(..., description="Total spend")
    revenue: Optional[float] = Field(None, description="Total revenue")
    cost_per_click: float = Field(..., description="Cost per click")
    cost_per_conversion: Optional[float] = Field(
        None, description="Cost per conversion")
    roas: Optional[float] = Field(
        None, description="Return on Ad Spend (revenue / spend)")

    @validator("ctr", "vtr", "conversion_rate")
    def validate_rate(cls, v):
        """Ensure rates are between 0 and 1."""
        if not 0 <= v <= 1:
            raise ValueError("Rate must be between 0 and 1")
        return v

    def get_kpi(self, kpi_name: str) -> float:
        """
        Retrieve a KPI value by name.

        Args:
            kpi_name: Name of KPI (e.g., 'ctr', 'roas', 'cost_per_click')

        Returns:
            The KPI value

        Raises:
            ValueError: If KPI not found or is None
        """
        value = getattr(self, kpi_name, None)
        if value is None:
            raise ValueError(f"KPI '{kpi_name}' not available")
        return value


class CreativeMetadata(BaseModel):
    """Information about the creative asset."""

    creative_id: str = Field(..., description="Unique creative identifier")
    creative_name: str = Field(..., description="Human-readable creative name")
    video_duration_seconds: int = Field(...,
                                        description="Video duration in seconds")
    platform: str = Field(..., description="Ad platform")
    target_audience: str = Field(..., description="Target audience segment")
    creative_type: str = Field(..., description="Creative type/template")


class CreativeVariant(BaseModel):
    """A single variant (A or B) with its metrics and metadata."""

    variant_label: VariantEnum = Field(...,
                                       description="Variant label (A or B)")
    metrics: CreativeMetrics = Field(..., description="Performance metrics")
    metadata: CreativeMetadata = Field(..., description="Creative metadata")
    date_start: datetime = Field(..., description="Period start date")
    date_end: datetime = Field(..., description="Period end date")

    def days_running(self) -> int:
        """Calculate number of days the variant was active."""
        delta = self.date_end - self.date_start
        return delta.days + 1  # Inclusive of both start and end


class Experiment(BaseModel):
    """An A/B experiment with variant A and B."""

    experiment_id: str = Field(..., description="Unique experiment identifier")
    experiment_name: str = Field(...,
                                 description="Human-readable experiment name")
    status: str = Field(..., description="Experiment status")
    variant_a: CreativeVariant = Field(..., description="Variant A")
    variant_b: CreativeVariant = Field(..., description="Variant B")
    hypothesis: Optional[str] = Field(None, description="Original hypothesis")

    @validator("variant_a", "variant_b")
    def validate_variants(cls, v):
        """Ensure variants are properly labeled."""
        if v.variant_label not in [VariantEnum.A, VariantEnum.B]:
            raise ValueError("Variant must be labeled A or B")
        return v


class ABComparisonResult(BaseModel):
    """Result of comparing variant A vs B."""

    experiment_id: str = Field(..., description="Experiment identifier")
    experiment_name: str = Field(..., description="Experiment name")
    kpi: str = Field(..., description="KPI being compared (e.g., 'ctr')")
    variant_a_value: float = Field(..., description="Variant A KPI value")
    variant_b_value: float = Field(..., description="Variant B KPI value")
    difference: float = Field(..., description="Absolute difference (B - A)")
    percent_change: float = Field(...,
                                  description="Percentage change ((B - A) / A * 100)")
    winner: Optional[str] = Field(
        None, description="Winner variant ('A' or 'B')")
    is_statistically_significant: bool = Field(
        False,
        description="Whether difference is statistically significant"
    )
    confidence_level: Optional[float] = Field(
        None,
        description="Confidence level (0-1) if available"
    )
    recommendation: str = Field(..., description="Business recommendation")

    @validator("percent_change")
    def validate_percent_change(cls, v, values):
        """Ensure percent change is calculated correctly."""
        if "variant_a_value" in values and values["variant_a_value"] != 0:
            expected = (
                (values["difference"] / values["variant_a_value"]) * 100
            )
            if abs(v - expected) > 0.01:  # Allow small floating point differences
                raise ValueError("percent_change calculation is incorrect")
        return v

    def summary(self) -> str:
        """Generate a brief text summary of the comparison."""
        direction = "improved" if self.percent_change > 0 else "decreased"
        sig = " (significant)" if self.is_statistically_significant else ""
        return (
            f"Variant {self.winner} {direction} {self.kpi} by {abs(self.percent_change):.1f}%{sig}"
        )
