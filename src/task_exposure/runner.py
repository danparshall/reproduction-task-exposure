"""CDR production runner — core logic for full 18k pipeline with C-v2 + R-v8.

Separates testable logic (data loading, checkpointing, consensus) from
CLI orchestration (in scripts/run_cdr_production.py).
"""

from __future__ import annotations

import csv
import hashlib
import json
import tempfile
from collections import Counter, defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------


def load_all_socs(csv_path: str) -> dict[str, list[dict]]:
    """Load tasks from full 18k CSV, grouped by SOC code.

    Returns dict mapping SOC code → list of task dicts.
    Each task dict has: task_id, onet_soc_code, occupation_title, task_description.
    """
    grouped: dict[str, list[dict]] = defaultdict(list)
    with open(csv_path, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            soc = row["onet_soc_code"]
            grouped[soc].append(
                {
                    "task_id": row["task_id"],
                    "onet_soc_code": soc,
                    "occupation_title": row["occupation_title"],
                    "task_description": row["task_description"],
                }
            )
    return dict(grouped)


# ---------------------------------------------------------------------------
# Checkpoint / resume
# ---------------------------------------------------------------------------


def save_checkpoint(
    results: dict[str, dict],
    soc_code: str,
    model_label: str,
    checkpoint_dir: str,
) -> None:
    """Atomically save per-SOC results for one model.

    File: {checkpoint_dir}/{model_label}/soc_{soc_code}.json
    """
    model_dir = Path(checkpoint_dir) / model_label
    model_dir.mkdir(parents=True, exist_ok=True)
    target = model_dir / f"soc_{soc_code}.json"

    # Atomic write via temp file + rename
    fd, tmp_path = tempfile.mkstemp(dir=str(model_dir), suffix=".tmp")
    try:
        with open(fd, "w") as f:
            json.dump(results, f, indent=2)
        Path(tmp_path).replace(target)
    except Exception:
        Path(tmp_path).unlink(missing_ok=True)
        raise


def load_checkpoints(
    checkpoint_dir: str,
    model_label: str,
) -> dict[str, dict]:
    """Load all checkpoints for one model.

    Returns dict mapping SOC code → task results dict.
    """
    model_dir = Path(checkpoint_dir) / model_label
    if not model_dir.exists():
        return {}

    results = {}
    for f in model_dir.glob("soc_*.json"):
        soc_code = f.stem.replace("soc_", "")
        with open(f) as fp:
            results[soc_code] = json.load(fp)
    return results


def get_remaining_work(
    all_socs: list[str],
    checkpoint_dir: str,
    model_label: str,
) -> list[str]:
    """Return SOC codes that don't have checkpoints for this model."""
    completed = load_checkpoints(checkpoint_dir, model_label)
    return [soc for soc in all_socs if soc not in completed]


# ---------------------------------------------------------------------------
# Consensus
# ---------------------------------------------------------------------------


def build_consensus(
    model_results: dict[str, dict[str, dict[str, str]]],
    axes: list[str] | None = None,
) -> tuple[list[dict], list[dict]]:
    """Build majority-vote consensus from 3-model results.

    Resolves 2-1 splits via majority vote. Only 3-way splits (all three
    models give different values) remain unresolved in disputed_rows.

    NOTE: This function does NOT determine c-round eligibility. The c-round
    sends ALL non-unanimous task-axis combos (both 2-1 and 3-way splits)
    for re-rating — see build_r2_prompt() in run_cdr_production.py. This
    function is used for output aggregation after both i-round and c-round.

    Args:
        model_results: {model_label: {task_id: {C, D, R, ...}}}
        axes: Axes to compute consensus over. Default ["C", "D", "R"].

    Returns:
        (consensus_rows, disputed_rows) where each row is a dict with
        task_id, per-model ratings, consensus values, and dispute info.
        disputed_rows contains only tasks with at least one 3-way split.
    """
    if axes is None:
        axes = ["C", "D", "R"]

    model_labels = list(model_results.keys())

    # Collect all task IDs across models
    all_task_ids = sorted(
        set().union(*(r.keys() for r in model_results.values()))
    )

    consensus_rows = []
    disputed_rows = []

    for tid in all_task_ids:
        # Gather ratings from each model
        ratings_by_model = {}
        for label in model_labels:
            r = model_results[label].get(tid)
            if r:
                ratings_by_model[label] = r

        if len(ratings_by_model) < 2:
            continue

        row = {"task_id": tid}

        # Add per-model ratings
        for label in model_labels:
            r = ratings_by_model.get(label, {})
            for axis in axes:
                row[f"{label}_{axis}"] = r.get(axis, "")

        # Compute per-axis consensus
        dispute_axes = []
        for axis in axes:
            vals = [
                r.get(axis)
                for r in ratings_by_model.values()
                if r.get(axis)
            ]
            if not vals:
                row[f"consensus_{axis}"] = ""
                continue

            counts = Counter(vals)
            winner, winner_count = counts.most_common(1)[0]

            if winner_count >= 2:
                # Majority (2/3 unanimous or 2/3 majority) — resolved
                row[f"consensus_{axis}"] = winner
            else:
                # 3-way split (all 3 models differ) — unresolvable by vote
                row[f"consensus_{axis}"] = ""
                dispute_axes.append(axis)

        row["dispute_axes"] = ",".join(dispute_axes) if dispute_axes else ""

        if dispute_axes:
            disputed_rows.append(row)
        else:
            consensus_rows.append(row)

    return consensus_rows, disputed_rows


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------


def save_aggregated_results(
    consensus: list[dict],
    disputed: list[dict],
    out_dir: str,
) -> None:
    """Write consensus and disputed CSVs."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    for rows, filename in [(consensus, "consensus.csv"), (disputed, "disputed.csv")]:
        if not rows:
            # Write empty file with minimal header
            with open(out / filename, "w", newline="") as f:
                f.write("task_id\n")
            continue

        fieldnames = list(rows[0].keys())
        with open(out / filename, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


# ---------------------------------------------------------------------------
# Prompt snapshot
# ---------------------------------------------------------------------------


def build_prompt_snapshot(
    system_prompt: str,
    sample_user_prompt: str,
) -> dict:
    """Build reproducibility snapshot with SHA-256 hash."""
    combined = system_prompt + sample_user_prompt
    sha = hashlib.sha256(combined.encode()).hexdigest()
    return {
        "system_prompt": system_prompt,
        "sample_user_prompt": sample_user_prompt,
        "sha256": sha,
    }
