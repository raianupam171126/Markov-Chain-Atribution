# 🔗 Markov Chain Marketing Attribution Model

**Multi-touch attribution using absorbing Markov chains and removal effects — quantifying each marketing channel's true structural importance in driving conversions across a B2B SaaS funnel.**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![Status](https://img.shields.io/badge/Status-Complete-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## Business Problem

A B2B SaaS company runs campaigns across 10+ marketing channels (Organic Search, Paid Search, LinkedIn, Webinars, Referrals, etc.). Leads flow through a 10-stage funnel — from Website Visit to Opportunity Won — touching multiple channels along the way.

**The attribution challenge:** Traditional heuristic models (First Touch, Last Touch, Linear) assign credit using simplistic rules that ignore the sequential, probabilistic nature of the customer journey. This leads to:

- **Over-investment** in channels that happen to be first or last (but aren't structurally important)
- **Under-investment** in mid-funnel channels that nurture and accelerate leads
- **No visibility** into which channel removal would most damage the conversion rate

**The Markov Chain approach** treats the entire journey as a stochastic process and answers: *"If we removed channel X entirely, how much would our conversion rate drop?"* — giving a mathematically grounded, data-driven attribution.

---

## Pipeline Overview

```
Step 0:   Environment Setup
Step 1:   Configuration (funnel stages, channels, transition probabilities)
Step 2:   Synthetic Dataset Generation (5,000 leads, realistic B2B funnel)
Step 3:   Build Journey Paths (Start → Channel → Stages → Conversion/Null)
Step 4:   Build Transition Probability Matrix
Step 5:   Absorbing Markov Chain — Compute Base Conversion Probability
Step 6:   Removal Effect Attribution (core Markov attribution)
Step 7:   Heuristic Model Comparison (First Touch, Last Touch, Linear)
Step 8:   Funnel Transition Analysis (stage-to-stage conversion rates)
Step 9:   Channel Depth vs Conversion Rate (bubble chart analysis)
Step 10:  Save All Results (JSON export)
Step 11:  Final Summary & Key Insights
```

---

## Data

| Detail | Value |
|:---|:---|
| Leads | 5,000 simulated B2B SaaS leads |
| Funnel Stages | 10 stages (Website Visit → Opportunity Won) |
| Channels | 10 marketing channels |
| Data Type | Synthetic with realistic transition probabilities, drop-off rates, and channel boost effects |

### Funnel Stages

```
Website Visit → Filled Form → Downloaded Whitepaper → Content Syndication →
Attended Webinar → Email Engaged → Demo Requested → MQL → SAL → SQL → Opportunity Won
```

### Channels

Organic Search, Paid Search, LinkedIn Ads, Facebook Ads, Display Ads, Email Campaign, Referral, Webinar Promotion, Content Syndication, Direct Traffic

---

## Key Techniques

### Absorbing Markov Chain Theory

The customer journey is modelled as a Markov chain with two types of states:

- **Transient states** — channels and funnel stages (leads move between these)
- **Absorbing states** — Conversion (Opportunity Won) and Null (drop-off)

From the transition matrix, we compute:

```
Q = transient-to-transient sub-matrix
R = transient-to-absorbing sub-matrix
N = (I - Q)⁻¹                          ← Fundamental matrix
B = N × R                               ← Absorption probabilities
```

`B[Start, Conversion]` gives the base conversion probability.

### Removal Effect Attribution

For each channel C:
1. **Remove** C from the chain (redirect all traffic through C → Null)
2. **Recalculate** conversion probability without C
3. **Removal Effect** = `(base_prob - removed_prob) / base_prob`
4. **Normalize** all removal effects → attribution weights

A higher removal effect means removing that channel causes a larger drop in conversions — proving its structural importance.

### Heuristic Comparison Models

Three simpler models computed for benchmarking:

| Model | Logic | Weakness |
|:---|:---|:---|
| First Touch | 100% credit to entry channel | Ignores mid-funnel influence |
| Last Touch | 100% credit to last touchpoint | Ignores awareness channels |
| Linear | Equal credit across all touchpoints | Assumes all touches equally important |

---

## Results Summary

### Markov Attribution vs Heuristic Models

The notebook produces a side-by-side grouped bar chart comparing all four models across channels, revealing how heuristic models systematically misattribute credit.

### Funnel Transition Analysis

Stage-to-stage conversion rates are color-coded by health:
- 🟢 **>70%** — strong progression
- 🟡 **45–70%** — moderate (optimization opportunity)
- 🔴 **<45%** — weak (needs intervention)

### Channel Depth vs Conversion Rate

Bubble chart showing how deep each channel pushes leads into the funnel, correlated with conversion rate. Bubble size represents lead volume — revealing which channels drive both depth and volume.

### Visualizations

The notebook includes 10+ publication-quality charts:
- Funnel drop-off bar chart
- Transition probability heatmap
- Markov attribution weight horizontal bars
- 4-model comparison grouped bar chart
- Funnel waterfall chart (stage-to-stage rates)
- Channel depth vs conversion bubble chart

---

## Project Structure

```
markov-chain-attribution/
│
├── data/
│   ├── raw/                          # Raw synthetic journey data
│   └── processed/                    # Transition matrices & attribution results
│
├── notebooks/
│   └── Markov_Chain_Marketing_Attribution.ipynb   # Full 11-step pipeline
│
├── src/
│   ├── __init__.py
│   ├── data_generator.py             # Synthetic B2B funnel data generation
│   ├── journey_builder.py            # Journey path construction from raw records
│   ├── markov_model.py               # Transition matrix, absorbing chain, removal effects
│   └── heuristic_models.py           # First Touch, Last Touch, Linear attribution
│
├── outputs/                          # Saved charts and JSON results
├── requirements.txt
├── README.md
└── LICENSE
```

---

## How to Run

```bash
# Clone the repository
git clone https://github.com/raianupam171126/markov-chain-attribution.git
cd markov-chain-attribution

# Create virtual environment
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Launch the notebook
jupyter notebook notebooks/Markov_Chain_Marketing_Attribution.ipynb
```

**Google Colab:**

[![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/raianupam171126/markov-chain-attribution/blob/main/notebooks/Markov_Chain_Marketing_Attribution.ipynb)

---

## Tech Stack

- **Python 3.10** — pandas, NumPy
- **Linear Algebra** — NumPy (matrix inversion for fundamental matrix computation)
- **Visualization** — Matplotlib, Seaborn
- **Data Structures** — collections.defaultdict for transition counting

---

## Limitations & Future Work

- **Synthetic data** — results are illustrative; real-world implementation requires actual CRM journey data (Marketo/HubSpot activity logs + Salesforce opportunities)
- **First-order Markov** — current model assumes transitions depend only on the current state; higher-order Markov chains could capture longer memory effects
- **Time-independent** — transition probabilities are static; time-decay weighting could improve accuracy for long sales cycles
- **No channel interaction** — channels are treated independently; Shapley value attribution could capture cooperative effects
- **Scalability** — matrix inversion is O(n³); for very large state spaces, simulation-based approaches may be more efficient

---

## References

- Anderl, E., Becker, I., von Wangenheim, F., Schumann, J.H. (2016). *Mapping the Customer Journey: Lessons Learned from Graph-Based Online Attribution Modeling*
- Shao, X., Li, L. (2011). *Data-Driven Multi-Touch Attribution Models*
- ChannelAttribution R package — Markov chain attribution implementation
- Google Analytics Attribution — First Touch, Last Touch, Linear models

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## Connect

[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat&logo=linkedin&logoColor=white)](https://linkedin.com/in/YOUR-PROFILE)
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat&logo=github&logoColor=white)](https://github.com/raianupam171126)
