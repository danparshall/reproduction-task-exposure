# Rename rounds from r1/r2 to i-round/c-round

**Date:** 2026-04-12
**Branch:** rename-rounds

## Summary

This session eliminated a naming collision that plagued every conversation about the codebase. The pipeline uses two rounds — an initial independent classification and a consensus dispute-resolution round — which were internally called "r1/r2." But "R" is also an axis in the CDR framework (Regulatory restrictions, levels R0-R4), so "R1" was ambiguous: pipeline round 1 or R-axis level 1?

We audited the full codebase via subagent, identified every round reference (distinguishing from R-axis references), wrote a plan, then implemented using TDD: 23 tests written first (RED), all passing after implementation (GREEN). The rename touched code, CLI flags, published CSV files/headers, metadata JSON, and all documentation.

## Topics Explored
- Full audit of r1/r2 usage across the codebase (code, data, docs)
- Distinguishing round references from R-axis level references
- Three-way naming collision: pipeline rounds, R-axis levels, and Eloundou rubric variants
- Backward compatibility for legacy `_r2` filenames

## Decisions Made
- **Code internals:** `r1` → `ir`, `r2` → `cr` (e.g., `build_cr_prompt()`, `merge_ir_cr()`)
- **CLI:** `--round 1/2` → `--round initial/consensus`; `--r1-only` → `--ir-only`
- **Files:** `consensus_r2.csv` → `consensus_cr.csv`; `disputed_r2.csv` → `disputed_cr.csv`
- **CSV columns:** `_r1` suffix → `_ir` in published data headers
- **Docs:** Use "initial round (i-round)" / "consensus round (c-round)" consistently
- **Eloundou tests:** `metrics_r1`/`metrics_r2` → `metrics_rub1`/`metrics_rub2` (rubric variants, not rounds)
- **Backward compat:** `compare_results.py` tries `_cr` → `_r2` → plain filenames
- Plan doc: [20260412_rename_rounds_ir_cr](../plans/20260412_rename_rounds_ir_cr.md)

## Results
- No analysis results — this was a mechanical rename
- 23 new tests in `tests/test_round_naming.py`
- 56/56 total tests passing (23 new + 33 existing)

## Open Questions
- None — rename is complete and tested
