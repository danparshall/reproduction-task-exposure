#!/usr/bin/env python3
"""Build task-level and occupation-level CDR files from the reproduction package.

Inputs (paths relative to a clone of danparshall/reproduction-task-exposure):
    results/data_20260313_midtier/consensus_cr.csv   # DWA-level consensus ratings
    data/extracted/onet_tasks_full_18k.csv           # O*NET 30.2 task -> SOC map

Outputs:
    cdr_task_level_soc.csv      # one row per O*NET parent task (DWA rows recombined)
    cdr_occupation_level.csv    # one row per O*NET-SOC 2019 occupation

Usage:
    python build_cdr_occupation_files.py [--repo PATH_TO_REPRO_CLONE] [--outdir DIR]
"""

import argparse
import sys
from pathlib import Path

import pandas as pd

WARNING = (
    "WARNING: DWA-decomposed rows are recombined to parent tasks by SIMPLE AVERAGING\n"
    "of ordinal 0-4 scores. Averaging ordinal categories is technically wrong, but is\n"
    "nevertheless useful: it is transparent, monotone, and reproducible, and threshold\n"
    "measures (e.g. C<=2) are applied to the fractional value. E.g. (C1+C3)/2 -> C2.0;\n"
    "(C2+C3)/2 -> C2.5, which does NOT satisfy C<=2. Sensitivity-check your thresholds."
)

# Policy thresholds (working-paper conventions)
C_EXPOSED = 2   # cognitively tractable
D_LOW = 1       # no meaningful physical tether
R_LOW = 1       # no meaningful licensing/regulatory tether


def build(repo: Path, outdir: Path) -> None:
    print(WARNING, file=sys.stderr)

    consensus = pd.read_csv(
        repo / "results/data_20260313_midtier/consensus_cr.csv", dtype={"task_id": str}
    )
    onet = pd.read_csv(repo / "data/extracted/onet_tasks_full_18k.csv")

    # task_id like "9999-2" = second DWA component of parent O*NET task 9999
    consensus["base_id"] = consensus["task_id"].str.split("-").str[0].astype(int)
    for ax in "CDR":
        # labels like "C2" -> 2.0
        consensus[ax] = consensus[f"consensus_{ax}"].str[1].astype(float)

    # --- recombine DWA components to parent tasks (simple average; see WARNING) ---
    task = (
        consensus.groupby("base_id")
        .agg(n_dwa_rows=("task_id", "count"), C=("C", "mean"), D=("D", "mean"), R=("R", "mean"))
        .reset_index()
        .merge(
            onet[["task_id", "onet_soc_code", "occupation_title", "task_description",
                  "importance_score"]],
            left_on="base_id", right_on="task_id", how="left",
        )
        .drop(columns="task_id")
        .rename(columns={"base_id": "onet_task_id"})
    )
    n_unmatched = task["onet_soc_code"].isna().sum()
    if n_unmatched:
        raise RuntimeError(f"{n_unmatched} tasks failed the O*NET SOC join")

    # --- policy measures (thresholds applied to fractional recombined scores) ---
    task["exposed_C2D1"] = (task.C <= C_EXPOSED) & (task.D <= D_LOW)
    task["footloose_D1R1"] = (task.D <= D_LOW) & (task.R <= R_LOW)
    for cmax in (1, 2, 3):
        task[f"footloose_C{cmax}"] = task["footloose_D1R1"] & (task.C <= cmax)

    task_cols = ["onet_task_id", "onet_soc_code", "occupation_title", "task_description",
                 "importance_score", "n_dwa_rows", "C", "D", "R",
                 "exposed_C2D1", "footloose_D1R1",
                 "footloose_C1", "footloose_C2", "footloose_C3"]
    task[task_cols].round(3).to_csv(outdir / "cdr_task_level_soc.csv", index=False)

    # --- occupation-level unweighted task shares ---
    occ = (
        task.groupby(["onet_soc_code", "occupation_title"])
        .agg(
            n_tasks=("onet_task_id", "count"),
            mean_C=("C", "mean"), mean_D=("D", "mean"), mean_R=("R", "mean"),
            share_C_le2=("C", lambda s: (s <= C_EXPOSED).mean()),
            share_D_le1=("D", lambda s: (s <= D_LOW).mean()),
            share_R_le1=("R", lambda s: (s <= R_LOW).mean()),
            share_exposed_C2D1=("exposed_C2D1", "mean"),
            share_footloose_D1R1=("footloose_D1R1", "mean"),
            share_footloose_C_le1=("footloose_C1", "mean"),
            share_footloose_C_le2=("footloose_C2", "mean"),
            share_footloose_C_le3=("footloose_C3", "mean"),
        )
        .round(4)
        .reset_index()
    )
    occ.to_csv(outdir / "cdr_occupation_level.csv", index=False)

    print(f"tasks: {len(task)} | occupations: {len(occ)} | wrote to {outdir}/", file=sys.stderr)


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    here = Path(__file__).resolve().parent
    p.add_argument("--repo", type=Path, default=here.parent,
                   help="path to a clone of reproduction-task-exposure (default: this repo)")
    p.add_argument("--outdir", type=Path, default=here)
    args = p.parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    build(args.repo, args.outdir)
