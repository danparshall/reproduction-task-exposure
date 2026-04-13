"""Tests for Eloundou replication module.

Tests prompt construction, response parsing, comparison logic, and data loading
for reproducing Eloundou et al. (2023) GPT-4 exposure labeling.
"""
import json
from pathlib import Path

import pandas as pd
import pytest

from eloundou.prompt import (
    build_system_prompt,
    build_user_prompt,
    parse_response,
)
from eloundou.compare import (
    load_eloundou_labels,
    load_replication_results,
    compare_labels,
    compare_two_models,
)

PACKAGE_ROOT = Path(__file__).parent.parent
DATA_DIR = PACKAGE_ROOT / "data"
ELOUNDOU_TSV = DATA_DIR / "eloundou_labels.tsv"
TASKS_CSV = DATA_DIR / "onet_tasks_18k.csv"

# SOC codes used in our standard pilot/expanded sets
PILOT_SOCS = ["39-5012.00", "49-9021.00", "29-1141.00"]


# ── Prompt construction tests ────────────────────────────────────────────


class TestBuildSystemPrompt:
    def test_eloundou_rubric_contains_key_phrases(self):
        prompt = build_system_prompt("eloundou_2023")
        # Must contain the E-level definitions
        assert "E0" in prompt
        assert "E1" in prompt
        assert "E2" in prompt
        assert "E3" in prompt
        # Must contain the time-reduction threshold
        assert "half" in prompt
        # Must contain the 2000-word context constraint
        assert "2000" in prompt

    def test_eloundou_rubric_no_openai_branding(self):
        prompt = build_system_prompt("eloundou_2023")
        assert "OpenAI" not in prompt

    def test_eloundou_rubric_has_release_date_anchor(self):
        prompt = build_system_prompt("eloundou_2023")
        assert "release date" in prompt.lower()

    def test_eloundou_rubric_has_annotation_examples(self):
        prompt = build_system_prompt("eloundou_2023")
        # The appendix includes examples for Inspectors, Computer Scientists, etc.
        assert "Inspectors" in prompt
        assert "Computer and Information Research Scientists" in prompt

    def test_invalid_rubric_raises(self):
        with pytest.raises((ValueError, KeyError)):
            build_system_prompt("nonexistent_rubric")


class TestBuildUserPrompt:
    def test_contains_occupation_title(self):
        tasks = [
            {"task_id": 100, "task_description": "Do something"},
            {"task_id": 101, "task_description": "Do another thing"},
        ]
        prompt = build_user_prompt("Chief Executives", tasks)
        assert "Chief Executives" in prompt

    def test_contains_all_task_ids(self):
        tasks = [
            {"task_id": 8823, "task_description": "Direct financial activities"},
            {"task_id": 8831, "task_description": "Appoint department heads"},
            {"task_id": 8825, "task_description": "Analyze operations"},
        ]
        prompt = build_user_prompt("Chief Executives", tasks)
        assert "8823" in prompt
        assert "8831" in prompt
        assert "8825" in prompt

    def test_contains_all_task_descriptions(self):
        tasks = [
            {"task_id": 100, "task_description": "Direct financial activities"},
            {"task_id": 101, "task_description": "Appoint department heads"},
        ]
        prompt = build_user_prompt("Some Occupation", tasks)
        assert "Direct financial activities" in prompt
        assert "Appoint department heads" in prompt

    def test_empty_tasks_raises(self):
        with pytest.raises(ValueError):
            build_user_prompt("Chief Executives", [])


# ── Response parsing tests ───────────────────────────────────────────────


