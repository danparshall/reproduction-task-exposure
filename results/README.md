# Classification Results

This directory contains CDR classification results from production runs. Each subdirectory is labeled as `data_YYYYMMDD_<tier>` indicating when the run was performed and which model tier was used.

## Available Datasets

### `data_20260313_midtier/`

Full 923-occupation production run using **mid-tier** models with two-round consensus.

| Field | Value |
|-------|-------|
| **Date** | 2026-03-13 |
| **Model tier** | Mid-tier |
| **Models** | Claude Sonnet 4.6, GPT-5-mini, Gemini 3 Flash |
| **Occupations** | 923 (all O*NET SOCs) |
| **Tasks** | 18,796 |
| **Prompt versions** | C-v2, D-v4.1, R-v8 |
| **Reasoning format** | Per-axis |

**Files:**
- `consensus_cr.csv` — Final consensus classifications after both rounds (i-round + c-round). Each row is one task-DWA pair with per-model ratings, consensus values, and resolution method (unanimous, majority, or disputed).
- `disputed_cr.csv` — Tasks with unresolved 3-way splits after both rounds.
- `run_metadata.json` — Machine-readable run parameters.

## CSV Column Reference

The consensus CSV columns follow this pattern:

```
task_id,
{model}_C, {model}_C_ir,     # Model's C rating (final, ir = initial round original)
{model}_D, {model}_D_ir,     # Same for D axis
{model}_R, {model}_R_ir,     # Same for R axis
consensus_C, consensus_C_method,   # Final consensus + how it was reached
consensus_D, consensus_D_method,
consensus_R, consensus_R_method,
dispute_axes                  # Which axes (if any) remain disputed
```

**Consensus methods:**
- `unanimous` — All 3 models agreed in the initial round (i-round)
- `majority` — 2/3 models agreed (majority vote)
- Consensus methods are `unanimous` or `majority` regardless of which round resolved them
- Empty `consensus_*` + listed in `dispute_axes` — Unresolved 3-way split

## Reproducing These Results

To reproduce this dataset:

```bash
# Initial round (i-round): Independent classification
python scripts/classify.py --soc-set full

# Consensus round (c-round): Resolve disputes
python scripts/classify.py --soc-set full --round consensus
```

Results will appear in `output/results/`. Compare your `consensus.csv` against the provided dataset. Due to LLM non-determinism, exact reproduction is unlikely, but aggregate distributions should be similar.
