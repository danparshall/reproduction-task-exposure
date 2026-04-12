# Rename Round Terminology: r1/r2 → i-round/c-round

**Goal:** Eliminate the naming collision between pipeline rounds (r1/r2) and R-axis levels (R0-R4) in the CDR framework.

**Originating conversation:** [20260412_rename_rounds_ir_cr](../convos/20260412_rename_rounds_ir_cr.md)

**Context:** The codebase uses "r1/r2" everywhere to mean initial-round/consensus-round, but "R" is also an axis in the CDR framework with levels R0-R4. This creates genuine confusion when discussing results — "R1" could mean round 1 or R-axis level 1. The rename uses "ir" (initial round) and "cr" (consensus round) internally, and "initial"/"consensus" in user-facing text.

**Confidence:** High — this is a mechanical rename with clear scope boundaries. The audit identified every reference.

**Architecture:** Find-and-replace across Python code, CSV headers, filenames, metadata JSON, and documentation. The critical constraint is distinguishing round references (rename) from R-axis references (do NOT touch).

**Branch:** `rename-rounds`

**Tech Stack:** Python, CSV, JSON, Markdown

---

## Testing Plan

The existing test suite (33 tests in `eloundou/tests/test_replication.py`) does not directly test the round-related code paths — it tests the Eloundou replication module. We need tests that verify:

1. **CLI flag parsing:** `--round initial` and `--round consensus` are accepted; old values `1`/`2` are rejected
2. **Consensus round prompt building:** `build_cr_prompt()` (renamed from `build_r2_prompt()`) produces valid prompts
3. **Checkpoint directory naming:** c-round checkpoints use `_cr` suffix (not `_r2`)
4. **Aggregation merge:** `merge_ir_cr()` (renamed from `merge_r1_r2()`) correctly overlays c-round ratings onto i-round
5. **Output filenames:** aggregated output uses `consensus_cr.csv` / `disputed_cr.csv` naming
6. **CSV column headers:** published data has `_ir` columns (not `_r1`)
7. **Result loading:** `compare_results.py` finds both new `_cr` filenames and legacy `_r2` filenames (backward compat for any external data)

NOTE: I will write *all* tests before I add any implementation behavior.

## Steps

### Phase 1: Write failing tests (RED)

1. Create `tests/test_round_naming.py` with tests for:
   - CLI arg parsing accepts `--round initial` and `--round consensus`
   - CLI arg parsing rejects `--round 1` and `--round 2`
   - `build_cr_prompt` function exists and is callable
   - `merge_ir_cr` function exists and is callable
   - Aggregation script generates `_cr` suffix filenames (not `_r2`)
   - `compare_results.py::load_results()` finds `consensus_cr.csv` files
   - `compare_results.py::load_results()` falls back to `consensus_r2.csv` for legacy data
   - Published CSV files in `results/` use `_cr` naming
   - Published CSV headers use `_ir` column suffix (not `_r1`)
   - Metadata JSON files use i-round/c-round terminology

2. Run tests — confirm they all fail for the right reasons (missing functions, wrong filenames, etc.)

### Phase 2: Rename Python code (GREEN)

3. **`scripts/classify.py`:**
   - `--round` choices: `[1, 2]` → `["initial", "consensus"]`, default `"initial"`
   - Function: `build_r2_prompt()` → `build_cr_prompt()`
   - Variables: `r2_checkpoint_dir` → `cr_checkpoint_dir`, `r2_prompts` → `cr_prompts`, `r2_prompt` → `cr_prompt`, `r2_all_complete` → `cr_all_complete`
   - Round checks: `args.round == 1` → `args.round == "initial"`, `args.round == 2` → `args.round == "consensus"`
   - Comments/prints: "Round 1" → "Initial round (i-round)", "Round 2" → "Consensus round (c-round)", "R2" → "c-round"
   - Checkpoint dir suffix: `+ "_r2"` → `+ "_cr"`
   - Metadata: `"round": args.round` stays (now stores "initial"/"consensus" string)
   - Epilog examples: `--round 2` → `--round consensus`

4. **`scripts/aggregate.py`:**
   - Function: `merge_r1_r2()` → `merge_ir_cr()`
   - Parameters: `r1:` → `ir:`, `r2:` → `cr:`
   - Variables: `r1_dir` → `ir_dir`, `r2_dir` → `cr_dir`, `r1_data` → `ir_data`, `r2_data` → `cr_data`, `r2_count` → `cr_count`, `r1_vals` → `ir_vals`, `r2_vals` → `cr_vals`
   - CLI flag: `--r1-only` → `--ir-only`
   - Suffix: `"_r2"` → `"_cr"` in filename generation
   - Comments/docstrings: "R1" → "i-round", "R2" → "c-round"
   - Dir expectations: `"{dir}_r2"` → `"{dir}_cr"`

5. **`scripts/compare_results.py`:**
   - Filenames: `consensus_r2.csv` → `consensus_cr.csv` (with fallback to old names for backward compat)
   - Comments: "R1-only" → "i-round-only", "R2" → "c-round"
   - Column reference in docstring: `"_r1"` → `"_ir"`