class TestParseResponse:
    def test_parse_pipe_delimited_format(self):
        response = """Here are my labels:

Task ID: 8823 | E2 | The model could help analyze financial data
Task ID: 8831 | E0 | Requires in-person delegation and judgment
Task ID: 8825 | E2 | Could help with data analysis portions"""

        result = parse_response(response, [8823, 8831, 8825])
        labels = {r["task_id"]: r["label"] for r in result}
        assert labels[8823] == "E2"
        assert labels[8831] == "E0"
        assert labels[8825] == "E2"

    def test_parse_colon_format(self):
        response = """8823: E1 - Writing and analysis task
8831: E0 - Requires physical presence
8825: E2 - Needs additional software"""

        result = parse_response(response, [8823, 8831, 8825])
        labels = {r["task_id"]: r["label"] for r in result}
        assert labels[8823] == "E1"
        assert labels[8831] == "E0"
        assert labels[8825] == "E2"

    def test_parse_captures_e3(self):
        response = """Task ID: 100 | E3 | Needs image capabilities
Task ID: 101 | E1 | Pure text task"""

        result = parse_response(response, [100, 101])
        labels = {r["task_id"]: r["label"] for r in result}
        assert labels[100] == "E3"
        assert labels[101] == "E1"

    def test_parse_reports_missing_tasks(self):
        response = """Task ID: 100 | E1 | Some explanation"""

        result = parse_response(response, [100, 101, 102])
        parsed_ids = {r["task_id"] for r in result}
        assert 100 in parsed_ids
        assert 101 not in parsed_ids
        assert 102 not in parsed_ids

    def test_parse_extracts_explanations(self):
        response = """Task ID: 100 | E2 | The model could assist with data analysis"""

        result = parse_response(response, [100])
        assert len(result) == 1
        assert result[0]["explanation"] != ""

    def test_parse_handles_markdown_table(self):
        response = """| Task ID | Label | Explanation |
|---------|-------|-------------|
| 8823 | E2 | Financial analysis |
| 8831 | E0 | In-person delegation |
| 8825 | E1 | Text-based analysis |"""

        result = parse_response(response, [8823, 8831, 8825])
        labels = {r["task_id"]: r["label"] for r in result}
        assert labels[8823] == "E2"
        assert labels[8831] == "E0"
        assert labels[8825] == "E1"


# ── Comparison logic tests ───────────────────────────────────────────────


class TestCompareLabels:
    def test_perfect_agreement(self):
        replication = pd.DataFrame({
            "task_id": [1, 2, 3, 4],
            "onet_soc_code": ["11-1011.00"] * 4,
            "replication_label": ["E0", "E1", "E2", "E0"],
        })
        eloundou = pd.DataFrame({
            "task_id": [1, 2, 3, 4],
            "onet_soc_code": ["11-1011.00"] * 4,
            "gpt4_exposure": ["E0", "E1", "E2", "E0"],
        })
        metrics = compare_labels(replication, eloundou)
        assert metrics["accuracy"] == 1.0
        assert metrics["cohens_kappa"] == 1.0

    def test_e3_merged_to_e2(self):
        """Replication says E3, Eloundou says E2 — should agree after merge."""
        replication = pd.DataFrame({
            "task_id": [1, 2],
            "onet_soc_code": ["11-1011.00"] * 2,
            "replication_label": ["E3", "E1"],
        })
        eloundou = pd.DataFrame({
            "task_id": [1, 2],
            "onet_soc_code": ["11-1011.00"] * 2,
            "gpt4_exposure": ["E2", "E1"],
        })
        metrics = compare_labels(replication, eloundou)
        assert metrics["accuracy"] == 1.0

    def test_known_disagreement_counts(self):
        """4 tasks: 2 agree, 2 disagree -> 50% accuracy."""
        replication = pd.DataFrame({
            "task_id": [1, 2, 3, 4],
            "onet_soc_code": ["X"] * 4,
            "replication_label": ["E0", "E1", "E0", "E2"],
        })
        eloundou = pd.DataFrame({
            "task_id": [1, 2, 3, 4],
            "onet_soc_code": ["X"] * 4,
            "gpt4_exposure": ["E0", "E1", "E2", "E0"],
        })
        metrics = compare_labels(replication, eloundou)
        assert metrics["accuracy"] == 0.5
        assert "confusion_matrix" in metrics

    def test_compare_against_alt_rubric(self):
        """Should be able to compare against gpt4_exposure_alt_rubric too."""
        replication = pd.DataFrame({
            "task_id": [1, 2],
            "onet_soc_code": ["X"] * 2,
            "replication_label": ["E0", "E1"],
        })
        eloundou = pd.DataFrame({
            "task_id": [1, 2],
            "onet_soc_code": ["X"] * 2,
            "gpt4_exposure": ["E0", "E2"],
            "gpt4_exposure_alt_rubric": ["E0", "E1"],
        })
        metrics_rub1 = compare_labels(replication, eloundou, target_col="gpt4_exposure")
        metrics_rub2 = compare_labels(replication, eloundou, target_col="gpt4_exposure_alt_rubric")
        assert metrics_rub1["accuracy"] == 0.5  # disagrees on task 2
        assert metrics_rub2["accuracy"] == 1.0  # agrees with alt rubric


