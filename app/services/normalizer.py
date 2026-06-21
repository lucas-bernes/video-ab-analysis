"""
Normalization layer: Converts nested API payloads into clean domain objects and DataFrames.

This module handles:
1. Loading JSON API responses
2. Parsing into Pydantic domain models
3. Flattening to pandas DataFrames for analysis
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

import pandas as pd
from pydantic import ValidationError

from app.models.domain_models import (
    Experiment,
    CreativeVariant,
    CreativeMetrics,
    CreativeMetadata,
)


@dataclass
class NormalizedABData:
    """Container for normalized A/B experiment data."""

    experiments: List[Experiment]
    experiments_df: pd.DataFrame
    variants_df: pd.DataFrame
    metrics_df: pd.DataFrame
    metadata_df: pd.DataFrame

    def __repr__(self) -> str:
        return (
            f"NormalizedABData("
            f"n_experiments={len(self.experiments)}, "
            f"experiments_df={self.experiments_df.shape}, "
            f"variants_df={self.variants_df.shape}, "
            f"metrics_df={self.metrics_df.shape}, "
            f"metadata_df={self.metadata_df.shape})"
        )


def load_json_payload(file_path: str) -> Dict[str, Any]:
    """
    Load JSON payload from file.

    Args:
        file_path: Path to JSON file

    Returns:
        Parsed JSON as dictionary

    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If JSON is invalid
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    with open(path, "r") as f:
        return json.load(f)


def _parse_variant_from_payload(
    experiment_dict: Dict,
    variant_key: str,
    variant_label: str,
) -> tuple[Dict[str, Any], CreativeVariant]:
    """
    Parse a single variant (A or B) from experiment payload.

    Args:
        experiment_dict: Experiment data from JSON
        variant_key: Key in experiment dict (e.g., 'variant_a', 'variant_b')
        variant_label: Label for variant ('A' or 'B')

    Returns:
        Tuple of (raw_variant_dict, CreativeVariant domain object)
    """
    raw_variant = experiment_dict[variant_key]

    # Parse metrics
    metrics_data = raw_variant["metrics"]
    metrics = CreativeMetrics(
        impressions=metrics_data["impressions"],
        clicks=metrics_data["clicks"],
        conversions=metrics_data["conversions"],
        # Fallback if views not provided
        views=metrics_data.get("impressions", 0),
        vtr=metrics_data.get("ctr", 0.0),  # VTR placeholder
        ctr=metrics_data["ctr"],
        conversion_rate=metrics_data["conversion_rate"],
        spend=metrics_data["spend"],
        revenue=metrics_data.get("revenue"),
        cost_per_click=metrics_data["spend"] / metrics_data["clicks"]
        if metrics_data["clicks"] > 0
        else 0.0,
        cost_per_conversion=(
            metrics_data["spend"] / metrics_data["conversions"]
            if metrics_data["conversions"] > 0
            else None
        ),
        roas=(
            metrics_data.get("revenue", 0) / metrics_data["spend"]
            if metrics_data["spend"] > 0
            else None
        ),
    )

    # Parse metadata
    metadata_data = raw_variant["metadata"]
    metadata = CreativeMetadata(
        creative_id=raw_variant["creative_id"],
        creative_name=raw_variant["creative_name"],
        video_duration_seconds=metadata_data["duration_sec"],
        platform=experiment_dict.get("platform", "Unknown"),
        target_audience="",  # Not in sample payload
        creative_type="",  # Not in sample payload
    )

    # Parse dates
    date_start = datetime.fromisoformat(
        experiment_dict["date_start"].replace("Z", "+00:00")
    )
    date_end = datetime.fromisoformat(
        experiment_dict["date_end"].replace("Z", "+00:00")
    )

    # Create variant object
    variant = CreativeVariant(
        variant_label=variant_label,
        metrics=metrics,
        metadata=metadata,
        date_start=date_start,
        date_end=date_end,
    )

    return raw_variant, variant


def normalize_experiments(payload: Dict[str, Any]) -> NormalizedABData:
    """
    Normalize nested API payload into clean domain objects and DataFrames.

    Args:
        payload: Raw API response (dict with 'experiments' key)

    Returns:
        NormalizedABData containing parsed experiments and flattened DataFrames

    Raises:
        ValidationError: If data does not match domain models
        KeyError: If required fields are missing
    """
    experiments_list: List[Experiment] = []

    # Parse experiments
    for exp_dict in payload.get("experiments", []):
        # Parse variant A
        _, variant_a = _parse_variant_from_payload(
            exp_dict, "variant_a", "A"
        )

        # Parse variant B
        _, variant_b = _parse_variant_from_payload(
            exp_dict, "variant_b", "B"
        )

        # Create experiment
        experiment = Experiment(
            experiment_id=exp_dict["experiment_id"],
            experiment_name=exp_dict.get("campaign_name", "Unnamed"),
            status=exp_dict.get("status", "unknown"),
            variant_a=variant_a,
            variant_b=variant_b,
            hypothesis=exp_dict.get("hypothesis"),
        )

        experiments_list.append(experiment)

    # Build DataFrames
    experiments_df = _build_experiments_df(payload)
    variants_df = _build_variants_df(experiments_list, payload)
    metrics_df = _build_metrics_df(experiments_list)
    metadata_df = _build_metadata_df(experiments_list)

    return NormalizedABData(
        experiments=experiments_list,
        experiments_df=experiments_df,
        variants_df=variants_df,
        metrics_df=metrics_df,
        metadata_df=metadata_df,
    )


