# Eloundou Replication: Vintage Model Comparison

Self-contained reproduction of the task-level AI exposure labels from Eloundou et al. (2023), "GPTs are GPTs," using 8 OpenAI model vintages spanning June 2023 to March 2026.

This package is independent of the CDR classification pipeline in the parent repo. It reconstructs the Eloundou Appendix A.1 rubric and runs it against O\*NET tasks to measure how well current models can reproduce the original GPT-4 labels.

## Quick Start

```bash
# From the repo root:
cd reproduction-task-exposure

# Install dependencies
uv venv && uv sync

# Run a small test (3 occupations, ~$0.50)
python -m eloundou.runner --model gpt-4-0613 --soc-set pilot --seed 137

# Compare results against Eloundou's published labels
python -m eloundou.compare eloundou/results/gpt-4-0613-per-occ/
```

## What's Here

```
eloundou/
├── prompt.py               # Rubric construction + response parsing
├── runner.py               # Runner + CLI (per-occ and per-task modes)
├── compare.py              # Comparison logic + CLI
├── data/
│   ├── eloundou_labels.tsv     # Eloundou's published GPT-4 labels (19,265 tasks)
│   ├── onet_tasks_18k.csv      # O*NET task descriptions (18,796 tasks, 923 SOCs)
│   └── stratified_50_sample.json   # 1,014-task stratified sample (50 SOCs)
├── results/                # Published results from our vintage comparison
│   ├── gpt-4-0613-full-923/        # Full 923-SOC run with GPT-4-0613
│   ├── gpt-4-0613-strat50-runA/    # GPT-4-0613, 50 SOCs, per-occ, run A
│   ├── gpt-4-0613-strat50-runB/    # GPT-4-0613, 50 SOCs, per-occ, run B
│   ├── gpt-4-turbo-per-occ-strat50/
│   ├── gpt-4-turbo-...-per-task-strat50/
│   ├── {gpt-5,gpt-5.1,gpt-5.2,gpt-5.4}-per-{occ,task}-strat50/
│   ├── {o1,o3}-per-{occ,task}-strat50/
│   └── gpt-5.4-...-strat50-runB/   # Self-agreement test
└── tests/
    └── test_replication.py     # 33 tests
```

## Two Execution Modes

- **Per-occupation** (`--soc-set pilot`): All tasks for a given occupation bundled into one API call. This is how most researchers would implement the rubric at scale.
- **Per-task** (`--per-task`): One API call per task, matching Eloundou's actual methodology more closely.

The mode effect (+3 to +16pp higher agreement in per-task mode) is consistently larger than vintage differences.

## Models

| Model | Type | Released | Knowledge Cutoff |
|-------|------|----------|-----------------|
| GPT-4-0613 | standard | Jun 2023 | Sep 2021 |
| GPT-4-Turbo | standard | Apr 2024 | Dec 2023 |
| o1 | reasoning | Dec 2024 | Oct 2023 |
| o3 | reasoning | Apr 2025 | ~Jun 2025 |
| GPT-5 | reasoning | Aug 2025 | Sep 2024 |
| GPT-5.1 | standard | Nov 2025 | Sep 2024 |
| GPT-5.2 | standard | Dec 2025 | Aug 2025 |
| GPT-5.4 | standard | Mar 2026 | Aug 2025 |

"Standard" models support `temperature=0` and `seed` parameters. "Reasoning" models (o1, o3, GPT-5 base) use `developer` role instead of `system` and don't support temperature or seed.

## Key Results

### Three-Class Agreement with Eloundou (E0/E1/E2)

| Model | Per-occ | Per-task | Mode Gap |
|-------|---------|----------|----------|
| GPT-4-0613 | 57.9% | -- | -- |
| GPT-4-Turbo | 56.5% | 72.7% | +16pp |
| o1 | 64.2% | 66.8% | +3pp |
| o3 | 65.3% | 69.0% | +4pp |
| GPT-5 | 69.1% | 75.6% | +7pp |
| GPT-5.1 | 57.7% | 69.7% | +12pp |
| **GPT-5.2** | **73.8%** | **80.6%** | **+7pp** |
| GPT-5.4 | 68.8% | 75.0% | +6pp |

**The practical ceiling for Eloundou reproduction is ~80%.** No model exceeds 81% agreement. ~20% of labels are inherently ambiguous or depend on factors not in the rubric.

### Sources of Disagreement (by effect size)

1. **Execution mode** (+3 to +16pp): Per-task > per-occ. Models hedge toward E1 when seeing multiple tasks.
2. **Model identity** (±15pp within mode): GPT-5.2 and GPT-5.1 are 1 month apart but differ by 11pp.
3. **E1/E2 boundary**: E0 recall is >90% across all models. E1 vs E2 is where models diverge.
4. **Stochastic variation** (~5%): GPT-5.4 self-agreement is 95%; GPT-4-0613 was ~88%.

### CDR as Alternative Reference

When CDR classifications (binary exposed/not-exposed) replace Eloundou as reference:
- Agreement is higher and more stable (77-84% vs 56-81%)
- Mode effect largely disappears
- No trend with model vintage — the Eloundou rubric constrains models to evaluate a "text-only, 2000-word" LLM, suppressing capability tracking

## Running Your Own Comparison

```bash
# Run GPT-5.2 on the stratified 50-SOC set (per-occupation mode)
python -m eloundou.runner --model gpt-5.2 --soc-set stratified_50 --seed 137

# Run per-task mode on the same sample
python -m eloundou.runner --model gpt-5.2 --per-task --seed 137

# Compare against Eloundou labels
python -m eloundou.compare eloundou/results/gpt-5.2-per-occ/

# Compare two models against each other
python -m eloundou.compare eloundou/results/gpt-5.2-per-occ-strat50/ \
    --versus eloundou/results/gpt-4-0613-strat50-runA/
```

## API Parameters

| Model Type | Role | Temperature | Seed | Token Param |
|-----------|------|-------------|------|-------------|
| Standard | system | 0.0 | configurable | max_tokens (GPT-4) or max_completion_tokens (GPT-5+) |
| Reasoning | developer | not supported | not supported | max_completion_tokens |

## Citation

```bibtex
@article{eloundou2023gpts,
  title={GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models},
  author={Eloundou, Tyna and Manning, Sam and Mishkin, Pamela and Rock, Daniel},
  journal={arXiv preprint arXiv:2303.10130},
  year={2023}
}
```
