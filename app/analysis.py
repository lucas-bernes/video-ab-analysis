import json
from pathlib import Path

import pandas as pd

from video_fetcher import fetch_video
from video_features import extract_video_features


def load_api_response(json_path: str) -> dict:
    """
    Loads the mock API response from a JSON file.

    Args:
        json_path (str): Path to the JSON file.

    Returns:
        dict: Parsed JSON content.
    """
    with open(json_path, "r", encoding="utf-8") as file:
        return json.load(file)


def build_variant_level_dataframe(api_response: dict) -> pd.DataFrame:
    """
    Builds a variant-level DataFrame by combining API metrics
    with extracted video features.

    Each row represents one video variant inside an A/B experiment.

    Args:
        api_response (dict): Parsed API response containing experiments.

    Returns:
        pd.DataFrame: One row per variant with metrics and video features.
    """
    rows = []

    experiments = api_response.get("experiments", [])

    for experiment in experiments:
        experiment_id = experiment.get("experiment_id")
        campaign_name = experiment.get("campaign_name")
        platform = experiment.get("platform")

        variants = [
            ("A", experiment.get("variant_a")),
            ("B", experiment.get("variant_b")),
        ]

        for variant_label, variant_data in variants:
            if not variant_data:
                continue

            creative_id = variant_data.get("creative_id")
            creative_name = variant_data.get("creative_name")
            video_url = variant_data.get("video_url")
            metrics = variant_data.get("metrics", {})

            local_video_path = fetch_video(video_url)
            video_features = extract_video_features(local_video_path)

            row = {
                "experiment_id": experiment_id,
                "campaign_name": campaign_name,
                "platform": platform,
                "variant_label": variant_label,
                "creative_id": creative_id,
                "creative_name": creative_name,
                "video_url": video_url,
                "local_video_path": local_video_path,
                "ctr": metrics.get("ctr"),
                "watch_time": metrics.get("watch_time"),
                "conversions": metrics.get("conversions"),
                "impressions": metrics.get("impressions"),
                "clicks": metrics.get("clicks"),
                "duration_sec": video_features.get("duration_sec"),
                "estimated_cut_count": video_features.get("estimated_cut_count"),
                "avg_frame_change": video_features.get("avg_frame_change"),
                "avg_brightness": video_features.get("avg_brightness"),
                "avg_saturation": video_features.get("avg_saturation"),
            }

            rows.append(row)

    return pd.DataFrame(rows)


def run_analysis(json_path: str) -> pd.DataFrame:
    """
    Loads the API response and returns the variant-level analysis table.

    Args:
        json_path (str): Path to the sample API response JSON.

    Returns:
        pd.DataFrame: Variant-level analysis DataFrame.
    """
    api_response = load_api_response(json_path)
    variant_df = build_variant_level_dataframe(api_response)
    return variant_df
