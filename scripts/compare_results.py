#!/usr/bin/env python3
"""Compare your classification results against published baseline data.

Loads both consensus and disputed files from each dataset, handles format
differences between R1-only runs and R2 (two-round) published data, and
reports task-level agreement, distribution-level agreement, and per-model
divergence.

Usage:
  # Compare default output against published mid-tier baseline:
  python scripts/compare_results.py

  # Compare a specific output directory:
  python scripts/compare_results.py --yours output/results_t0

  # Compare against a different baseline:
  python scripts/compare_results.py --baseline results/data_20260313_flagship
"""

from __future__ import annotations

import argparse
import csv
import sys
from collections import Counter
from pathlib import Path

AXES = ["C", "D", "R"]

# Published data uses these model labels (mid-tier)
KNOWN_MODEL_LABELS = ["sonnet", "gpt", "gemini"]


def load_results(directory: Path) -> dict[str, dict]:
    """Load all task results from a results directory.

    Reads both consensus and disputed CSVs, returning a unified dict
    of task_id -> row. Works with both R1-only format (consensus.csv)
    and R2 format (consensus_r2.csv).
    """
    results = {}

    # Try R2 filenames first, then R1
    consensus_file = directory / "consensus_r2.csv"
    disputed_file = directory / "disputed_r2.csv"
    if not consensus_file.exists():
        consensus_file = directory / "consensus.csv"
        disputed_file = directory / "disputed.csv"

    for path in [consensus_file, disputed_file]:
        if not path.exists():
            continue
        with open(path, newline="") as f:
            for row in csv.DictReader(f):
                results[row["task_id"]] = row

    return results


def extract_consensus(row: dict) -> dict[str, str]:
    """Extract consensus values for each axis from a row."""
    return {axis: row.get(f"consensus_{axis}", "") for axis in AXES}


def extract_model_ratings(row: dict) -> dict[str, dict[str, str]]:
    """Extract per-model ratings from a row (uses final ratings, not _r1)."""
    ratings = {}
    for label in KNOWN_MODEL_LABELS:
        model_ratings = {}
        for axis in AXES:
            val = row.get(f"{label}_{axis}", "")
            if val:
                model_ratings[axis] = val
        if model_ratings:
            ratings[label] = model_ratings
    return ratings


