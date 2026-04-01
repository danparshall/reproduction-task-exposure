# Conversation: Oldest-Available Model Stability Testing

**Date:** 2026-03-27 to 2026-04-01
**Participants:** Dan Parshall, Claude (Opus 4.6)
**Repo:** reproduction-task-exposure (CDR framework reproduction package)

## Goal

Test whether the CDR classification framework produces stable results when run with older, non-frontier mid-tier models — and document what happens when you try to reproduce with models from different eras. The key question is temporal drift: how much do classifications change across model generations, and is the drift structured or random?

## What we tried

### Early 2024 mid-tier models (all failed)

| Provider | Model | Result |
|----------|-------|--------|
| Anthropic | `claude-3-sonnet-20240229` | 404 — sunset |
| OpenAI | `gpt-3.5-turbo-0125` | Max output 4096 tokens; max context 16K. System prompt alone is ~9.4K tokens, leaving ~2.9K for user prompt after output reservation. Framework requires ~32K+ context. |
| Google | `gemini-1.0-pro` | 404 — sunset |

### Early 2025 mid-tier models (mostly failed)

| Provider | Model | Result |
|----------|-------|--------|
| Anthropic | `claude-3-5-sonnet-20241022` | 404 — sunset |
| OpenAI | `gpt-4o-mini` | Works |
| Google | `gemini-2.0-flash` | 404 — sunset for new users as of 2026-03-06 |

### "Oldest available" tier (what actually ran)

| Provider | Model | Approx. release | Result |
|----------|-------|-----------------|--------|
| Anthropic | `claude-sonnet-4-20250514` | May 2025 | Works |
| OpenAI | `gpt-4o-mini` | Jul 2024 | Works, but R-axis broken in R1 |
| Google | `gemini-2.5-flash` | Early 2025 | Works with `--max-tokens 32768` |

## Key findings

### 1. The reproducibility window is ~12 months

API model sunsetting creates a hard wall. Only OpenAI maintains older model versions; Anthropic and Google sunset aggressively — everything before mid-2025 is gone from both providers as of March 2026. Even where a model survives (GPT-3.5-turbo), context window limitations may make it architecturally incompatible.

This means any LLM-based classification framework faces a choice: either pin to specific model versions (which will eventually disappear) or demonstrate that results are stable across model generations (which requires measuring temporal drift). We chose the latter.

### 2. Full-scale temporal drift (923 occupations, ~23,800 tasks)

Comparing post-c-round consensus between the oldest available tier and current mid-tier (`compare_results.py` output):

**Task-level agreement:**

| Axis | Exact match | Off-by-1 | Off-by-2+ |
|------|-------------|----------|-----------|
| C | 78.5% | 21.0% | 0.4% |
| D | 84.2% | 11.9% | 3.9% |
| R | 70.1% | 17.3% | 12.6% |
| **Overall** | **77.6%** | | |
| **Within 1 level** | | | **94.4%** |

C and D show near-zero systematic bias between generations. R has the most drift, driven by GPT-4o-mini's R0 tendency.

**Distribution stability:**

| Level | C delta | D delta | R delta |
|-------|---------|---------|---------|
| 0 | +0.2% | +2.1% | -7.5% |
| 1 | -3.3% | -4.1% | -9.0% |
| 2 | +4.5% | -0.8% | +13.0% |
| 3 | -1.6% | +2.8% | +3.4% |
| 4 | +0.2% | +0.1% | -0.0% |

C and D distributions shift <5 percentage points per level. R shifts more (R2 is +13%) because GPT-4o-mini overcorrects in the c-round.

### 3. Stability varies by rating level and occupation

**Extremes are stable, boundaries drift** (from 12-occupation analysis):
- R0 (94% stable), D0 (95%), D4 (100%) — clear cases, all generations agree
- R1 (50%), R2 (30%), C0 (40%) — boundary categories are fragile
- Drift is directional at boundaries, not random

**Per-occupation** (12-occupation subset):
- Software Developers (92% exact), Customer Service (94%) — rock-solid
- Accountants (58%), Teachers (71%) — most ambiguous regulatory/complexity boundaries

