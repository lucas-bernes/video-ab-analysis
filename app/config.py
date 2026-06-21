"""
Configuration and constants for the A/B Creative Analytics application.
"""

from typing import List, Dict

# ============================================================================
# DEFAULT KPI SETTINGS
# ============================================================================

DEFAULT_KPI = "ctr"  # Click-Through Rate

AVAILABLE_KPIS: List[str] = [
    "ctr",                    # Click-Through Rate
    "vtr",                    # View-Through Rate
    "conversion_rate",        # Conversion Rate
    "roas",                   # Return on Ad Spend
    "cost_per_click",         # Cost per Click
    "cost_per_conversion",    # Cost per Conversion
]

KPI_DESCRIPTIONS: Dict[str, str] = {
    "ctr": "Click-Through Rate (clicks / impressions)",
    "vtr": "View-Through Rate (views / impressions)",
    "conversion_rate": "Conversion Rate (conversions / clicks)",
    "roas": "Return on Ad Spend (revenue / spend)",
    "cost_per_click": "Cost per Click (spend / clicks)",
    "cost_per_conversion": "Cost per Conversion (spend / conversions)",
}

# ============================================================================
# STATISTICAL TESTING SETTINGS
# ============================================================================

# Significance threshold for statistical tests (e.g., p-value)
SIGNIFICANCE_THRESHOLD = 0.05

# Minimum sample size for reliable statistical testing
MIN_SAMPLE_SIZE = 100

# ============================================================================
# KPI THRESHOLD SETTINGS (for business logic)
# ============================================================================

# Minimum percent change to be considered "meaningful" (5%)
MINIMUM_MEANINGFUL_CHANGE_PERCENT = 5.0

# Performance thresholds by KPI
KPI_THRESHOLDS: Dict[str, Dict[str, float]] = {
    "ctr": {
        "excellent": 0.05,   # 5%+
        "good": 0.03,        # 3-5%
        "average": 0.01,     # 1-3%
        "poor": 0.0,         # <1%
    },
    "roas": {
        "excellent": 5.0,
        "good": 3.0,
        "average": 1.5,
        "poor": 1.0,
    },
}

# ============================================================================
# DATA VALIDATION SETTINGS
# ============================================================================

# Supported platforms
SUPPORTED_PLATFORMS = [
    "Facebook",
    "Instagram",
    "YouTube",
    "TikTok",
    "LinkedIn",
    "Twitter",
]

# Supported creative types
SUPPORTED_CREATIVE_TYPES = [
    "hero",
    "testimonial",
    "educational",
    "promotional",
    "user_generated",
    "carousel",
]

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================

# Application version
APP_VERSION = "0.1.0"

# Application name
APP_NAME = "A/B Creative Analytics Prototype"

# Date format for display
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Currency symbol (can be overridden per region)
CURRENCY_SYMBOL = "$"

# ============================================================================
# EXPERIMENT STATUS OPTIONS
# ============================================================================

EXPERIMENT_STATUSES = [
    "running",
    "completed",
    "paused",
    "cancelled",
]