def compare_datasets(yours: dict[str, dict], baseline: dict[str, dict]) -> None:
    """Compare two result datasets and print a report."""
    your_ids = set(yours.keys())
    base_ids = set(baseline.keys())
    overlap = your_ids & base_ids
    yours_only = your_ids - base_ids
    base_only = base_ids - your_ids

    print(f"Your results:     {len(your_ids)} tasks")
    print(f"Baseline results: {len(base_ids)} tasks")
    print(f"Overlapping:      {len(overlap)} tasks")

    if yours_only:
        print(f"In yours only:    {len(yours_only)} tasks")
    if base_only:
        # Only count baseline tasks that would be in our SOC set
        # (baseline may cover all 923 occupations)
        print(f"In baseline only: {len(base_only)} tasks (baseline may cover more occupations)")

    if not overlap:
        print("\nNo overlapping tasks to compare!")
        return

    # ── Task-level agreement ────────────────────────────────────────
    print("\n═══ Task-Level Agreement ═══\n")

    per_axis_stats = {axis: {"exact": 0, "off_by_one": 0, "off_by_more": 0, "both_resolved": 0, "yours_resolved": 0, "baseline_resolved": 0, "neither_resolved": 0} for axis in AXES}

    for tid in sorted(overlap):
        y_cons = extract_consensus(yours[tid])
        b_cons = extract_consensus(baseline[tid])

        for axis in AXES:
            yv = y_cons[axis]
            bv = b_cons[axis]
            stats = per_axis_stats[axis]

            if yv and bv:
                stats["both_resolved"] += 1
                if yv == bv:
                    stats["exact"] += 1
                else:
                    diff = abs(int(yv[1]) - int(bv[1]))
                    if diff == 1:
                        stats["off_by_one"] += 1
                    else:
                        stats["off_by_more"] += 1
            elif yv and not bv:
                stats["yours_resolved"] += 1
            elif bv and not yv:
                stats["baseline_resolved"] += 1
            else:
                stats["neither_resolved"] += 1

    total_comparable = 0
    total_exact = 0
    total_within_one = 0

    for axis in AXES:
        s = per_axis_stats[axis]
        n = s["both_resolved"]
        total_comparable += n
        total_exact += s["exact"]
        total_within_one += s["exact"] + s["off_by_one"]

        if n > 0:
            print(f"  {axis} axis ({n} comparable):")
            print(f"    Exact match:  {s['exact']:>4}/{n}  ({100 * s['exact'] / n:.1f}%)")
            print(f"    Off by one:   {s['off_by_one']:>4}/{n}  ({100 * s['off_by_one'] / n:.1f}%)")
            if s["off_by_more"]:
                print(f"    Off by 2+:    {s['off_by_more']:>4}/{n}  ({100 * s['off_by_more'] / n:.1f}%)")
        else:
            print(f"  {axis} axis: no comparable tasks")

        # Resolution differences
        notes = []
        if s["yours_resolved"]:
            notes.append(f"{s['yours_resolved']} resolved in yours but disputed in baseline")
        if s["baseline_resolved"]:
            notes.append(f"{s['baseline_resolved']} resolved in baseline but disputed in yours")
        if s["neither_resolved"]:
            notes.append(f"{s['neither_resolved']} disputed in both")
        if notes:
            for note in notes:
                print(f"    Note: {note}")
        print()

    if total_comparable > 0:
        print(f"  Overall exact match: {100 * total_exact / total_comparable:.1f}%")
        print(f"  Within one level:    {100 * total_within_one / total_comparable:.1f}%")

    # ── Distribution comparison ─────────────────────────────────────
    print("\n═══ Distribution Comparison ═══\n")

    for axis in AXES:
        y_vals = [extract_consensus(yours[tid])[axis] for tid in overlap if extract_consensus(yours[tid])[axis]]
        b_vals = [extract_consensus(baseline[tid])[axis] for tid in overlap if extract_consensus(baseline[tid])[axis]]

        if not y_vals or not b_vals:
            print(f"  {axis} axis: insufficient data")
            continue

        y_dist = Counter(y_vals)
        b_dist = Counter(b_vals)
        all_levels = sorted(set(list(y_dist.keys()) + list(b_dist.keys())))

        y_total = sum(y_dist.values())
        b_total = sum(b_dist.values())

        print(f"  {axis} axis:")
        print(f"    {'Level':<6} {'Yours':>8} {'Baseline':>10} {'Delta':>8}")
        for level in all_levels:
            y_pct = 100 * y_dist.get(level, 0) / y_total
            b_pct = 100 * b_dist.get(level, 0) / b_total
            print(f"    {level:<6} {y_pct:>7.1f}% {b_pct:>9.1f}% {y_pct - b_pct:>+7.1f}%")
        print()

    # ── Per-model divergence ────────────────────────────────────────
    print("═══ Per-Model Divergence ═══\n")
    print("  How often each model changed its rating between your run and baseline:\n")

    for label in KNOWN_MODEL_LABELS:
        axis_stats = {axis: {"match": 0, "diff": 0, "missing": 0} for axis in AXES}
        for tid in overlap:
            for axis in AXES:
                yv = yours[tid].get(f"{label}_{axis}", "")
                bv = baseline[tid].get(f"{label}_{axis}", "")
                if yv and bv:
                    if yv == bv:
                        axis_stats[axis]["match"] += 1
                    else:
                        axis_stats[axis]["diff"] += 1
                else:
                    axis_stats[axis]["missing"] += 1

        total_match = sum(s["match"] for s in axis_stats.values())
        total_comp = sum(s["match"] + s["diff"] for s in axis_stats.values())
        if total_comp > 0:
            per_axis_detail = "  ".join(
                f"{a}: {100 * axis_stats[a]['match'] / (axis_stats[a]['match'] + axis_stats[a]['diff']):.0f}%"
                if (axis_stats[a]["match"] + axis_stats[a]["diff"]) > 0 else f"{a}: n/a"
                for a in AXES
            )
            print(f"  {label:<8} {100 * total_match / total_comp:.1f}% exact  ({per_axis_detail})")
        else:
            print(f"  {label:<8} no comparable data")

    print()