### 4. GPT-4o-mini's R-axis failure and c-round recovery

**R1:** GPT-4o-mini rates R=0 on ~95% of tasks with template reasoning ("No regulatory barriers") — even for cosmetology-licensed hairdressers, EPA-certified HVAC, and nurse practice acts. It's not engaging with the regulatory data in the prompt.

**R2 (c-round):** When shown other models' reasoning, GPT-4o-mini reversed ~86% of its R-axis ratings (pilot set). Reasoning became substantive — citing specific statutes. It *can* reason about regulation; it doesn't invest the effort independently.

**Contrast with o1 (pilot only):** o1 changed zero R-axis ratings in its c-round — held every position. Better in R1 (32.4% R0 vs 95.3%) but won't update. Two failure modes:
- **4o-mini**: follower — doesn't think independently, capitulates in c-round
- **o1**: stubborn — thinks independently, won't update

### 5. Consensus protocol is robust

Post-c-round consensus rates on the full 923-occupation set:

| Metric | Value |
|--------|-------|
| Per-axis consensus (2-of-3) | **98.2%** |
| Disputed (3-way splits) | 1.8% |

The two-round protocol handles both failure modes effectively. Even with one weak model (4o-mini R-axis), the final consensus converges.

### 6. CDR framework requires ~32K+ context windows

System prompt ~9.4K tokens + user prompts with full O*NET enrichment (profile, abilities, work context, DWA-decomposed tasks) 5-10K tokens + output reservation. GPT-3.5-turbo's 16K context is fundamentally incompatible. This became standard in mid-tier models around late 2024.

## Code changes

1. **`scripts/classify.py`:**
   - Added `early2024`, `oldest`, and `oldest_o1` model tiers to `MODEL_TIERS`
   - Updated `.env` loading to check `.env.local` first (`.env.local` → `.env` fallback)
   - Added `None` guard for Gemini empty responses (line 257)
2. **`scripts/aggregate.py`** — new script. Merges R1+R2 checkpoints into `consensus_r2.csv` / `disputed_r2.csv`
3. **`README.md`** — updated with:
   - Four-step reproduction workflow (classify R1 → classify R2 → aggregate → compare)
   - Model tiers table
   - Temporal stability findings
   - R-axis sensitivity documentation
   - Model sunsetting as reproducibility constraint
   - Gemini thinking-token workaround
   - Updated repo structure

## Data produced and committed

**Committed to `results/`:**
- `results/data_oldest_available/consensus_r2.csv` — final consensus ratings (23,421 resolved tasks)
- `results/data_oldest_available/disputed_r2.csv` — remaining 3-way disputes (425 tasks)
- `results/data_oldest_available/run_metadata.json` — models used, notes on quirks

**In `data/checkpoints_*` (gitignored):**
- `data/checkpoints_oldest_expanded/` — R1 checkpoints (923 SOCs x 3 models)
- `data/checkpoints_oldest_expanded_r2/` — R2 checkpoints
- `data/checkpoints_oldest/` — pilot set checkpoints
- `data/checkpoints_oldest_o1/` — o1 pilot comparison

**In `output/` (gitignored):**
- `output/results_oldest_full/` — full output including R1-only CSVs
- `output/results_oldest/` — pilot output with NOTES.md
- Various partial/intermediate outputs from early experiments

## Open questions for the paper

1. **Is the R-axis drift a GPT-4o-mini problem or a structural issue?** The c-round corrects it, but the overcorrection (R2 at +13%) suggests the c-round may be anchoring too strongly on the other models' reasoning rather than doing independent analysis.
2. **Should minimum model requirements be stated?** Context window ≥32K, ability to integrate domain-specific context from prompts. This effectively excludes pre-2024 models.
3. **How to frame the sunsetting finding?** It's a general problem for all LLM-based research, not specific to CDR. But CDR's multi-provider design makes it especially visible — you need 3 providers' models to all be available simultaneously.