# ── Data loading tests (use real files) ──────────────────────────────────


class TestDataLoading:
    @pytest.mark.skipif(not ELOUNDOU_TSV.exists(), reason="Eloundou TSV not found")
    def test_load_eloundou_labels_filters_socs(self):
        df = load_eloundou_labels(ELOUNDOU_TSV, PILOT_SOCS)
        assert set(df["onet_soc_code"].unique()) <= set(PILOT_SOCS)
        assert len(df) > 0

    @pytest.mark.skipif(not ELOUNDOU_TSV.exists(), reason="Eloundou TSV not found")
    def test_load_eloundou_labels_has_required_columns(self):
        df = load_eloundou_labels(ELOUNDOU_TSV, PILOT_SOCS)
        assert "task_id" in df.columns
        assert "onet_soc_code" in df.columns
        assert "gpt4_exposure" in df.columns
        assert "gpt4_exposure_alt_rubric" in df.columns

    @pytest.mark.skipif(not ELOUNDOU_TSV.exists(), reason="Eloundou TSV not found")
    def test_eloundou_labels_are_valid(self):
        df = load_eloundou_labels(ELOUNDOU_TSV, PILOT_SOCS)
        valid_labels = {"E0", "E1", "E2", "E3"}
        assert set(df["gpt4_exposure"].unique()) <= valid_labels

    @pytest.mark.skipif(not TASKS_CSV.exists(), reason="Tasks CSV not found")
    def test_task_id_overlap_with_eloundou(self):
        """Our task CSV and Eloundou's TSV should share task IDs for pilot SOCs."""
        el_df = load_eloundou_labels(ELOUNDOU_TSV, PILOT_SOCS)

        # Load our tasks for pilot SOCs
        tasks_df = pd.read_csv(TASKS_CSV)
        tasks_df = tasks_df[tasks_df["onet_soc_code"].isin(PILOT_SOCS)]

        el_ids = set(el_df["task_id"].values)
        our_ids = set(tasks_df["task_id"].values)
        overlap = el_ids & our_ids
        # Should have substantial overlap
        assert len(overlap) > 0
        assert len(overlap) / len(el_ids) > 0.5, (
            f"Only {len(overlap)}/{len(el_ids)} Eloundou task IDs found in our CSV"
        )

    def test_load_replication_results_from_jsons(self, tmp_path):
        """Load results from per-SOC checkpoint JSONs."""
        # Create fake checkpoint files
        for soc, label in [("11-1011.00", "E2"), ("15-1252.00", "E1")]:
            checkpoint = {
                "soc_code": soc,
                "parsed_labels": [
                    {"task_id": 100, "label": label, "explanation": "test"},
                    {"task_id": 101, "label": "E0", "explanation": "test"},
                ],
            }
            with open(tmp_path / f"{soc}.json", "w") as f:
                json.dump(checkpoint, f)

        df = load_replication_results(tmp_path)
        assert len(df) == 4
        assert set(df.columns) >= {"task_id", "onet_soc_code", "replication_label"}
        assert df[df["onet_soc_code"] == "11-1011.00"].iloc[0]["replication_label"] == "E2"

    def test_load_replication_results_per_task_format(self, tmp_path):
        """Load results from per-task checkpoint JSONs."""
        for tid, soc, label in [(100, "11-1011.00", "E0"), (101, "15-1252.00", "E1")]:
            checkpoint = {
                "task_id": tid,
                "soc_code": soc,
                "label": label,
                "explanation": "test",
                "raw_response": "test",
            }
            with open(tmp_path / f"task_{tid}.json", "w") as f:
                json.dump(checkpoint, f)

        df = load_replication_results(tmp_path)
        assert len(df) == 2
        assert set(df.columns) >= {"task_id", "onet_soc_code", "replication_label"}
        assert set(df["replication_label"]) == {"E0", "E1"}

    def test_load_replication_results_mixed_formats(self, tmp_path):
        """Can load a directory with both per-occ and per-task checkpoints."""
        # Per-occ checkpoint
        with open(tmp_path / "11-1011.00.json", "w") as f:
            json.dump({
                "soc_code": "11-1011.00",
                "parsed_labels": [{"task_id": 100, "label": "E2", "explanation": "t"}],
            }, f)
        # Per-task checkpoint
        with open(tmp_path / "task_200.json", "w") as f:
            json.dump({
                "task_id": 200, "soc_code": "15-1252.00",
                "label": "E1", "explanation": "t", "raw_response": "t",
            }, f)

        df = load_replication_results(tmp_path)
        assert len(df) == 2

    def test_load_replication_results_skips_null_labels(self, tmp_path):
        """Per-task checkpoints with empty labels are skipped."""
        with open(tmp_path / "task_100.json", "w") as f:
            json.dump({
                "task_id": 100, "soc_code": "11-1011.00",
                "label": "", "explanation": "", "raw_response": "unparseable",
            }, f)
        df = load_replication_results(tmp_path)
        assert len(df) == 0

    def test_load_replication_results_skips_metrics_json(self, tmp_path):
        """comparison_metrics.json should not be parsed as a checkpoint."""
        with open(tmp_path / "comparison_metrics.json", "w") as f:
            json.dump({"rubric_1": {"accuracy": 0.5}}, f)
        with open(tmp_path / "11-1011.00.json", "w") as f:
            json.dump({
                "soc_code": "11-1011.00",
                "parsed_labels": [{"task_id": 1, "label": "E0", "explanation": "t"}],
            }, f)
        df = load_replication_results(tmp_path)
        assert len(df) == 1