def compare_two_runs(run_a: dict[str, dict], run_b: dict[str, dict], label_a: str, label_b: str) -> None:
    """Compare two of your own runs (e.g., T=0 vs default temperature)."""
    overlap = set(run_a.keys()) & set(run_b.keys())
    if not overlap:
        print("No overlapping tasks!")
        return

    print(f"Comparing {label_a} vs {label_b}: {len(overlap)} tasks\n")

    for label in KNOWN_MODEL_LABELS:
        matches = 0
        total = 0
        for tid in overlap:
            for axis in AXES:
                va = run_a[tid].get(f"{label}_{axis}", "")
                vb = run_b[tid].get(f"{label}_{axis}", "")
                if va and vb:
                    total += 1
                    if va == vb:
                        matches += 1
        if total:
            print(f"  {label:<8} {matches}/{total} identical ({100 * matches / total:.1f}%)")
        else:
            print(f"  {label:<8} no data")

    # Also compare consensus
    cons_match = 0
    cons_total = 0
    for tid in overlap:
        for axis in AXES:
            va = run_a[tid].get(f"consensus_{axis}", "")
            vb = run_b[tid].get(f"consensus_{axis}", "")
            if va and vb:
                cons_total += 1
                if va == vb:
                    cons_match += 1
    if cons_total:
        print(f"  {'consensus':<8} {cons_match}/{cons_total} identical ({100 * cons_match / cons_total:.1f}%)")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Compare classification results against published baseline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/compare_results.py
  python scripts/compare_results.py --yours output/results_t0
  python scripts/compare_results.py --yours output/results_t0 --also output/results
""",
    )
    parser.add_argument(
        "--yours",
        type=str,
        default="output/results",
        help="Path to your results directory. Default: output/results",
    )
    parser.add_argument(
        "--baseline",
        type=str,
        default="results/data_20260313_midtier",
        help="Path to baseline results directory. Default: results/data_20260313_midtier",
    )
    parser.add_argument(
        "--also",
        type=str,
        default=None,
        help="Path to a second result set for cross-run comparison (e.g., T=0 vs default).",
    )
    args = parser.parse_args()

    yours_dir = Path(args.yours)
    baseline_dir = Path(args.baseline)

    if not yours_dir.exists():
        print(f"ERROR: Results directory not found: {yours_dir}")
        sys.exit(1)
    if not baseline_dir.exists():
        print(f"ERROR: Baseline directory not found: {baseline_dir}")
        sys.exit(1)

    yours = load_results(yours_dir)
    baseline = load_results(baseline_dir)

    if not yours:
        print(f"ERROR: No results loaded from {yours_dir}")
        sys.exit(1)

    print(f"Comparing: {yours_dir} vs {baseline_dir}\n")
    compare_datasets(yours, baseline)

    if args.also:
        also_dir = Path(args.also)
        if not also_dir.exists():
            print(f"ERROR: --also directory not found: {also_dir}")
            sys.exit(1)
        also = load_results(also_dir)
        if also:
            print("═══ Cross-Run Comparison ═══\n")
            compare_two_runs(yours, also, str(yours_dir), str(args.also))

    print("Done.")


if __name__ == "__main__":
    main()
