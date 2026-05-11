"""
Journey Builder Module
======================
Transforms raw lead-status records into ordered journey paths
suitable for Markov chain modelling.

Each path follows the format:
    Start → Channel → Stage₁ → Stage₂ → ... → Conversion / Null

Where:
- "Start" is a universal entry node
- "Conversion" = Opportunity Won (absorbing state)
- "Null" = drop-off at any stage (absorbing state)
"""

import pandas as pd


def build_journey_paths(
    df: pd.DataFrame,
    conversion_stage: str = "Opportunity Won",
    lead_col: str = "Lead_ID",
    status_col: str = "Lead_Status",
    channel_col: str = "Channel",
    timestamp_col: str = "Timestamp_Status",
) -> pd.DataFrame:
    """
    Build journey paths from raw lead records.

    Parameters
    ----------
    df : pd.DataFrame
        Raw journey data with one row per lead-status event.
    conversion_stage : str
        The stage name that counts as a conversion.
    lead_col, status_col, channel_col, timestamp_col : str
        Column name overrides.

    Returns
    -------
    pd.DataFrame
        One row per lead with columns:
        Lead_ID, Channel, Converted, Num_Stages, Path, Path_List
    """
    journeys = []

    for lead_id, group in df.groupby(lead_col):
        group = group.sort_values(timestamp_col)
        channel = group[channel_col].iloc[0]
        stages = group[status_col].tolist()
        converted = conversion_stage in stages

        # Build path: Start → Channel → Stages → Outcome
        path_elements = ["Start", channel] + stages
        path_elements.append("Conversion" if converted else "Null")

        journeys.append({
            lead_col: lead_id,
            "Channel": channel,
            "Converted": converted,
            "Num_Stages": len(stages),
            "Path": " → ".join(path_elements),
            "Path_List": path_elements,
        })

    return pd.DataFrame(journeys)


def get_conversion_rate(journeys_df: pd.DataFrame) -> float:
    """Calculate overall conversion rate from journey paths."""
    return journeys_df["Converted"].mean()


def get_channel_conversion_rates(journeys_df: pd.DataFrame) -> pd.DataFrame:
    """Calculate conversion rate per channel."""
    rates = (
        journeys_df.groupby("Channel")["Converted"]
        .agg(["sum", "count", "mean"])
        .rename(columns={"sum": "conversions", "count": "total_leads", "mean": "conversion_rate"})
        .sort_values("conversion_rate", ascending=False)
        .reset_index()
    )
    return rates
