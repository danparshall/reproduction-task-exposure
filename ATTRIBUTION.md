# Attribution and Data Licensing

## O*NET Database (CC BY 4.0)

This repository includes data from the **O*NET 30.1 Database**, published by the U.S. Department of Labor, Employment and Training Administration (USDOL/ETA). Used under the [Creative Commons Attribution 4.0 International License](https://creativecommons.org/licenses/by/4.0/).

**Files:** `data/onet/*.xlsx`, `data/extracted/onet_tasks_full_18k.csv`

**Source:** [O*NET Resource Center](https://www.onetcenter.org/database.html)

**Modifications:** Subset of 4 files from the full database (Occupation Data, Tasks to DWAs, Abilities, Work Context). Task CSV is a pre-extracted flat file derived from the O*NET Task Statements.

## RAPIDS Apprenticeship Crosswalk (CC BY 4.0)

Apprenticeship data in `data/extracted/occupation_profiles.csv` (columns: `is_apprenticeable`, `rapids_term_hours`) is derived from the O*NET-to-RAPIDS crosswalk published by the [O*NET Resource Center](https://www.onetcenter.org/crosswalks.html), used under CC BY 4.0.

**Source:** U.S. Department of Labor, Employment and Training Administration

## Carollo Licensing Data

Licensing data in `data/extracted/occupation_profiles.csv` (columns: `carollo_licensed`, `carollo_n_states`, `carollo_pct`) is a derived aggregation from Nicholas Carollo's occupational licensing dataset.

**Source:** [github.com/ncarollo/licensing-data](https://github.com/ncarollo/licensing-data)

**Paper:** Carollo, N., Hicks, J., Karch, A., & Kleiner, M. M. (2025). "The Origins and Evolution of Occupational Licensing in the United States." NBER Working Paper 33580. [https://www.nber.org/papers/w33580](https://www.nber.org/papers/w33580)

**Note:** The original repository does not include an explicit open-source license. The derivative columns included here are SOC-level aggregations (licensed yes/no, number of states, percentage) — not the raw historical legislation data. Permission to redistribute this derivative has been requested from the author. If you are the rights holder and would like this data removed, please open an issue.
