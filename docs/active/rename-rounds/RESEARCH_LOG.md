# Research Log: rename-rounds
Created: 2026-04-12
Purpose: Rename r1/r2 round terminology to i-round/c-round to eliminate collision with R-axis levels in CDR framework

## Session: 2026-04-12 — 20260412_rename_rounds_ir_cr
### Topics Explored
- Full codebase audit distinguishing round refs from R-axis refs
- TDD implementation of rename across code, CLI, data files, and docs
- Three-way collision fix (pipeline rounds + R-axis levels + Eloundou rubric variants)

### Provisional Findings
- Rename is mechanical and complete — 23 new tests verify the convention at all integration boundaries
- Backward compat preserved via fallback filename loading in compare_results.py

### Results
- 23 new tests in `tests/test_round_naming.py`, 56/56 total passing

### Next Steps
- Merge to main

## Sessions

| Date | Convo | Summary |
|------|-------|---------|
| 2026-04-12 | [20260412_rename_rounds_ir_cr](convos/20260412_rename_rounds_ir_cr.md) | Initial session — audit scope, write plan, implement rename |

## Plans

| Date | Plan | Originating Convo |
|------|------|-------------------|
| 2026-04-12 | [20260412_rename_rounds_ir_cr](plans/20260412_rename_rounds_ir_cr.md) | [20260412_rename_rounds_ir_cr](convos/20260412_rename_rounds_ir_cr.md) |
