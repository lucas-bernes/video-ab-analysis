"""Service layer for business logic."""

from app.services.normalizer import (
    NormalizedABData,
    normalize_experiments,
    normalize_from_file,
    load_json_payload,
)
from app.services.comparator import (
    MetricComparison,
    ExperimentComparison,
    ABComparator,
    compare_experiments,
)
from app.services.insight_generator import (
    InsightResult,
    InsightGenerator,
    generate_insight,
)

__all__ = [
    "NormalizedABData",
    "normalize_experiments",
    "normalize_from_file",
    "load_json_payload",
    "MetricComparison",
    "ExperimentComparison",
    "ABComparator",
    "compare_experiments",
    "InsightResult",
    "InsightGenerator",
    "generate_insight",
]