6. **`src/task_exposure/runner.py`:**
   - Docstring reference: `build_r2_prompt()` → `build_cr_prompt()`
   - Comments: "i-round and c-round" already used in places; make consistent

### Phase 3: Rename data files

7. **Rename published CSV files:**
   - `results/data_20260313_midtier/consensus_r2.csv` → `consensus_cr.csv`
   - `results/data_20260313_midtier/disputed_r2.csv` → `disputed_cr.csv`
   - `results/data_oldest_available/consensus_r2.csv` → `consensus_cr.csv`
   - `results/data_oldest_available/disputed_r2.csv` → `disputed_cr.csv`

8. **Rename CSV column headers** in `results/data_20260313_midtier/`:
   - `sonnet_C_r1` → `sonnet_C_ir` (and all similar `{model}_{axis}_r1` → `{model}_{axis}_ir`)
   - The `data_oldest_available/` CSVs don't have `_r1` columns — no change needed

9. **Update metadata JSON files:**
   - `results/data_20260313_midtier/run_metadata.json`: `"round": 2` → `"round": "consensus"`
   - `results/data_oldest_available/run_metadata.json`: update `n_tasks_r2` → `n_tasks_cr`, `"R1 + R2 (c-round)"` → `"initial + consensus (i-round + c-round)"`, references in notes

### Phase 4: Update documentation

10. **`README.md`:** Update all round references:
    - "Round 1"/"Round 2" → "Initial round"/"Consensus round" (with i-round/c-round in parens)
    - `--round 2` → `--round consensus`
    - "R1+R2" → "i-round + c-round"
    - File references: `consensus_r2.csv` → `consensus_cr.csv`
    - Add a brief note about the naming convention change

11. **`AGENTS.md`:** Same treatment as README

12. **`results/README.md`:** Update column reference docs, consensus methods (`r2_unanimous` → `cr_unanimous`, `r2_majority` → `cr_majority`), reproduction instructions

13. **`convo_20260327_oldest_model_stability.md`:** Update round references. Be careful — some "R1"/"R2" in this file are R-axis levels (line 77: "R1 (50%), R2 (30%)"). Only rename those that clearly mean rounds based on context.

### Phase 5: Verify

14. Run full test suite — all tests pass
15. Grep for remaining `_r1` and `_r2` references that might have been missed (excluding R-axis levels in prompts.py/profiles.py/CSV cell values)
16. Spot-check CSV files to confirm headers are correct

### Phase 6: Rename Eloundou rubric variables

17. **`eloundou/tests/test_replication.py`:** Rename `metrics_r1`/`metrics_r2` → `metrics_rub1`/`metrics_rub2` (these refer to Eloundou's two rubric variants, not pipeline rounds — but the `r1`/`r2` naming creates a three-way collision with both pipeline rounds AND R-axis levels)

## DO NOT TOUCH

These all refer to R-axis levels, NOT rounds:
- `src/task_exposure/prompts.py` — all R0/R1/R2/R3/R4 references
- `src/task_exposure/profiles.py` — `R0_or_R1` in Carollo data
- CSV cell values (e.g., a task rated `R2` on the regulatory axis)

## Edge Cases

- **Backward compatibility for external data:** Someone may have `consensus_r2.csv` files from a prior run. `compare_results.py` should fall back to old filenames if new ones aren't found.
- **Checkpoint directories:** Existing `_r2` checkpoint dirs in `data/` are gitignored and won't be renamed. The code change means new runs create `_cr` dirs. Old dirs will be orphaned but harmless (per the "never delete data" rule).
- **The convo file** (`convo_20260327_oldest_model_stability.md`) mixes round and R-axis references. Line 77 ("R1 (50%), R2 (30%)") is R-axis levels. Lines 86-90 ("R1:", "R2 (c-round):") are rounds. Must rename carefully by context.

---

**Testing Details:** Tests verify the rename at integration boundaries: CLI parsing, function names/signatures, output file naming, CSV headers, and backward-compatible file loading. Tests exercise real code paths, not mocks.

**Implementation Details:**
- `build_r2_prompt()` → `build_cr_prompt()` is the central function rename
- `merge_r1_r2()` → `merge_ir_cr()` in aggregate.py
- CLI `--round` becomes string-typed with choices `["initial", "consensus"]`
- `--r1-only` → `--ir-only` in aggregate.py
- CSV column suffix `_r1` → `_ir` in published data headers
- File suffix `_r2` → `_cr` in published data filenames
- Consensus method values `r2_unanimous`/`r2_majority` → `cr_unanimous`/`cr_majority`
- Checkpoint dir suffix `_r2` → `_cr` for new runs
- Backward compat: `compare_results.py` tries `_cr` filenames first, falls back to `_r2`

**What could change:** Nothing — this is a settled mechanical rename.

**Questions:**
1. Should the `--round` flag also accept short aliases like `--round i` / `--round c`? Decision: no, full words only.
2. ~~The `eloundou/` module uses `metrics_r1`/`metrics_r2` for Eloundou rubric comparison~~ Resolved: renaming to `metrics_rub1`/`metrics_rub2` to kill the three-way naming collision.

---
