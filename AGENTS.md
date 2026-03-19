# AGENTS.md — Instructions for AI Coding Assistants

This file explains how this repository works so that an AI agent (Claude Code, Cursor, Copilot, etc.) can help a researcher run the classification pipeline.

## What This Repo Does

This repo classifies ~18,800 occupational tasks from O*NET on three axes:

| Axis | Measures | Scale |
|------|----------|-------|
| **C** (Cognitive complexity) | Reasoning/judgment required | C0 (minimal) to C4 (frontier research) |
| **D** (Deployment difficulty) | Sensorimotor/physical requirements | D0 (pure digital) to D4 (extreme dexterity) |
| **R** (Regulatory restrictions) | Barriers to AI-assisted performance | R0 (none) to R3 (hard legal barriers) |

Each task is classified by three LLM providers (Anthropic, OpenAI, Google) independently. Disagreements are resolved through a structured consensus round where each model sees the others' reasoning.

The result is a task-level exposure map: for each of ~18,800 tasks across 923 occupations, we know how cognitively complex it is, how much physical capability it requires, and how much regulation constrains AI augmentation.

## Repository Structure

```
reproduction-task-exposure/
├── scripts/classify.py          # Main entry point — run this
├── src/task_exposure/           # Python package
│   ├── clients.py               #   API clients (Anthropic, OpenAI, Google)
│   ├── prompts.py               #   CDR axis definitions and prompt formatting
│   ├── runner.py                #   Checkpoint/resume, consensus, output
│   ├── parser.py                #   Response parser (pipe-delimited format)
│   └── profiles.py              #   Occupation profile loading
├── data/
│   ├── onet/                    #   Bundled O*NET database files (public domain)
│   ├── extracted/               #   Pre-built CSVs (tasks, profiles with licensing)
│   └── checkpoints/             #   Runtime checkpoint storage (gitignored)
├── results/                     #   Published classification results
│   └── data_YYYYMMDD_<tier>/    #   Labeled by date and model tier
└── output/                      #   User's own run results (gitignored)
```

## How to Help a Researcher

### Setup (first time)

1. Ensure Python 3.12+ is available
2. Create and activate a virtual environment:
   ```bash
   uv venv && source .venv/bin/activate && uv sync
   ```
   Or with pip:
   ```bash
   python -m venv .venv && source .venv/bin/activate && pip install -e .
   ```
3. Copy `.env.example` to `.env` and add API keys for all three providers:
   - `ANTHROPIC_API_KEY` — from https://console.anthropic.com/
   - `OPENAI_API_KEY` — from https://platform.openai.com/
   - `GEMINI_API_KEY` — from https://aistudio.google.com/

### Running Classification

The main script is `scripts/classify.py`. Key commands:

```bash
# Validate setup — dry run, no API calls:
python scripts/classify.py --dry-run

# Quick test — 3 occupations, ~$2:
python scripts/classify.py --soc-set pilot

# Standard test — 12 occupations, ~$10:
python scripts/classify.py --soc-set expanded

# Full reproduction — 923 occupations, ~$100:
python scripts/classify.py --soc-set full

# Round 2 consensus on disputed tasks:
python scripts/classify.py --soc-set full --round 2
```

### Checkpoint/Resume

The pipeline saves a checkpoint after each occupation completes. If a run is interrupted:
- Just re-run the same command — it skips completed SOCs automatically
- Use `--model gemini` to resume only one provider
- Checkpoints are in `data/checkpoints/{model_label}/soc_{SOC_CODE}.json`

### Understanding the Output

After a run, `output/results/` contains:
- `consensus.csv` — Tasks where models agreed (or majority ruled)
- `disputed.csv` — Tasks with 3-way splits (all models gave different values)
- `prompt_snapshot.json` — Exact prompt text + SHA-256 hash for reproducibility
- `system_prompt.txt` — The full system prompt sent to each model
- `run_metadata.json` — Run parameters (models, tier, SOC set, timestamp)

### Comparing with Published Results

Published results are in `results/data_YYYYMMDD_<tier>/`. To compare:
1. Run your own classification
2. Compare `output/results/consensus.csv` with the published `consensus_r2.csv`
3. Due to LLM non-determinism, expect ~85-95% agreement on individual ratings
4. Aggregate distributions (% at each C/D/R level) should be within a few percentage points