class TestCompareTwoModels:
    def test_perfect_agreement(self):
        model_a = pd.DataFrame({
            "task_id": [1, 2, 3],
            "onet_soc_code": ["X"] * 3,
            "replication_label": ["E0", "E1", "E2"],
        })
        model_b = model_a.copy()
        metrics = compare_two_models(model_a, model_b)
        assert metrics["agreement"] == 1.0
        assert metrics["cohens_kappa"] == 1.0
        assert metrics["n_tasks"] == 3

    def test_known_disagreement(self):
        model_a = pd.DataFrame({
            "task_id": [1, 2, 3, 4],
            "onet_soc_code": ["X"] * 4,
            "replication_label": ["E0", "E1", "E0", "E2"],
        })
        model_b = pd.DataFrame({
            "task_id": [1, 2, 3, 4],
            "onet_soc_code": ["X"] * 4,
            "replication_label": ["E0", "E1", "E1", "E0"],
        })
        metrics = compare_two_models(model_a, model_b)
        assert metrics["agreement"] == 0.5
        assert metrics["n_tasks"] == 4
        assert metrics["distribution_a"]["E0"] == 2
        assert metrics["distribution_b"]["E1"] == 2

    def test_e3_merged_across_models(self):
        """E3 in one model, E2 in other -> should agree after merge."""
        model_a = pd.DataFrame({
            "task_id": [1],
            "onet_soc_code": ["X"],
            "replication_label": ["E3"],
        })
        model_b = pd.DataFrame({
            "task_id": [1],
            "onet_soc_code": ["X"],
            "replication_label": ["E2"],
        })
        metrics = compare_two_models(model_a, model_b)
        assert metrics["agreement"] == 1.0

    def test_disagree_analysis_with_eloundou(self):
        model_a = pd.DataFrame({
            "task_id": [1, 2, 3],
            "onet_soc_code": ["X"] * 3,
            "replication_label": ["E0", "E1", "E2"],
        })
        model_b = pd.DataFrame({
            "task_id": [1, 2, 3],
            "onet_soc_code": ["X"] * 3,
            "replication_label": ["E0", "E2", "E1"],  # disagrees on tasks 2,3
        })
        eloundou = pd.DataFrame({
            "task_id": [1, 2, 3],
            "onet_soc_code": ["X"] * 3,
            "gpt4_exposure": ["E0", "E1", "E2"],  # model_a is right on both
        })
        metrics = compare_two_models(model_a, model_b, eloundou=eloundou)
        assert "disagree_analysis" in metrics
        da = metrics["disagree_analysis"]
        assert da["n_disagree"] == 2
        assert da["a_correct"] == 2
        assert da["b_correct"] == 0

    def test_only_shared_tasks_compared(self):
        model_a = pd.DataFrame({
            "task_id": [1, 2, 3],
            "onet_soc_code": ["X"] * 3,
            "replication_label": ["E0", "E1", "E2"],
        })
        model_b = pd.DataFrame({
            "task_id": [2, 3, 4],
            "onet_soc_code": ["X"] * 3,
            "replication_label": ["E1", "E2", "E0"],
        })
        metrics = compare_two_models(model_a, model_b)
        assert metrics["n_tasks"] == 2  # only tasks 2,3 overlap
        assert metrics["agreement"] == 1.0
