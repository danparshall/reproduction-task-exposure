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
# Round 1: Initial classification
python scripts/classify.py --soc-set full

# Round 2: Consensus on disputed tasks
python scripts/classify.py --soc-set full --round 2
```

The pipeline checkpoints after each occupation — if interrupted, re-run the same command to resume.

### Comparing Results

Your results appear in `output/results/`. Compare against the published results in `results/data_20260313_midtier/`:

```bash
python scripts/compare_results.py
```

Due to LLM non-determinism, individual ratings may differ, but aggregate distributions should be close. See `results/README.md` for column definitions.

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
