# task_exposure — Module Documentation

This package implements the CDR classification pipeline for measuring AI task exposure.

## Module Overview

### `prompts.py` (~2000 lines)
The largest module. Contains the full text of all axis definitions (C, D, R, plus the deprecated F axis).

**Key functions:**
- `format_cdr_system_prompt(reasoning_format, c_version, r_version)` — Composes axis definitions into a system prompt. Production uses `reasoning_format="per_axis"`, `c_version="v2"`, `r_version="v8"`.
- `format_user_prompt(tasks, axes, profile, description, abilities, work_context)` — Builds a per-occupation user prompt with DWA expansion and O*NET enrichment.
- `expand_task_dwa_rows(tasks)` — Expands compound tasks into task-DWA pairs. Each task with N DWA labels becomes N rows, each classified independently.
- `get_response_format(format_type, axes)` — Returns the expected response format specification for a given format type.

**Axis versions in production:**
- C-v2: Added "manual test" framing, verification-difficulty bump-up
- D-v4.1: Sensorimotor loop + contact complexity, driving rule
- R-v8: "50% time-reduction" framing with augmentation perspective

### `clients.py`
API clients for three providers. All share the `BaseClient` interface with a single `classify(prompt, system_prompt)` method.

**Error hierarchy:**
- `NonRetryableAPIError` — base for errors that shouldn't be retried
  - `QuotaExhaustedError` — daily/monthly quota hit (wait or upgrade)
  - `BillingError` — payment issues
  - `TruncatedResponseError` — response hit max_tokens ceiling

**`create_client(model, api_key, **kwargs)`** — Factory that selects the right client based on model name prefix. Note: silently drops temperature for Gemini to prevent thinking-token exhaustion.

### `runner.py`
Pipeline infrastructure. No LLM calls — purely data loading, checkpointing, and consensus.

**Checkpoint format:** `{checkpoint_dir}/{model_label}/soc_{SOC_CODE}.json`
Each file contains a dict of `{task_id: {C, D, R, reasoning fields, conf}}`.

**Consensus algorithm:** Simple majority vote per axis. 2/3 agreement resolves the axis. 3-way splits (all three models differ) go to `disputed.csv`.

### `parser.py`
Parses pipe-delimited responses. Handles three formats:
- `merged`: `task_id || reasoning || C || D || R || confidence`
- `per_axis`: `task_id || c_reasoning || d_reasoning || r_reasoning || C || D || R || confidence`
- `axis_dispute`: `task_id || axis || reasoning || rating || confidence` (one row per disputed axis)

Uses `||` as primary delimiter, falls back to `|` for models that don't double-delimit.

### `profiles.py`
Loads `occupation_profiles.csv` and formats it into prompt text. Handles the Carollo licensing display logic (universally regulated, majority of states, minority of states).