def _build_experiments_df(payload: Dict[str, Any]) -> pd.DataFrame:
    """Build experiments DataFrame."""
    rows = []
    for exp in payload.get("experiments", []):
        rows.append({
            "experiment_id": exp["experiment_id"],
            "campaign_id": exp.get("campaign_id", ""),
            "campaign_name": exp.get("campaign_name", ""),
            "platform": exp.get("platform", ""),
            "status": exp.get("status", ""),
            "hypothesis": exp.get("hypothesis", ""),
            "date_start": exp.get("date_start", ""),
            "date_end": exp.get("date_end", ""),
        })
    return pd.DataFrame(rows)


def _build_variants_df(
    experiments: List[Experiment],
    payload: Dict[str, Any],
) -> pd.DataFrame:
    """Build variants DataFrame with creative info."""
    rows = []

    for exp, exp_payload in zip(
        experiments, payload.get("experiments", [])
    ):
        # Variant A
        rows.append({
            "experiment_id": exp.experiment_id,
            "variant": "A",
            "creative_id": exp.variant_a.metadata.creative_id,
            "creative_name": exp.variant_a.metadata.creative_name,
            "video_url": exp_payload["variant_a"].get("video_url", ""),
            "thumbnail_url": exp_payload["variant_a"].get("thumbnail_url", ""),
            "video_duration_seconds": exp.variant_a.metadata.video_duration_seconds,
            "date_start": exp.variant_a.date_start,
            "date_end": exp.variant_a.date_end,
        })

        # Variant B
        rows.append({
            "experiment_id": exp.experiment_id,
            "variant": "B",
            "creative_id": exp.variant_b.metadata.creative_id,
            "creative_name": exp.variant_b.metadata.creative_name,
            "video_url": exp_payload["variant_b"].get("video_url", ""),
            "thumbnail_url": exp_payload["variant_b"].get("thumbnail_url", ""),
            "video_duration_seconds": exp.variant_b.metadata.video_duration_seconds,
            "date_start": exp.variant_b.date_start,
            "date_end": exp.variant_b.date_end,
        })

    return pd.DataFrame(rows)


def _build_metrics_df(experiments: List[Experiment]) -> pd.DataFrame:
    """Build metrics DataFrame with performance data."""
    rows = []

    for exp in experiments:
        # Variant A metrics
        rows.append({
            "experiment_id": exp.experiment_id,
            "variant": "A",
            "creative_id": exp.variant_a.metadata.creative_id,
            "impressions": exp.variant_a.metrics.impressions,
            "clicks": exp.variant_a.metrics.clicks,
            "ctr": exp.variant_a.metrics.ctr,
            "conversions": exp.variant_a.metrics.conversions,
            "conversion_rate": exp.variant_a.metrics.conversion_rate,
            "spend": exp.variant_a.metrics.spend,
            "revenue": exp.variant_a.metrics.revenue,
            "cost_per_click": exp.variant_a.metrics.cost_per_click,
            "cost_per_conversion": exp.variant_a.metrics.cost_per_conversion,
            "roas": exp.variant_a.metrics.roas,
        })

        # Variant B metrics
        rows.append({
            "experiment_id": exp.experiment_id,
            "variant": "B",
            "creative_id": exp.variant_b.metadata.creative_id,
            "impressions": exp.variant_b.metrics.impressions,
            "clicks": exp.variant_b.metrics.clicks,
            "ctr": exp.variant_b.metrics.ctr,
            "conversions": exp.variant_b.metrics.conversions,
            "conversion_rate": exp.variant_b.metrics.conversion_rate,
            "spend": exp.variant_b.metrics.spend,
            "revenue": exp.variant_b.metrics.revenue,
            "cost_per_click": exp.variant_b.metrics.cost_per_click,
            "cost_per_conversion": exp.variant_b.metrics.cost_per_conversion,
            "roas": exp.variant_b.metrics.roas,
        })

    return pd.DataFrame(rows)


def _build_metadata_df(experiments: List[Experiment]) -> pd.DataFrame:
    """Build metadata DataFrame with creative details."""
    rows = []

    for exp in experiments:
        # Variant A metadata (requires access to raw payload for tags)
        rows.append({
            "experiment_id": exp.experiment_id,
            "variant": "A",
            "creative_id": exp.variant_a.metadata.creative_id,
            "creative_name": exp.variant_a.metadata.creative_name,
            "video_duration_seconds": exp.variant_a.metadata.video_duration_seconds,
            "date_start": exp.variant_a.date_start,
            "date_end": exp.variant_a.date_end,
            "platform": exp.variant_a.metadata.platform,
            "target_audience": exp.variant_a.metadata.target_audience,
            "creative_type": exp.variant_a.metadata.creative_type,
        })

        # Variant B metadata
        rows.append({
            "experiment_id": exp.experiment_id,
            "variant": "B",
            "creative_id": exp.variant_b.metadata.creative_id,
            "creative_name": exp.variant_b.metadata.creative_name,
            "video_duration_seconds": exp.variant_b.metadata.video_duration_seconds,
            "date_start": exp.variant_b.date_start,
            "date_end": exp.variant_b.date_end,
            "platform": exp.variant_b.metadata.platform,
            "target_audience": exp.variant_b.metadata.target_audience,
            "creative_type": exp.variant_b.metadata.creative_type,
        })

    return pd.DataFrame(rows)


def normalize_from_file(file_path: str) -> NormalizedABData:
    """
    Convenience function: Load JSON and normalize in one call.

    Args:
        file_path: Path to JSON file

    Returns:
        NormalizedABData
    """
    payload = load_json_payload(file_path)
    return normalize_experiments(payload)
