# CDR Scores — Variable Dictionary and Technical Note

Accompanies `cdr_task_level_soc.csv` and `cdr_occupation_level.csv`, both reproducible via
`build_cdr_occupation_files.py` in this folder.
Source: Parshall & Lopez-Luzuriaga (2026), "Measuring AI's Economic Reach: A Multi-Axis Task Exposure Framework."
Reproduction package: https://github.com/danparshall/reproduction-task-exposure
Living paper: https://canaryinstitute.ai/research/task-exposure

## What the scores are

Each O*NET task is classified on three **independent ordinal 0–4 scales**. The values are
**ordinal categories — not probabilities, not task proportions, not continuous indices.**

| Axis | Measures | Anchor question |
|------|----------|-----------------|
| **C** — Cognitive complexity | Reasoning demand of the task | "Could you write a complete how-to manual for this task?" (C0 = fully proceduralizable … C4 = frontier judgment) |
| **D** — Deployment difficulty | Sensorimotor / physical-presence requirements | "What sensorimotor loop does this task require?" (D0 = pure information work … D4 = dexterous unstructured embodiment) |
| **R** — Regulatory restrictions | Legal/licensing barriers to AI-assisted performance | "Can a licensed professional use AI tools to save 50% of time on this task?" (R0 = unrestricted … R4 = prohibited/human-mandated) |

All classification is anchored to one economic question: *what would it take for AI to cut the
time a worker spends on this task by at least 50%?* Scores measure augmentation feasibility,
not full replacement.

**Provenance.** O*NET 30.2 (Feb 2026), 923 occupations, ~18.8k task statements. Each task rated
by three LLMs (one per provider: Anthropic, OpenAI, Google), disagreements resolved by a
two-round consensus protocol (independent round, then chain-of-thought–sharing round, majority
vote). End-to-end pipeline stability is ~91% pairwise on the full C/D/R vector; the R axis is
the most stable (~98%), C the least (~86%). Treat one-notch differences near a threshold as
noise; shares aggregated over many tasks are robust.

**Coverage.** 18,549 of 18,796 O*NET tasks (98.7%). The remainder had unresolved three-way
model splits on at least one axis and are excluded rather than imputed.

## DWA decomposition and recombination

Compound O*NET tasks were split into their Detailed Work Activity (DWA) components and each
component rated separately (row IDs like `9999-2` in the raw consensus file). In these files,
components are recombined to the parent task by **simple averaging** of the component scores.
Consequence: task-level C/D/R can be fractional (e.g., C = 1.5 from components rated C1 and C2).
This is a deliberate crude approximation — an ordinal mean is not strictly defined — chosen for
transparency and reproducibility. All threshold measures below apply the threshold to the
fractional value (C ≤ 2 includes C = 2.0 but not C = 2.5).

## Files

### `cdr_task_level_soc.csv` — one row per O*NET task (18,549 rows)

| Column | Description |
|--------|-------------|
| `onet_task_id` | O*NET Task ID (joins to O*NET 30.2 Task Statements) |
| `onet_soc_code` | O*NET-SOC 2019 code (e.g., `43-4051.00`) |
| `occupation_title` | O*NET occupation title |
| `task_description` | Task statement text |
| `importance_score` | O*NET task importance (1–5), included for optional weighting |
| `n_dwa_rows` | Number of DWA components averaged into this task's scores |
| `C`, `D`, `R` | Recombined axis scores, 0–4, fractional (see above) |
| `exposed_C2D1` | Boolean: C ≤ 2 AND D ≤ 1 (cognitively tractable, low deployment friction) |
| `footloose_D1R1` | Boolean: D ≤ 1 AND R ≤ 1 (no physical tether, no licensing tether — the stock at risk of relocation/offshoring/reshoring, regardless of current AI capability). "Footloose" in the economic-geography sense: work whose location decision is unconstrained (Spanish: *deslocalizable*) |
| `footloose_C1` / `_C2` / `_C3` | Boolean: footloose AND C ≤ 1 / ≤ 2 / ≤ 3 — timing bands within the footloose stock (lower C ⇒ nearer-term AI pressure) |

### `cdr_occupation_level.csv` — one row per occupation (923 rows)

Unweighted shares of the occupation's tasks (each parent task counts once; DWA components do
**not** multiply a task's weight, per the recombination above).

| Column | Description |
|--------|-------------|
| `n_tasks` | Parent tasks with resolved scores |
| `mean_C`, `mean_D`, `mean_R` | Mean of fractional task scores (descriptive only — ordinal caveat applies) |
| `share_C_le2`, `share_D_le1`, `share_R_le1` | Marginal shares of tasks at/below the threshold |
| `share_exposed_C2D1` | Share of tasks with C ≤ 2 AND D ≤ 1 |
| `share_footloose_D1R1` | Share of tasks with D ≤ 1 AND R ≤ 1 (relocation-risk envelope) |
| `share_footloose_C_le1` / `_le2` / `_le3` | Shares footloose AND within each C band (nested: `_le1` ≤ `_le2` ≤ `_le3` ≤ `share_footloose_D1R1`) |

**Recommended use for relocation/fiscal exposure:** `share_footloose_D1R1` is the *maximum*
exposed envelope for an occupation; the `share_footloose_C_le*` columns grade it by nearness
of AI pressure. Multiply by employment and wage mass from your own administrative or survey
data. If you prefer different cuts (other thresholds, importance-weighted shares), rebuild
from the task-level file — everything needed is in it.

## Caveats

1. **Jurisdiction of R.** The R axis was scored against the US regulatory context. For export
   services (call centers, back office, remote professional work serving foreign clients),
   client-side regulation typically binds, so US-context R is approximately the right measure.
   For occupations serving a domestic market under a different country's law, treat R as
   approximate.
2. **Task exposure ≠ headcount displacement — caveat lector.** Shares measure the fraction of
   an occupation's *tasks* that are exposed/footloose. Occupations can be tethered by mechanisms
   the task framework does not measure — authority, trust, liability, relationship capital,
   within-firm complementarities. Chief Executives score ~94% footloose at the task level and
   are therefore *technically* reshoreable; no one expects CEO reshoring. High footloose shares
   in authority- or trust-intensive occupations are upper bounds on task mobility, not
   predictions about workers. Be cautious converting task shares to worker counts without an
   occupation-level adoption/displacement model.
3. **O*NET task statements can lag modern practice.** Some occupations are described by task
   statements written for older workflows, and D scores inherit the anachronism. Example: Data
   Entry Keyers score only ~33% footloose because O*NET's tasks involve handling physical
   source documents ("canceled checks," "load machines with paper, cards, disks, tape") — rated
   D2, correctly, *for that description*. The modern digital-input variant of the occupation
   would be near-fully footloose. If an occupation's footloose share looks suspiciously low for
   how the work is actually performed in your context, inspect its task-level rows.
4. **Ordinal thresholds are choices.** The C ≤ 2 / D ≤ 1 / R ≤ 1 cutoffs follow the working
   paper's usage. One-notch sensitivity checks are cheap from the task-level file and
   recommended for any headline number.
5. **Stability.** ~91% pairwise end-to-end reproducibility means occupation shares carry a few
   points of pipeline noise; differences of <5pp between occupations should not be
   over-interpreted.

## Citation

Please cite the working paper (Parshall & Lopez-Luzuriaga 2026) and the reproduction package
(data files: `results/data_20260313_midtier`, 2026-03-13 mid-tier run: Claude Sonnet 4.6,
GPT-5-mini, Gemini 3 Flash).
