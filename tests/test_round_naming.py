"""Tests for round naming convention: i-round/c-round (not r1/r2).

Verifies that the codebase uses 'ir' (initial round) and 'cr' (consensus round)
terminology consistently, avoiding collision with R-axis levels (R0-R4).
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RESULTS_MIDTIER = PROJECT_ROOT / "results" / "data_20260313_midtier"
RESULTS_OLDEST = PROJECT_ROOT / "results" / "data_oldest_available"


# ── CLI flag tests ──────────────────────────────────────────────────────


class TestCLIRoundFlag:
    """The --round flag should accept 'initial'/'consensus', not 1/2."""

    def test_round_initial_accepted(self):
        """--round initial should be accepted by the argument parser."""
        result = subprocess.run(
            [sys.executable, "scripts/classify.py", "--round", "initial", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"--round initial rejected: {result.stderr}"

    def test_round_consensus_accepted(self):
        """--round consensus should be accepted by the argument parser."""
        result = subprocess.run(
            [
                sys.executable,
                "scripts/classify.py",
                "--round",
                "consensus",
                "--dry-run",
            ],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode == 0, f"--round consensus rejected: {result.stderr}"

    def test_round_numeric_1_rejected(self):
        """--round 1 (old convention) should be rejected."""
        result = subprocess.run(
            [sys.executable, "scripts/classify.py", "--round", "1", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode != 0, "--round 1 should be rejected"

    def test_round_numeric_2_rejected(self):
        """--round 2 (old convention) should be rejected."""
        result = subprocess.run(
            [sys.executable, "scripts/classify.py", "--round", "2", "--dry-run"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert result.returncode != 0, "--round 2 should be rejected"


class TestAggregateCLI:
    """The aggregate script should use --ir-only (not --r1-only)."""

    def test_ir_only_flag_accepted(self):
        """--ir-only should be a valid flag."""
        result = subprocess.run(
            [sys.executable, "scripts/aggregate.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert "--ir-only" in result.stdout, f"--ir-only not in help: {result.stdout}"

    def test_r1_only_flag_absent(self):
        """--r1-only (old convention) should not appear in help."""
        result = subprocess.run(
            [sys.executable, "scripts/aggregate.py", "--help"],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
        )
        assert "--r1-only" not in result.stdout, "--r1-only still present in help"


# ── Function naming tests ──────────────────────────────────────────────


class TestFunctionNaming:
    """Key functions should use ir/cr naming, not r1/r2."""

    def test_build_cr_prompt_exists(self):
        """classify.py should define build_cr_prompt (not build_r2_prompt)."""
        # Import the module's namespace by reading the source
        source = (PROJECT_ROOT / "scripts" / "classify.py").read_text()
        assert "def build_cr_prompt(" in source, (
            "build_cr_prompt not found in classify.py"
        )
        assert "def build_r2_prompt(" not in source, (
            "build_r2_prompt still present in classify.py"
        )

    def test_merge_ir_cr_exists(self):
        """aggregate.py should define merge_ir_cr (not merge_r1_r2)."""
        source = (PROJECT_ROOT / "scripts" / "aggregate.py").read_text()
        assert "def merge_ir_cr(" in source, "merge_ir_cr not found in aggregate.py"
        assert "def merge_r1_r2(" not in source, (
            "merge_r1_r2 still present in aggregate.py"
        )


# ── Checkpoint directory naming ────────────────────────────────────────


class TestCheckpointNaming:
    """C-round checkpoint dirs should use _cr suffix, not _r2."""

    def test_cr_suffix_in_classify(self):
        """classify.py should append '_cr' for consensus round checkpoints."""
        source = (PROJECT_ROOT / "scripts" / "classify.py").read_text()
        assert '"_cr"' in source or "'_cr'" in source, (
            "_cr suffix not found in classify.py"
        )
        # The old _r2 suffix should not appear (except possibly in comments about the change)
        # Check the actual checkpoint_dir assignment line
        assert 'checkpoint_dir + "_r2"' not in source, (
            "_r2 checkpoint suffix still in classify.py"
        )

    def test_cr_suffix_in_aggregate(self):
        """aggregate.py should look for _cr checkpoint dirs."""
        source = (PROJECT_ROOT / "scripts" / "aggregate.py").read_text()
        assert '"_cr"' in source or "'_cr'" in source, (
            "_cr suffix not found in aggregate.py"
        )
        assert 'checkpoint_dir}_r2"' not in source, (
            "_r2 checkpoint suffix still in aggregate.py"
        )


# ── Published result file naming ───────────────────────────────────────


class TestPublishedFileNames:
    """Published result files should use _cr naming."""

    def test_midtier_consensus_cr_exists(self):
        path = RESULTS_MIDTIER / "consensus_cr.csv"
        assert path.exists(), f"Expected {path} (was consensus_r2.csv)"

    def test_midtier_disputed_cr_exists(self):
        path = RESULTS_MIDTIER / "disputed_cr.csv"
        assert path.exists(), f"Expected {path} (was disputed_r2.csv)"

    def test_oldest_consensus_cr_exists(self):
        path = RESULTS_OLDEST / "consensus_cr.csv"
        assert path.exists(), f"Expected {path} (was consensus_r2.csv)"

    def test_oldest_disputed_cr_exists(self):
        path = RESULTS_OLDEST / "disputed_cr.csv"
        assert path.exists(), f"Expected {path} (was disputed_r2.csv)"

    def test_old_r2_files_gone(self):
        """Old _r2 filenames should not exist alongside new _cr ones."""
        for d in [RESULTS_MIDTIER, RESULTS_OLDEST]:
            assert not (d / "consensus_r2.csv").exists(), (
                f"Legacy consensus_r2.csv still in {d}"
            )
            assert not (d / "disputed_r2.csv").exists(), (
                f"Legacy disputed_r2.csv still in {d}"
            )


# ── CSV column headers ─────────────────────────────────────────────────


class TestCSVColumnHeaders:
    """Published CSVs should use _ir column suffix, not _r1."""

    def test_midtier_consensus_uses_ir_columns(self):
        """Column headers like sonnet_C_r1 should be sonnet_C_ir."""
        path = RESULTS_MIDTIER / "consensus_cr.csv"
        if not path.exists():
            pytest.skip("consensus_cr.csv not yet renamed")
        with open(path) as f:
            headers = f.readline().strip().split(",")
        ir_cols = [h for h in headers if h.endswith("_ir")]
        r1_cols = [h for h in headers if h.endswith("_r1")]
        assert len(ir_cols) > 0, f"No _ir columns found in headers: {headers}"
        assert len(r1_cols) == 0, f"Legacy _r1 columns still present: {r1_cols}"

    def test_midtier_disputed_uses_ir_columns(self):
        path = RESULTS_MIDTIER / "disputed_cr.csv"
        if not path.exists():
            pytest.skip("disputed_cr.csv not yet renamed")
        with open(path) as f:
            headers = f.readline().strip().split(",")
        r1_cols = [h for h in headers if h.endswith("_r1")]
        assert len(r1_cols) == 0, f"Legacy _r1 columns still present: {r1_cols}"


# ── Backward compatibility in compare_results.py ──────────────────────


class TestCompareResultsBackwardCompat:
    """compare_results.py should try _cr filenames first, fall back to _r2."""

    def test_load_results_finds_cr_files(self, tmp_path):
        """Should load from consensus_cr.csv when present."""
        # Create a minimal consensus_cr.csv
        csv_path = tmp_path / "consensus_cr.csv"
        csv_path.write_text("task_id,consensus_C\ntask1,C2\n")

        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            # We need to import load_results from compare_results
            import importlib

            spec = importlib.util.spec_from_file_location(
                "compare_results", PROJECT_ROOT / "scripts" / "compare_results.py"
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            results = mod.load_results(tmp_path)
            assert "task1" in results, f"load_results didn't find task1: {results}"
        finally:
            sys.path.pop(0)

    def test_load_results_falls_back_to_r2(self, tmp_path):
        """Should fall back to consensus_r2.csv for legacy data."""
        csv_path = tmp_path / "consensus_r2.csv"
        csv_path.write_text("task_id,consensus_C\nlegacy1,C1\n")

        sys.path.insert(0, str(PROJECT_ROOT / "scripts"))
        try:
            import importlib

            spec = importlib.util.spec_from_file_location(
                "compare_results_fallback",
                PROJECT_ROOT / "scripts" / "compare_results.py",
            )
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            results = mod.load_results(tmp_path)
            assert "legacy1" in results, (
                f"load_results didn't fall back to _r2: {results}"
            )
        finally:
            sys.path.pop(0)


# ── Metadata JSON ─────────────────────────────────────────────────────


class TestMetadataJSON:
    """Metadata files should use i-round/c-round terminology."""

    def test_midtier_metadata_round_value(self):
        path = RESULTS_MIDTIER / "run_metadata.json"
        data = json.loads(path.read_text())
        # Should be "consensus" not 2
        assert data.get("round") != 2, 'Metadata still has "round": 2'
        assert data.get("round") == "consensus", (
            f'Expected "consensus", got {data.get("round")}'
        )

    def test_oldest_metadata_no_r1_r2_keys(self):
        path = RESULTS_OLDEST / "run_metadata.json"
        text = path.read_text()
        # Should not have keys/values like "n_tasks_r2" or "R1 + R2"
        assert "n_tasks_r2" not in text, 'Metadata still has "n_tasks_r2" key'
        assert '"R1 ' not in text, 'Metadata still references "R1" as round'


# ── Aggregate output naming ───────────────────────────────────────────


class TestAggregateOutputNaming:
    """aggregate.py should produce _cr suffixed files, not _r2."""

    def test_suffix_logic(self):
        """The suffix variable should be '_cr' not '_r2' for two-round runs."""
        source = (PROJECT_ROOT / "scripts" / "aggregate.py").read_text()
        # The line that sets the suffix should use _cr
        assert '"_cr"' in source or "'_cr'" in source, "_cr suffix not in aggregate.py"
        # Should not generate _r2 filenames
        assert (
            'f"consensus{suffix}.csv"' in source
            or 'f"consensus{suffix}.csv"' in source
            or 'f"consensus' in source
        )


# ── Eloundou rubric variable naming ──────────────────────────────────


class TestEloundouRubricNaming:
    """Eloundou test variables should use rub1/rub2 (not r1/r2)."""

    def test_metrics_rub_naming(self):
        """metrics_r1/metrics_r2 should be renamed to metrics_rub1/metrics_rub2."""
        source = (
            PROJECT_ROOT / "eloundou" / "tests" / "test_replication.py"
        ).read_text()
        assert "metrics_rub1" in source, "metrics_rub1 not found in test_replication.py"
        assert "metrics_rub2" in source, "metrics_rub2 not found in test_replication.py"
        assert "metrics_r1" not in source, (
            "metrics_r1 still present in test_replication.py"
        )
        assert "metrics_r2" not in source, (
            "metrics_r2 still present in test_replication.py"
        )
