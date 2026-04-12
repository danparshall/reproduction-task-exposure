#!/usr/bin/env python3
"""Aggregate i-round and c-round checkpoints into final consensus CSVs.

After running both rounds of classification:
  python scripts/classify.py --soc-set full                      # Initial round (i-round)
  python scripts/classify.py --soc-set full --round consensus    # Consensus round (c-round)

Run this script to merge the results:
  python scripts/aggregate.py

This produces consensus_cr.csv and disputed_cr.csv in the output directory,
which compare_results.py uses for comparison against published baselines.

The merge logic: for each task, c-round ratings override i-round on any axis
where the model provided an updated rating. Axes not disputed in the c-round
keep their i-round values. The final consensus is computed by majority vote (2-of-3).

Usage:
  # Default: merge data/checkpoints into output/results
  python scripts/aggregate.py

  # Custom directories:
  python scripts/aggregate.py --checkpoint-dir data/checkpoints_oldest_expanded \\
                              --output-dir output/results_oldest_full

  # Custom model tier (determines which model labels to look for):
  python scripts/aggregate.py --model-tier oldest

  # i-round only (no c-round merge):
  python scripts/aggregate.py --ir-only
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from task_exposure.runner import build_consensus, save_aggregated_results  # noqa: E402

AXES = ["C", "D", "R"]

# Must match the model labels in MODEL_TIERS in classify.py
DEFAULT_MODEL_LABELS = ["sonnet", "gpt", "gemini"]


def load_model_checkpoints(checkpoint_dir: Path, model_label: str) -> dict[str, dict]:
    """Load all checkpoint files for one model, returning {task_id: {axis: rating, ...}}."""
    model_dir = checkpoint_dir / model_label
    if not model_dir.exists():
        return {}

    merged = {}
    for f in sorted(model_dir.glob("soc_*.json")):
        with open(f) as fp:
            soc_results = json.load(fp)
            merged.update(soc_results)
    return merged


def merge_ir_cr(
    ir: dict[str, dict],
    cr: dict[str, dict],
) -> dict[str, dict]:
    """Overlay c-round ratings onto i-round. C-round values override per-axis where present."""
    merged = {}
    for tid, ir_vals in ir.items():
        merged[tid] = dict(ir_vals)

    for tid, cr_vals in cr.items():
        if tid not in merged:
            merged[tid] = dict(cr_vals)
            continue
        for axis in AXES:
            if cr_vals.get(axis):
                merged[tid][axis] = cr_vals[axis]
            # Also update reasoning if present
            reasoning_key = f"{axis.lower()}_reasoning"
            if cr_vals.get(reasoning_key):
                merged[tid][reasoning_key] = cr_vals[reasoning_key]

    return merged


def main():
    parser = argparse.ArgumentParser(
        description="Aggregate i-round and c-round checkpoints into final consensus CSVs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/aggregate.py
  python scripts/aggregate.py --checkpoint-dir data/checkpoints_oldest_expanded
  python scripts/aggregate.py --ir-only
""",
    )
    parser.add_argument(
        "--checkpoint-dir",
        type=str,
        default="data/checkpoints",
        help="Initial round checkpoint directory. C-round checkpoints are expected at {dir}_cr. Default: data/checkpoints",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output/results",
        help="Output directory for consensus CSVs. Default: output/results",
    )
    parser.add_argument(
        "--model-labels",
        type=str,
        nargs="+",
        default=DEFAULT_MODEL_LABELS,
        help=f"Model labels to aggregate. Default: {' '.join(DEFAULT_MODEL_LABELS)}",
    )
    parser.add_argument(
        "--ir-only",
        action="store_true",
        help="Only aggregate i-round checkpoints (skip c-round merge).",
    )
    args = parser.parse_args()

    ir_dir = Path(args.checkpoint_dir)
    cr_dir = Path(f"{args.checkpoint_dir}_cr")
    out_dir = Path(args.output_dir)

    if not ir_dir.exists():
        print(f"ERROR: Checkpoint directory not found: {ir_dir}")
        sys.exit(1)

    # Load and merge checkpoints for each model
    print(f"Loading checkpoints from {ir_dir}")
    model_results = {}
    for label in args.model_labels:
        ir_data = load_model_checkpoints(ir_dir, label)

        if args.ir_only or not cr_dir.exists():
            final = ir_data
            cr_count = 0
        else:
            cr_data = load_model_checkpoints(cr_dir, label)
            final = merge_ir_cr(ir_data, cr_data)
            cr_count = len(cr_data)

        if final:
            model_results[label] = final
            cr_note = f" (+{cr_count} c-round updates)" if cr_count else ""
            print(f"  [{label}] {len(final)} task rows{cr_note}")
        else:
            print(f"  [{label}] no checkpoints found")

    if len(model_results) < 2:
        print(f"ERROR: Need at least 2 models, found {len(model_results)}")
        sys.exit(1)

    # Build consensus
    print(f"\nBuilding consensus from {len(model_results)} models...")
    consensus, disputed = build_consensus(model_results, axes=AXES)
    total = len(consensus) + len(disputed)

    if total == 0:
        print("ERROR: No overlapping tasks across models")
        sys.exit(1)

    print(f"  Consensus: {len(consensus)}/{total} ({100 * len(consensus) / total:.1f}%)")
    print(f"  Disputed:  {len(disputed)}/{total} ({100 * len(disputed) / total:.1f}%)")

    # Save with appropriate filenames
    suffix = "" if args.ir_only else "_cr"
    out_dir.mkdir(parents=True, exist_ok=True)

    consensus_file = out_dir / f"consensus{suffix}.csv"
    disputed_file = out_dir / f"disputed{suffix}.csv"

    # save_aggregated_results writes consensus.csv/disputed.csv — we need to
    # write with the correct suffix, so do it directly
    import csv

    for rows, path in [(consensus, consensus_file), (disputed, disputed_file)]:
        if not rows:
            with open(path, "w", newline="") as f:
                f.write("task_id\n")
            continue
        fieldnames = list(rows[0].keys())
        with open(path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    print(f"\nResults saved to {out_dir}:")
    print(f"  {consensus_file.name}")
    print(f"  {disputed_file.name}")


if __name__ == "__main__":
    main()
