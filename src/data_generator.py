"""
Data Generator Module
=====================
Generates synthetic B2B SaaS marketing funnel data mimicking
Marketo → Salesforce lead journeys.

Each lead is assigned an entry channel, then progresses through funnel
stages with:
- Realistic drop-off at each stage (transition probabilities)
- Stage skipping (not every lead attends a webinar or downloads a whitepaper)
- Channel boost (e.g., Referral leads convert better than Display Ads leads)
"""

import numpy as np
import pandas as pd
import random
from datetime import datetime, timedelta


# ──────────────────────────────────────────────
# Default Configuration
# ──────────────────────────────────────────────

DEFAULT_FUNNEL_STAGES = [
    "Website Visit",
    "Filled Form",
    "Downloaded Whitepaper",
    "Content Syndication",
    "Attended Webinar",
    "Email Engaged",
    "Demo Requested",
    "Marketing Qualified Lead (MQL)",
    "Sales Accepted Lead (SAL)",
    "Sales Qualified Lead (SQL)",
    "Opportunity Won",
]

DEFAULT_CHANNELS = [
    "Organic Search", "Paid Search", "LinkedIn Ads", "Facebook Ads",
    "Display Ads", "Email Campaign", "Referral", "Webinar Promotion",
    "Content Syndication", "Direct Traffic",
]

DEFAULT_CHANNEL_WEIGHTS = [
    0.18, 0.15, 0.12, 0.10, 0.08,
    0.12, 0.08, 0.07, 0.05, 0.05,
]

DEFAULT_STAGE_TRANSITION_PROBS = [
    0.65, 0.50, 0.45, 0.40, 0.55,
    0.35, 0.60, 0.70, 0.65, 0.50,
]

DEFAULT_SKIP_PROBS = [
    0.0, 0.0, 0.30, 0.35, 0.25,
    0.10, 0.0, 0.0, 0.0, 0.0,
]

DEFAULT_CHANNEL_BOOST = {
    "Referral": 1.25,
    "Webinar Promotion": 1.15,
    "Organic Search": 1.10,
    "Direct Traffic": 1.05,
    "Email Campaign": 1.08,
    "Paid Search": 1.00,
    "LinkedIn Ads": 0.95,
    "Content Syndication": 0.90,
    "Facebook Ads": 0.85,
    "Display Ads": 0.75,
}


# ──────────────────────────────────────────────
# Journey Generator
# ──────────────────────────────────────────────

def generate_lead_journey(
    lead_id: int,
    start_date: datetime,
    funnel_stages: list = None,
    channels: list = None,
    channel_weights: list = None,
    transition_probs: list = None,
    skip_probs: list = None,
    channel_boost: dict = None,
) -> list:
    """
    Generate a single lead's journey through the marketing funnel.

    Parameters
    ----------
    lead_id : int
        Unique lead identifier.
    start_date : datetime
        Simulation start date.
    funnel_stages : list, optional
        Ordered funnel stages. Uses defaults if None.
    channels, channel_weights, transition_probs, skip_probs, channel_boost :
        Configuration parameters. All use defaults if None.

    Returns
    -------
    list
        List of dicts with Lead_ID, Lead_Status, Channel, Timestamp_Status.
    """
    if funnel_stages is None:
        funnel_stages = DEFAULT_FUNNEL_STAGES
    if channels is None:
        channels = DEFAULT_CHANNELS
    if channel_weights is None:
        channel_weights = DEFAULT_CHANNEL_WEIGHTS
    if transition_probs is None:
        transition_probs = DEFAULT_STAGE_TRANSITION_PROBS
    if skip_probs is None:
        skip_probs = DEFAULT_SKIP_PROBS
    if channel_boost is None:
        channel_boost = DEFAULT_CHANNEL_BOOST

    channel = np.random.choice(channels, p=channel_weights)
    boost = channel_boost.get(channel, 1.0)
    records = []
    current_time = start_date + timedelta(days=random.uniform(0, 365))

    for stage_idx, stage in enumerate(funnel_stages):
        # Check if lead skips this stage
        if skip_probs[stage_idx] > 0 and random.random() < skip_probs[stage_idx]:
            continue

        # Check if lead progresses (after first stage)
        if stage_idx > 0:
            base_prob = transition_probs[stage_idx - 1]
            adjusted_prob = min(base_prob * boost, 0.95)
            if random.random() > adjusted_prob:
                break  # Lead drops off

        records.append({
            "Lead_ID": f"LEAD-{lead_id:05d}",
            "Lead_Status": stage,
            "Channel": channel,
            "Timestamp_Status": current_time,
        })

        # Advance time between stages
        current_time += timedelta(
            days=random.uniform(1, 14),
            hours=random.uniform(0, 23),
        )

    return records


def generate_dataset(
    num_leads: int = 5000,
    start_date: datetime = datetime(2024, 1, 1),
    seed: int = 42,
    **kwargs,
) -> pd.DataFrame:
    """
    Generate the full synthetic lead journey dataset.

    Parameters
    ----------
    num_leads : int
        Number of leads to simulate.
    start_date : datetime
        Simulation start date.
    seed : int
        Random seed for reproducibility.
    **kwargs :
        Passed to generate_lead_journey.

    Returns
    -------
    pd.DataFrame
        Complete journey dataset with columns:
        Lead_ID, Lead_Status, Channel, Timestamp_Status
    """
    np.random.seed(seed)
    random.seed(seed)

    all_records = []
    for i in range(num_leads):
        journey = generate_lead_journey(i, start_date, **kwargs)
        all_records.extend(journey)

    df = pd.DataFrame(all_records)
    df["Timestamp_Status"] = pd.to_datetime(df["Timestamp_Status"])
    return df.sort_values(["Lead_ID", "Timestamp_Status"]).reset_index(drop=True)