## Key Design Decisions

### Why DWA decomposition?
O*NET tasks often bundle cognitive and physical work: "Diagnose and repair heating systems." DWA decomposition splits this into separate classification units — the cognitive diagnosis (C2/D0) and the physical repair (C1/D3). Without decomposition, the model must guess how to weight the compound.

### Why 3-model consensus?
Single-model classification has ~10-15% noise. Provider identity (Anthropic vs OpenAI vs Google) dominates model tier in explaining disagreements, so we use one model per provider and resolve via majority vote.

### Why per-axis reasoning?
Each model provides separate reasoning for C, D, and R before giving ratings. This was validated through stability experiments: per-axis reasoning produces more consistent classifications than merged reasoning.

### Why two rounds?
Round 1 classifies independently. Round 2 shows each model the anonymized reasoning of the other models for disputed axes only. This resolves ~60-70% of initial disagreements.

## Common Issues

### Rate limits
All three providers run in parallel (independent rate limits). Gemini has the most restrictive limits:
- Gemini Flash: 1,000 RPM
- Gemini Pro: 25 RPM, ~250 RPD (requests per day)

If you hit rate limits, the retry logic handles per-minute limits automatically. Per-day limits (Gemini Pro) will raise `QuotaExhaustedError` — wait until midnight Pacific or switch to mid-tier.

### Temperature

**Temperature is not a useful lever for this pipeline.** The `--temperature` flag exists for experimentation, but the defaults are the settled production approach.

Per-provider behavior:
- **Anthropic (Sonnet/Opus)**: No default temperature set (uses provider default). T=0 does *not* produce deterministic output — two T=0 runs with identical prompts show ~87% rating agreement and <4% reasoning text identity. The ~11% disagreement is genuine model uncertainty at classification boundaries, not sampling noise.
- **OpenAI (GPT-5-mini)**: Reasoning model that rejects `temperature≠1`. The `is_reasoning` guard in `clients.py` silently skips temperature for these models. Non-reasoning OpenAI models get hardcoded T=0.
- **Gemini**: Temperature is silently dropped by `create_client()`. T=0 causes greedy-decoding verbosity that exhausts `max_output_tokens` via thinking tokens — at T=0, Gemini Flash completed only 4/12 occupations in testing.

### Truncated responses
Gemini's `max_output_tokens` budget includes internal thinking/reasoning tokens, not just the visible structured output. The structured response for the largest occupations needs ~4,200 visible tokens, but Gemini's internal reasoning can push total token usage well past 8,192. The default `--max-tokens 16384` provides safe headroom.

### Parse failures
A "PARSE FAILED" message means the model's response didn't match the expected pipe-delimited format. The pipeline continues and the occupation can be re-run with `--model <name>`.

## Module Reference

### `src/task_exposure/prompts.py`
The heart of the system. Contains:
- **Axis definitions** (C, D, R) with level descriptions, boundary tests, edge-case indicators
- **System prompt formatter** — composes axis definitions into a complete system prompt
- **User prompt formatter** — builds per-occupation prompts with contextual enrichment
- **DWA expansion** — splits compound tasks into task-DWA pairs

### `src/task_exposure/clients.py`
API clients for all three providers with:
- Retry logic with exponential backoff
- Truncation detection (raises `TruncatedResponseError`)
- Quota/billing error detection (raises `QuotaExhaustedError` / `BillingError`)
- Semaphore-based concurrency control

### `src/task_exposure/runner.py`
Pipeline infrastructure:
- `load_all_socs()` — loads the task CSV
- `save_checkpoint()` / `load_checkpoints()` — atomic per-SOC checkpoint files
- `get_remaining_work()` — determines which SOCs still need classification
- `build_consensus()` — majority-vote consensus across models
- `save_aggregated_results()` — writes consensus/disputed CSVs

### `src/task_exposure/parser.py`
Parses pipe-delimited model responses in three formats:
- `merged` — single reasoning column for all axes
- `per_axis` — separate reasoning per axis (used in production)
- `axis_dispute` — round 2 format (one row per disputed axis)

### `src/task_exposure/profiles.py`
Loads and formats occupation profiles including:
- O*NET descriptions, work activities, job zones
- RAPIDS apprenticeship status
- Carollo licensing data (number of states requiring licenses)
