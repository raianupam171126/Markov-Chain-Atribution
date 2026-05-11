"""
Heuristic Attribution Models
=============================
Implements three traditional attribution models for benchmarking
against the Markov chain approach.

Models:
- First Touch: 100% credit to the entry channel
- Last Touch:  100% credit to the last touchpoint before conversion
- Linear:      Equal credit across all touchpoints in the path
"""

import pandas as pd
from collections import defaultdict


def compute_heuristic_models(
    journeys_df: pd.DataFrame,
    channels: list,
) -> dict:
    """
    Compute First Touch, Last Touch, and Linear attribution.

    Parameters
    ----------
    journeys_df : pd.DataFrame
        Journey paths DataFrame (must have 'Converted', 'Channel', 'Path_List').
    channels : list
        List of channel names.

    Returns
    -------
    dict
        Per-channel results:
        {channel: {first_touch, last_touch, linear}} (as fractions summing to 1)
    """
    converted_df = journeys_df[journeys_df["Converted"]]
    total_conversions = len(converted_df)

    if total_conversions == 0:
        return {ch: {"first_touch": 0, "last_touch": 0, "linear": 0} for ch in channels}

    first_touch = defaultdict(float)
    last_touch = defaultdict(float)
    linear = defaultdict(float)

    for _, row in converted_df.iterrows():
        channel = row["Channel"]

        # First Touch: 100% to entry channel
        first_touch[channel] += 1.0

        # Last Touch: 100% to entry channel
        # (in this funnel design, channel is the entry — but the last *touchpoint*
        # before conversion is the last funnel stage. Since we attribute to channels,
        # and each journey has one channel, last-touch also goes to that channel.)
        last_touch[channel] += 1.0

        # Linear: equal credit across all path elements that are channels
        path = row["Path_List"]
        channel_touches = [p for p in path if p in channels]
        if channel_touches:
            credit = 1.0 / len(channel_touches)
            for ch in channel_touches:
                linear[ch] += credit

    # Normalize to fractions
    results = {}
    for ch in channels:
        results[ch] = {
            "first_touch": first_touch.get(ch, 0) / total_conversions,
            "last_touch": last_touch.get(ch, 0) / total_conversions,
            "linear": linear.get(ch, 0) / total_conversions,
        }

    return results


def compare_all_models(
    markov_results: dict,
    heuristic_results: dict,
    channels: list,
) -> pd.DataFrame:
    """
    Create a comparison DataFrame of all attribution models.

    Parameters
    ----------
    markov_results : dict
        Output from compute_removal_effects.
    heuristic_results : dict
        Output from compute_heuristic_models.
    channels : list
        List of channel names.

    Returns
    -------
    pd.DataFrame
        Comparison table with columns:
        Channel, Markov, First_Touch, Last_Touch, Linear
    """
    rows = []
    for ch in channels:
        rows.append({
            "Channel": ch,
            "Markov": markov_results.get(ch, {}).get("attribution_weight", 0) * 100,
            "First_Touch": heuristic_results.get(ch, {}).get("first_touch", 0) * 100,
            "Last_Touch": heuristic_results.get(ch, {}).get("last_touch", 0) * 100,
            "Linear": heuristic_results.get(ch, {}).get("linear", 0) * 100,
        })

    return pd.DataFrame(rows).sort_values("Markov", ascending=False).reset_index(drop=True)
