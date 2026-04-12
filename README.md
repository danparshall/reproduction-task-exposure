# Measuring AI Task Exposure: A CDR Classification Framework

**Reproduction package** for Parshall & Lopez-Luzuriaga (2026), "Measuring AI's Economic Reach: A Multi-Axis Task Exposure Framework."

Living paper and abstract: [canaryinstitute.ai/research/task-exposure](https://canaryinstitute.ai/research/task-exposure)

## Overview

This repo classifies ~18,800 occupational tasks from the O*NET database on three independent axes measuring different dimensions of AI task exposure:

| Axis | Measures | Key question |
|------|----------|-------------|
| **C** (Cognitive complexity) | Reasoning demand of the task | "Could you write a complete how-to manual for this task?" |
| **D** (Deployment difficulty) | Sensorimotor/physical requirements | "What sensorimotor loop does this task require?" |
| **R** (Regulatory restrictions) | Barriers to AI-assisted performance | "Can a licensed professional use AI to save 50% of time?" |

Each task is classified by three LLMs (one per provider: Anthropic, OpenAI, Google) using a structured prompt with O*NET contextual enrichment. Disagreements are resolved through a two-round consensus protocol.

### Key Results

- **923 occupations** classified across all three axes (C, D, R on 0-4 scales)
- **~90% inter-round stability** — classifications are reproducible across runs
- **Provider identity dominates tier** — using one model per provider matters more than using flagship models
- **DWA decomposition** splits compound tasks into atomic units, improving classification accuracy

## Getting Started

### Prerequisites

- Python 3.12+
- API keys for at least two of: [Anthropic](https://console.anthropic.com/), [OpenAI](https://platform.openai.com/), [Google AI Studio](https://aistudio.google.com/)
- All three providers are needed for full reproduction

### Setup

```bash
# Clone the repo
git clone https://github.com/danparshall/reproduction-task-exposure.git
cd reproduction-task-exposure

# Create virtual environment and install dependencies
uv venv && source .venv/bin/activate && uv sync

# Or with pip:
python -m venv .venv && source .venv/bin/activate && pip install -e .

# Add your API keys
cp .env.example .env
# Edit .env with your keys
```

### Quick Test (~$2, 3 occupations)

Validate that your setup works:

```bash
# Dry run first — inspect prompts, no API calls
python scripts/classify.py --dry-run

# Run the pilot set (3 occupations)
python scripts/classify.py --soc-set pilot
```

### Standard Test (~$10, 12 occupations)

A representative sample spanning manual labor, knowledge work, regulated professions, and creative occupations:

```bash
python scripts/classify.py --soc-set expanded
```

The 12-occupation test set includes: Hairdressers, HVAC Mechanics, Registered Nurses, Chief Executives, Accountants, Software Developers, Elementary School Teachers, Restaurant Cooks, Customer Service Reps, Construction Laborers, Welders, and Truck Drivers.

### Full Reproduction (~$100, 923 occupations)

```bash
# Step 1: Initial round (i-round) — independent classification
python scripts/classify.py --soc-set full

# Step 2: Consensus round (c-round) — resolve disputed tasks
python scripts/classify.py --soc-set full --round consensus

# Step 3: Aggregate — merge i-round + c-round into final CSVs
python scripts/aggregate.py

# Step 4: Compare — check your results against published baseline
python scripts/compare_results.py --yours output/results
```

The pipeline checkpoints after each occupation — if interrupted, re-run the same command to resume. Steps 1-2 make API calls; steps 3-4 are local only.

### Comparing Results

After aggregation, your results appear in `output/results/` as `consensus_cr.csv` and `disputed_cr.csv`. The comparison script reports task-level agreement, distribution-level agreement, and per-model divergence:

```bash
python scripts/compare_results.py --yours output/results
```

Due to LLM non-determinism, individual ratings may differ, but aggregate distributions should be close. See `results/README.md` for column definitions.

### Model Tiers and Temporal Stability

The pipeline includes several model tiers in `scripts/classify.py`:

| Tier | Anthropic | OpenAI | Google | Notes |
|------|-----------|--------|--------|-------|
| `mid` (default) | claude-sonnet-4-6 | gpt-5-mini | gemini-3-flash-preview | Current mid-tier, ~$100 for full run |
| `flagship` | claude-opus-4-6 | gpt-5.2 | gemini-3-pro-preview | ~$500+ for full run |
| `oldest` | claude-sonnet-4-20250514 | gpt-4o-mini | gemini-2.5-flash | Oldest still-available models |

Use `--model-tier` to select: `python scripts/classify.py --model-tier oldest --soc-set full`

**Temporal stability across model generations:** We tested the full 923-occupation pipeline with the oldest available mid-tier models (~6-12 months older than the defaults). Key findings:

- **77.6% exact match** on consensus ratings vs. current mid-tier
- **94.4% within one level** — nearly all drift is ±1 on the 0-4 scales
- C axis (cognitive complexity): 78.5% exact match, stable across generations
- D axis (deployment difficulty): 84.2% exact match, most stable axis
- R axis (regulatory restrictions): 70.1% exact match, most sensitive to model capability (see below)
- Distribution shapes are preserved: per-level shifts are <5 percentage points for C and D

**R-axis sensitivity:** The R axis requires models to integrate domain-specific context (licensing data, apprenticeship requirements) from the occupation profile enrichment. GPT-4o-mini rates R=0 on ~95% of tasks in the initial round with template reasoning ("No regulatory barriers"), regardless of the occupation's actual regulatory status. The two-round consensus protocol corrects this — GPT-4o-mini updates ~86% of its R-axis ratings in the consensus round when shown other models' reasoning — but some residual bias remains.

**Model sunsetting limits reproducibility:** As of March 2026, no mid-tier models from early 2024 are available via API. Claude 3 Sonnet (March 2024) and Gemini 1.0 Pro (December 2023) are sunset; GPT-3.5-turbo survives but its 16K context window is too small for the framework's enriched prompts (~32K+ required). The practical reproducibility window is ~12 months before models are retired. This framework addresses that by demonstrating stability across model generations rather than pinning to specific model versions.

**Gemini thinking tokens:** Gemini 2.5 Flash (and newer) uses thinking tokens that count against `max_output_tokens`. If you see truncation errors, run Gemini separately with a higher limit:

```bash
python scripts/classify.py --model gemini --max-tokens 32768
```

### A Note on Temperature and Determinism

The pipeline does not set temperature by default — each provider uses its own default. A `--temperature` flag exists for experimentation, but **T=0 does not produce deterministic classifications**:

- Two identical T=0 Sonnet runs agree on ~87% of ratings, with <4% of reasoning texts byte-identical. The ~11% disagreement is genuine model uncertainty at classification boundaries (mostly C1/C2), not sampling noise.
- GPT-5-mini and other reasoning models reject `temperature≠1`.
- Gemini at T=0 triggers a known thinking-token exhaustion bug and is silently blocked.

The default `--max-tokens 16384` accounts for Gemini's internal reasoning overhead, which counts against `max_output_tokens`.

## Using an AI Coding Assistant

This repo is designed to be used with AI coding assistants. Point your agent (Claude Code, Cursor, etc.) at `AGENTS.md` for complete instructions on how the pipeline works, common issues, and module reference.

## Data Sources

| Source | License | Description |
|--------|---------|-------------|
| [O*NET 30.1](https://www.onetcenter.org/database.html) | Public domain | Tasks, abilities, work context, DWA hierarchy |
| [RAPIDS](https://www.apprenticeship.gov/help/what-rapids) ([dataset](https://catalog.data.gov/dataset/registered-apprenticeship-partners-information-database-system-rapids-dataset)) | Public | Registered apprenticeship data (U.S. DOL) |
| [CareerOneStop License Finder](https://www.careeronestop.org/Toolkit/Training/find-licenses.aspx) ([overview](https://www.careeronestop.org/ExploreCareers/Plan/licensed-occupations.aspx)) | Public | State licensing requirements (DOL-sponsored) |
| [Carollo Licensing Data](https://github.com/ncarollo/licensing-data) ([paper](https://www.nber.org/papers/w33580)) | See repo | Historical occupational licensing across 50 states + DC |

O*NET data files are bundled in `data/onet/` (public domain). Pre-compiled licensing and apprenticeship data is in `data/extracted/occupation_profiles.csv`.

## Repository Structure

```
├── scripts/classify.py          # Main classification pipeline
├── scripts/aggregate.py         # Merge i-round + c-round checkpoints into final CSVs
├── scripts/compare_results.py   # Compare your results against published baseline
├── src/task_exposure/           # Python package
│   ├── clients.py               #   LLM API clients (3 providers)
│   ├── prompts.py               #   CDR axis definitions & prompt formatting
│   ├── runner.py                #   Checkpoint/resume & consensus logic
│   ├── parser.py                #   Response parser
│   └── profiles.py              #   Occupation profile loading
├── data/
│   ├── onet/                    #   Bundled O*NET database files
│   ├── extracted/               #   Pre-built task & profile CSVs
│   └── checkpoints/             #   Runtime checkpoints (gitignored)
├── results/                     #   Published classification results
└── output/                      #   Your own run results (gitignored)
```

## Citation

```bibtex
@article{parshall2026measuring,
  title={Measuring AI's Economic Reach: A Multi-Axis Task Exposure Framework},
  author={Parshall, Daniel and Lopez-Luzuriaga, Andrea},
  year={2026},
  url={https://canaryinstitute.ai/research/task-exposure}
}
```

## License

MIT. See [LICENSE](LICENSE) for details.

O*NET data is public domain (U.S. government work product).
