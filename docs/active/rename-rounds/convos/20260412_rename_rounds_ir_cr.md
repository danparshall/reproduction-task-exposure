# Conversation: Rename rounds from r1/r2 to i-round/c-round

**Date:** 2026-04-12
**Branch:** rename-rounds

## Problem

The codebase uses "r1/r2" to mean "round 1 (initial) / round 2 (consensus)" throughout — variable names, CLI flags, filenames, CSV columns, docs. But "R" is also an axis in the CDR framework (Regulatory restrictions, levels R0-R4). When discussing results, "R1" is ambiguous: does it mean round 1 or R-axis level 1? This has caused confusion in every conversation about the codebase.

## Decisions

1. **Variable/function names:** `r1` → `ir`, `r2` → `cr` (e.g., `build_cr_prompt()`, `merge_ir_cr()`)
2. **CLI flags:** `--round 1/2` → `--round initial/consensus` (human-readable for new researchers)
3. **Output filenames:** `consensus_r2.csv` → `consensus_cr.csv` (rename published files too)
4. **CSV column headers:** `sonnet_C_r1` → `sonnet_C_ir` (update published data)
5. **Docs:** Use "initial round (i-round)" and "consensus round (c-round)" consistently
6. **Convention note:** Add a note about the naming change so any missed references get discovered

## Audit findings

Full audit completed — see plan for scope. Key distinction: all `R0/R1/R2/R3/R4` in prompts.py, profiles.py, and CSV cell values are R-axis levels (NOT rounds) and must NOT be touched.

## Status

Plan written. Implementation pending.
