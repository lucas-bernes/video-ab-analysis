"""
Pydantic models representing the nested API response format.

These models strictly define the structure of data returned from the API.
No business logic; purely for validation and serialization.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field


class APIPerformanceMetrics(BaseModel):
    """Raw performance metrics from API response."""

    impressions: int = Field(..., description="Number of impressions")
    clicks: int = Field(..., description="Number of clicks")
    conversions: int = Field(..., description="Number of conversions")
    views: int = Field(..., description="Number of video views")
    view_through_rate: Optional[float] = Field(
        None, description="VTR as decimal (0-1)")
    click_through_rate: Optional[float] = Field(
        None, description="CTR as decimal (0-1)")
    conversion_rate: Optional[float] = Field(
        None, description="Conversion rate as decimal (0-1)")
    spend: float = Field(..., description="Total spend in currency units")
    revenue: Optional[float] = Field(
        None, description="Total revenue in currency units")

    class Config:
        json_schema_extra = {
            "example": {
                "impressions": 10000,
                "clicks": 500,
                "conversions": 50,
                "views": 8000,
                "view_through_rate": 0.8,
                "click_through_rate": 0.05,
                "conversion_rate": 0.01,
                "spend": 1000.0,
                "revenue": 5000.0,
            }
        }


class APICreativeMetadata(BaseModel):
    """Metadata about the creative (ad content)."""

    creative_id: str = Field(...,
                             description="Unique identifier for the creative")
    creative_name: str = Field(..., description="Human-readable creative name")
    video_duration_seconds: int = Field(...,
                                        description="Video duration in seconds")
    platform: str = Field(...,
                          description="Platform (e.g., 'Facebook', 'YouTube', 'TikTok')")
    target_audience: str = Field(..., description="Target audience segment")
    creative_type: str = Field(...,
                               description="Type of creative (e.g., 'hero', 'testimonial')")

    class Config:
        json_schema_extra = {
            "example": {
                "creative_id": "cr_001_hero",
                "creative_name": "Hero Campaign - Variant A",
                "video_duration_seconds": 15,
                "platform": "Facebook",
                "target_audience": "25-45 year old professionals",
                "creative_type": "hero",
            }
        }


class APICreativeVariant(BaseModel):
    """Represents a single variant (A or B) in the A/B experiment."""

    variant_label: str = Field(..., description="Variant identifier (A or B)")
    metrics: APIPerformanceMetrics = Field(...,
                                           description="Performance metrics")
    metadata: APICreativeMetadata = Field(..., description="Creative metadata")
    date_start: datetime = Field(..., description="Experiment start date")
    date_end: datetime = Field(..., description="Experiment end date")

    class Config:
        json_schema_extra = {
            "example": {
                "variant_label": "A",
                "metrics": {
                    "impressions": 10000,
                    "clicks": 500,
                    "conversions": 50,
                    "views": 8000,
                    "view_through_rate": 0.8,
                    "click_through_rate": 0.05,
                    "conversion_rate": 0.01,
                    "spend": 1000.0,
                    "revenue": 5000.0,
                },
                "metadata": {
                    "creative_id": "cr_001_hero",
                    "creative_name": "Hero Campaign - Variant A",
                    "video_duration_seconds": 15,
                    "platform": "Facebook",
                    "target_audience": "25-45 year old professionals",
                    "creative_type": "hero",
                },
                "date_start": "2026-06-01T00:00:00",
                "date_end": "2026-06-07T23:59:59",
            }
        }


class APIExperiment(BaseModel):
    """Root API response representing an A/B experiment."""

    experiment_id: str = Field(..., description="Unique experiment identifier")
    experiment_name: str = Field(...,
                                 description="Human-readable experiment name")
    status: str = Field(...,
                        description="Experiment status (running, completed, paused)")
    variants: List[APICreativeVariant] = Field(
        ..., description="List of variants (A, B, etc.)")
    hypothesis: Optional[str] = Field(
        None, description="Original hypothesis for the experiment")

    class Config:
        json_schema_extra = {
            "example": {
                "experiment_id": "exp_001",
                "experiment_name": "Q2 Video Campaign A/B Test",
                "status": "completed",
                "hypothesis": "Shorter videos increase engagement",
                "variants": [
                    {
                        "variant_label": "A",
                        "metrics": {},
                        "metadata": {},
                        "date_start": "2026-06-01T00:00:00",
                        "date_end": "2026-06-07T23:59:59",
                    }
                ],
            }
        }
