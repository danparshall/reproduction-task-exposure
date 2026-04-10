"""Comparison of replication results against Eloundou published labels.

Loads replication checkpoint JSONs, joins against eloundou_labels.tsv,
and computes concordance metrics (accuracy, kappa, confusion matrix).

Supports both per-occupation checkpoints ({soc_code}.json with parsed_labels)
and per-task checkpoints (task_{id}.json with label field).

Usage:
    # Compare one model vs Eloundou:
    python -m eloundou.compare results/gpt-4-0613-full-923/

    # Compare two models against each other and Eloundou:
    python -m eloundou.compare results/gpt-4-0613-per-occ-strat50/ \
        --versus results/gpt-5.2-per-occ-strat50/
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

PACKAGE_ROOT = Path(__file__).parent
DATA_DIR = PACKAGE_ROOT / "data"
ELOUNDOU_TSV = DATA_DIR / "eloundou_labels.tsv"


def load_eloundou_labels(tsv_path: Path, soc_codes: list[str]) -> pd.DataFrame:
    """Load Eloundou labels, filtered to specific SOC codes.

    Args:
        tsv_path: Path to eloundou_labels.tsv
        soc_codes: List of O*NET-SOC codes to include.

    Returns:
        DataFrame with columns: task_id, onet_soc_code, gpt4_exposure,
        gpt4_exposure_alt_rubric, human_exposure_agg, task_description, title.
    """
    df = pd.read_csv(tsv_path, sep="\t")
    df = df.rename(columns={
        "O*NET-SOC Code": "onet_soc_code",
        "Task ID": "task_id",
        "Task": "task_description",
        "Title": "title",
        "Task Type": "task_type",
    })
    df["task_id"] = df["task_id"].astype(int)
    df = df[df["onet_soc_code"].isin(soc_codes)]

    keep_cols = [
        "task_id", "onet_soc_code", "task_description", "title", "task_type",
        "gpt4_exposure", "gpt4_exposure_alt_rubric", "human_exposure_agg",
    ]
    return df[[c for c in keep_cols if c in df.columns]].reset_index(drop=True)


def load_replication_results(result_dir: Path) -> pd.DataFrame:
    """Load checkpoint JSONs into a flat DataFrame.

    Supports two checkpoint formats:
    - Per-occupation: {soc_code}.json with "parsed_labels" list
    - Per-task: task_{id}.json with "label" and "soc_code" fields

    Args:
        result_dir: Directory containing checkpoint JSON files.

    Returns:
        DataFrame with columns: task_id, onet_soc_code, replication_label.
    """
    rows = []
    for json_path in sorted(result_dir.glob("*.json")):
        if json_path.name in ("comparison_metrics.json",):
            continue
        with open(json_path) as f:
            checkpoint = json.load(f)
        if "soc_code" not in checkpoint:
            continue
        soc_code = checkpoint["soc_code"]

        if "parsed_labels" in checkpoint:
            # Per-occupation format
            for item in checkpoint["parsed_labels"]:
                rows.append({
                    "task_id": item["task_id"],
                    "onet_soc_code": soc_code,
                    "replication_label": item["label"],
                })
        elif "label" in checkpoint and "task_id" in checkpoint:
            # Per-task format
            label = checkpoint["label"]
            if label:  # skip empty/null labels
                rows.append({
                    "task_id": checkpoint["task_id"],
                    "onet_soc_code": soc_code,
                    "replication_label": label,
                })
    return pd.DataFrame(rows)


def compare_labels(
    replication: pd.DataFrame,
    eloundou: pd.DataFrame,
    target_col: str = "gpt4_exposure",
) -> dict:
    """Compute concordance between replication labels and Eloundou labels.

    Merges E3 into E2 before comparison (matching Eloundou's analysis convention).

    Args:
        replication: DataFrame with task_id, onet_soc_code, replication_label.
        eloundou: DataFrame with task_id, onet_soc_code, and target_col.
        target_col: Column in eloundou to compare against.

    Returns:
        Dict with accuracy, cohens_kappa, confusion_matrix, per_class, n_tasks.
    """
    merged = replication.merge(
        eloundou[["task_id", "onet_soc_code", target_col]],
        on=["task_id", "onet_soc_code"],
        how="inner",
    )

    # Merge E3 → E2
    pred = merged["replication_label"].replace({"E3": "E2"})
    actual = merged[target_col].replace({"E3": "E2"})

    labels = ["E0", "E1", "E2"]
    n = len(merged)

    if n == 0:
        return {"accuracy": 0.0, "cohens_kappa": 0.0, "confusion_matrix": {}, "n_tasks": 0}

    accuracy = (pred.values == actual.values).mean()

    # Confusion matrix
    cm = np.zeros((3, 3), dtype=int)
    idx = {label: i for i, label in enumerate(labels)}
    for a, p in zip(actual, pred):
        if a in idx and p in idx:
            cm[idx[a], idx[p]] += 1

    # Cohen's kappa
    p_o = accuracy
    row_sums = cm.sum(axis=1) / n
    col_sums = cm.sum(axis=0) / n
    p_e = (row_sums * col_sums).sum()
    kappa = (p_o - p_e) / (1 - p_e) if p_e < 1.0 else 1.0

    # Per-class precision/recall
    per_class = {}
    for label in labels:
        i = idx[label]
        tp = cm[i, i]
        pred_total = cm[:, i].sum()
        actual_total = cm[i, :].sum()
        per_class[label] = {
            "precision": float(tp / pred_total) if pred_total > 0 else 0.0,
            "recall": float(tp / actual_total) if actual_total > 0 else 0.0,
        }

    # Confusion matrix as nested dict
    cm_dict = {}
    for actual_label in labels:
        cm_dict[actual_label] = {}
        for pred_label in labels:
            cm_dict[actual_label][pred_label] = int(cm[idx[actual_label], idx[pred_label]])

    return {
        "accuracy": float(accuracy),
        "cohens_kappa": float(kappa),
        "confusion_matrix": cm_dict,
        "per_class": per_class,
        "n_tasks": n,
    }


def compare_two_models(
    model_a: pd.DataFrame,
    model_b: pd.DataFrame,
    eloundou: pd.DataFrame | None = None,
    target_col: str = "gpt4_exposure",
) -> dict:
    """Compare two replication runs against each other (and optionally Eloundou).

    Both DataFrames must have columns: task_id, onet_soc_code, replication_label.
    Merges E3 into E2 before comparison.

    Returns:
        Dict with agreement, cohens_kappa, confusion_matrix, per_class, n_tasks,
        distribution_a, distribution_b, and optionally disagree_analysis.
    """
    merged = model_a.merge(
        model_b[["task_id", "onet_soc_code", "replication_label"]],
        on=["task_id", "onet_soc_code"],
        how="inner",
        suffixes=("_a", "_b"),
    )

    pred_a = merged["replication_label_a"].replace({"E3": "E2"})
    pred_b = merged["replication_label_b"].replace({"E3": "E2"})

    labels = ["E0", "E1", "E2"]
    n = len(merged)
    if n == 0:
        return {"agreement": 0.0, "cohens_kappa": 0.0, "confusion_matrix": {}, "n_tasks": 0}

    agreement = (pred_a.values == pred_b.values).mean()

    # Confusion matrix (rows=model_a, cols=model_b)
    cm = np.zeros((3, 3), dtype=int)
    idx = {label: i for i, label in enumerate(labels)}
    for a, b in zip(pred_a, pred_b):
        if a in idx and b in idx:
            cm[idx[a], idx[b]] += 1

    # Cohen's kappa
    p_o = agreement
    row_sums = cm.sum(axis=1) / n
    col_sums = cm.sum(axis=0) / n
    p_e = (row_sums * col_sums).sum()
    kappa = (p_o - p_e) / (1 - p_e) if p_e < 1.0 else 1.0

    # Per-class
    per_class = {}
    for label in labels:
        i = idx[label]
        per_class[label] = {
            "count_a": int(cm[i, :].sum()),
            "count_b": int(cm[:, i].sum()),
            "agree": int(cm[i, i]),
        }

    # Distributions
    dist_a = {l: int((pred_a == l).sum()) for l in labels}
    dist_b = {l: int((pred_b == l).sum()) for l in labels}

    # Confusion matrix as nested dict
    cm_dict = {}
    for a_label in labels:
        cm_dict[a_label] = {}
        for b_label in labels:
            cm_dict[a_label][b_label] = int(cm[idx[a_label], idx[b_label]])

    result = {
        "agreement": float(agreement),
        "cohens_kappa": float(kappa),
        "confusion_matrix": cm_dict,
        "per_class": per_class,
        "n_tasks": n,
        "distribution_a": dist_a,
        "distribution_b": dist_b,
    }

    # If Eloundou labels provided, analyze disagreements
    if eloundou is not None and target_col in eloundou.columns:
        merged_el = merged.merge(
            eloundou[["task_id", "onet_soc_code", target_col]],
            on=["task_id", "onet_soc_code"],
            how="inner",
        )
        actual = merged_el[target_col].replace({"E3": "E2"})
        pa = merged_el["replication_label_a"].replace({"E3": "E2"})
        pb = merged_el["replication_label_b"].replace({"E3": "E2"})
        disagree_mask = pa != pb
        n_disagree = int(disagree_mask.sum())
        if n_disagree > 0:
            a_right = int((pa[disagree_mask] == actual[disagree_mask]).sum())
            b_right = int((pb[disagree_mask] == actual[disagree_mask]).sum())
            result["disagree_analysis"] = {
                "n_disagree": n_disagree,
                "a_correct": a_right,
                "b_correct": b_right,
                "neither_correct": n_disagree - a_right - b_right,
            }

    return result


def print_model_comparison(metrics: dict, name_a: str, name_b: str) -> str:
    """Format model-vs-model metrics as a readable report. Returns the report string."""
    lines = []
    lines.append(f"## {name_a} vs {name_b}")
    lines.append("")
    lines.append(f"**Tasks compared:** {metrics['n_tasks']}")
    lines.append(f"**Agreement:** {metrics['agreement']:.1%}")
    lines.append(f"**Cohen's kappa:** {metrics['cohens_kappa']:.3f}")
    lines.append("")

    # Distributions
    da = metrics.get("distribution_a", {})
    db = metrics.get("distribution_b", {})
    lines.append("### Label Distributions")
    lines.append("")
    lines.append(f"| Label | {name_a} | {name_b} |")
    lines.append("|---|---|---|")
    for label in ["E0", "E1", "E2"]:
        lines.append(f"| {label} | {da.get(label, 0)} | {db.get(label, 0)} |")
    lines.append("")

    # Confusion matrix
    cm = metrics.get("confusion_matrix", {})
    if cm:
        lines.append(f"### Confusion Matrix (rows={name_a}, cols={name_b})")
        lines.append("")
        lines.append("|  | Pred E0 | Pred E1 | Pred E2 |")
        lines.append("|---|---|---|---|")
        for label in ["E0", "E1", "E2"]:
            row = cm.get(label, {})
            lines.append(
                f"| **{label}** | {row.get('E0', 0)} | {row.get('E1', 0)} | {row.get('E2', 0)} |"
            )
        lines.append("")

    # Disagreement analysis
    da_info = metrics.get("disagree_analysis")
    if da_info:
        lines.append("### Disagreement Analysis (vs Eloundou)")
        lines.append("")
        lines.append(f"On {da_info['n_disagree']} disagreements:")
        lines.append(f"- {name_a} correct: {da_info['a_correct']}")
        lines.append(f"- {name_b} correct: {da_info['b_correct']}")
        lines.append(f"- Neither correct: {da_info['neither_correct']}")

    report = "\n".join(lines)
    print(report)
    return report


def print_report(metrics: dict, target_col: str) -> str:
    """Format metrics as a readable report. Returns the report string."""
    lines = []
    lines.append(f"## Comparison vs {target_col}")
    lines.append(f"")
    lines.append(f"**Tasks matched:** {metrics['n_tasks']}")
    lines.append(f"**Accuracy:** {metrics['accuracy']:.1%}")
    lines.append(f"**Cohen's kappa:** {metrics['cohens_kappa']:.3f}")
    lines.append("")

    cm = metrics.get("confusion_matrix", {})
    if cm:
        lines.append("### Confusion Matrix (rows=Eloundou, cols=Replication)")
        lines.append("")
        lines.append("|  | Pred E0 | Pred E1 | Pred E2 |")
        lines.append("|---|---|---|---|")
        for label in ["E0", "E1", "E2"]:
            row = cm.get(label, {})
            lines.append(
                f"| **{label}** | {row.get('E0', 0)} | {row.get('E1', 0)} | {row.get('E2', 0)} |"
            )
        lines.append("")

    pc = metrics.get("per_class", {})
    if pc:
        lines.append("### Per-Class Metrics")
        lines.append("")
        lines.append("| Label | Precision | Recall |")
        lines.append("|---|---|---|")
        for label in ["E0", "E1", "E2"]:
            p = pc.get(label, {})
            lines.append(
                f"| {label} | {p.get('precision', 0):.3f} | {p.get('recall', 0):.3f} |"
            )

    report = "\n".join(lines)
    print(report)
    return report


def main():
    parser = argparse.ArgumentParser(description="Compare replication results to Eloundou labels")
    parser.add_argument(
        "result_dir",
        type=Path,
        help="Directory containing per-SOC or per-task checkpoint JSONs",
    )
    parser.add_argument(
        "--eloundou-path",
        type=Path,
        default=ELOUNDOU_TSV,
        help="Path to eloundou_labels.tsv",
    )
    parser.add_argument(
        "--target-col",
        default="gpt4_exposure",
        choices=["gpt4_exposure", "gpt4_exposure_alt_rubric", "human_exposure_agg"],
        help="Which Eloundou column to compare against (default: gpt4_exposure = Rubric 1)",
    )
    parser.add_argument(
        "--versus",
        type=Path,
        default=None,
        help="Second result directory for model-vs-model comparison",
    )
    args = parser.parse_args()

    # Load replication results
    replication_df = load_replication_results(args.result_dir)
    if replication_df.empty:
        print(f"No results found in {args.result_dir}")
        return

    soc_codes = list(replication_df["onet_soc_code"].unique())
    print(f"Loaded {len(replication_df)} replication labels across {len(soc_codes)} occupations")

    # Load Eloundou labels
    eloundou_df = load_eloundou_labels(args.eloundou_path, soc_codes)
    print(f"Loaded {len(eloundou_df)} Eloundou labels for matching SOCs")
    print()

    # Compare against primary target
    metrics = compare_labels(replication_df, eloundou_df, target_col=args.target_col)
    report = print_report(metrics, args.target_col)

    # Also show comparison against alt rubric if comparing against primary
    if args.target_col == "gpt4_exposure" and "gpt4_exposure_alt_rubric" in eloundou_df.columns:
        print("\n---\n")
        alt_metrics = compare_labels(replication_df, eloundou_df, target_col="gpt4_exposure_alt_rubric")
        alt_report = print_report(alt_metrics, "gpt4_exposure_alt_rubric")
        report += "\n\n---\n\n" + alt_report

    # Also show comparison against human labels
    if "human_exposure_agg" in eloundou_df.columns:
        print("\n---\n")
        human_metrics = compare_labels(replication_df, eloundou_df, target_col="human_exposure_agg")
        human_report = print_report(human_metrics, "human_exposure_agg")
        report += "\n\n---\n\n" + human_report

    # Model-vs-model comparison
    all_metrics = {"rubric_1": metrics}
    if args.target_col == "gpt4_exposure":
        all_metrics["rubric_2"] = alt_metrics
        all_metrics["human"] = human_metrics

    if args.versus:
        versus_df = load_replication_results(args.versus)
        if versus_df.empty:
            print(f"\nNo results found in {args.versus}")
        else:
            name_a = args.result_dir.name
            name_b = args.versus.name
            print(f"\nLoaded {len(versus_df)} labels from {name_b}")

            # Also compare versus model against Eloundou
            versus_socs = list(versus_df["onet_soc_code"].unique())
            versus_eloundou = load_eloundou_labels(args.eloundou_path, versus_socs)
            print(f"\n---\n")
            print(f"## {name_b} vs Eloundou\n")
            versus_metrics = compare_labels(versus_df, versus_eloundou, target_col=args.target_col)
            versus_report = print_report(versus_metrics, args.target_col)
            report += "\n\n---\n\n" + f"# {name_b}\n\n" + versus_report
            all_metrics["versus_rubric_1"] = versus_metrics

            # Model-vs-model
            print(f"\n---\n")
            model_metrics = compare_two_models(
                replication_df, versus_df, eloundou=eloundou_df, target_col=args.target_col,
            )
            model_report = print_model_comparison(model_metrics, name_a, name_b)
            report += "\n\n---\n\n" + model_report
            all_metrics["model_vs_model"] = model_metrics

    # Save report
    report_path = args.result_dir / "comparison_report.md"
    with open(report_path, "w") as f:
        f.write(f"# Eloundou Replication Comparison\n\n{report}\n")
    print(f"\nReport saved to {report_path}")

    # Save metrics JSON
    metrics_path = args.result_dir / "comparison_metrics.json"
    with open(metrics_path, "w") as f:
        json.dump(all_metrics, f, indent=2)
    print(f"Metrics saved to {metrics_path}")


if __name__ == "__main__":
    main()
