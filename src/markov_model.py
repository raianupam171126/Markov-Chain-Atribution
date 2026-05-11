"""
Markov Model Module
===================
Core attribution engine using absorbing Markov chain theory.

Pipeline:
    1. Count state-to-state transitions across all journeys
    2. Normalize to transition probability matrix
    3. Identify transient vs absorbing states
    4. Compute fundamental matrix N = (I - Q)⁻¹
    5. Compute absorption probabilities B = N × R
    6. For each channel, compute removal effect → attribution weight

Key Concepts:
    - Q: transient-to-transient sub-matrix
    - R: transient-to-absorbing sub-matrix
    - N = (I - Q)⁻¹: fundamental matrix (expected visits to each transient state)
    - B = N × R: absorption probability matrix
    - Removal effect: fractional drop in conversion when a channel is removed
"""

import numpy as np
import pandas as pd
from collections import defaultdict


# ──────────────────────────────────────────────
# Transition Matrix
# ──────────────────────────────────────────────

def build_transition_matrix(journeys_df: pd.DataFrame) -> tuple:
    """
    Build the transition probability matrix from journey paths.

    Parameters
    ----------
    journeys_df : pd.DataFrame
        Journey paths with 'Path_List' column.

    Returns
    -------
    tuple
        (transition_matrix, all_states)
        - transition_matrix: dict of dict with probabilities
        - all_states: sorted list of all state names
    """
    transition_counts = defaultdict(lambda: defaultdict(int))
    all_states = set()

    for _, row in journeys_df.iterrows():
        path = row["Path_List"]
        for i in range(len(path) - 1):
            from_state = path[i]
            to_state = path[i + 1]
            transition_counts[from_state][to_state] += 1
            all_states.add(from_state)
            all_states.add(to_state)

    # Normalize counts to probabilities
    transition_matrix = {}
    for from_state, transitions in transition_counts.items():
        total = sum(transitions.values())
        transition_matrix[from_state] = {
            to_state: count / total
            for to_state, count in transitions.items()
        }

    return transition_matrix, sorted(all_states)


def transition_matrix_to_dataframe(
    transition_matrix: dict, states: list
) -> pd.DataFrame:
    """Convert transition matrix dict to a pandas DataFrame for display."""
    matrix = np.zeros((len(states), len(states)))
    for i, from_s in enumerate(states):
        if from_s in transition_matrix:
            for j, to_s in enumerate(states):
                matrix[i, j] = transition_matrix[from_s].get(to_s, 0.0)
    return pd.DataFrame(matrix, index=states, columns=states)


# ──────────────────────────────────────────────
# Absorbing Markov Chain
# ──────────────────────────────────────────────

def calculate_conversion_probability(
    trans_matrix: dict,
    states: list,
    removed_channel: str = None,
    absorbing_states: tuple = ("Conversion", "Null"),
) -> float:
    """
    Calculate conversion probability using absorbing Markov chain theory.

    If removed_channel is specified, all transitions through that channel
    are redirected to "Null" (simulating channel removal).

    Parameters
    ----------
    trans_matrix : dict
        Transition probability matrix (dict of dict).
    states : list
        All state names.
    removed_channel : str, optional
        Channel to remove for removal-effect calculation.
    absorbing_states : tuple
        Names of absorbing states.

    Returns
    -------
    float
        Probability of reaching "Conversion" from "Start".
    """
    # Deep copy and optionally remove a channel
    matrix = {}
    for from_s, transitions in trans_matrix.items():
        if removed_channel and from_s == removed_channel:
            # Redirect all traffic through this channel → Null
            matrix[from_s] = {"Null": 1.0}
        else:
            matrix[from_s] = dict(transitions)

    # Classify states
    transient = [s for s in states if s not in absorbing_states]
    absorbing = [s for s in states if s in absorbing_states]

    n_t = len(transient)
    n_a = len(absorbing)
    t_idx = {s: i for i, s in enumerate(transient)}
    a_idx = {s: i for i, s in enumerate(absorbing)}

    # Build Q (transient → transient) and R (transient → absorbing)
    Q = np.zeros((n_t, n_t))
    R = np.zeros((n_t, n_a))

    for from_s in transient:
        if from_s not in matrix:
            continue
        for to_s, prob in matrix[from_s].items():
            if to_s in t_idx:
                Q[t_idx[from_s], t_idx[to_s]] = prob
            elif to_s in a_idx:
                R[t_idx[from_s], a_idx[to_s]] = prob

    # Fundamental matrix N = (I - Q)⁻¹
    try:
        N = np.linalg.inv(np.eye(n_t) - Q)
    except np.linalg.LinAlgError:
        return 0.0

    # Absorption probabilities B = N × R
    B = N @ R

    # Return P(Start → Conversion)
    if "Start" in t_idx and "Conversion" in a_idx:
        return B[t_idx["Start"], a_idx["Conversion"]]
    return 0.0


# ──────────────────────────────────────────────
# Removal Effect Attribution
# ──────────────────────────────────────────────

def compute_removal_effects(
    trans_matrix: dict,
    states: list,
    channels: list,
) -> dict:
    """
    Compute Markov chain removal-effect attribution for all channels.

    For each channel:
    1. Remove it from the chain (redirect to Null)
    2. Recalculate conversion probability
    3. Removal effect = (base - removed) / base
    4. Normalize to attribution weights

    Parameters
    ----------
    trans_matrix : dict
        Transition probability matrix.
    states : list
        All state names.
    channels : list
        List of channel names to evaluate.

    Returns
    -------
    dict
        Per-channel results with keys:
        removal_effect, removed_conversion_prob, attribution_weight
    """
    base_prob = calculate_conversion_probability(trans_matrix, states)

    removal_effects = {}
    for channel in channels:
        removed_prob = calculate_conversion_probability(
            trans_matrix, states, removed_channel=channel
        )
        effect = (base_prob - removed_prob) / base_prob if base_prob > 0 else 0
        removal_effects[channel] = {
            "removal_effect": effect,
            "removed_conversion_prob": removed_prob,
        }

    # Normalize to attribution weights
    total_effect = sum(
        max(0, v["removal_effect"]) for v in removal_effects.values()
    )

    for channel in removal_effects:
        raw = max(0, removal_effects[channel]["removal_effect"])
        removal_effects[channel]["attribution_weight"] = (
            raw / total_effect if total_effect > 0 else 0
        )

    return removal_effects, base_prob


# ──────────────────────────────────────────────
# Funnel Analysis
# ──────────────────────────────────────────────

def compute_funnel_transition_rates(
    df: pd.DataFrame,
    funnel_stages: list,
    lead_col: str = "Lead_ID",
    status_col: str = "Lead_Status",
) -> dict:
    """
    Compute stage-to-stage conversion rates in the funnel.

    Returns
    -------
    dict
        {transition_label: rate} for each consecutive stage pair.
    """
    stage_counts = {}
    for stage in funnel_stages:
        stage_counts[stage] = df[df[status_col] == stage][lead_col].nunique()

    rates = {}
    for i in range(len(funnel_stages) - 1):
        from_s = funnel_stages[i]
        to_s = funnel_stages[i + 1]
        rate = stage_counts[to_s] / stage_counts[from_s] if stage_counts[from_s] > 0 else 0
        rates[f"{from_s} → {to_s}"] = rate

    return rates
