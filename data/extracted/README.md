# Pre-Extracted Data Files

These CSV files are pre-processed from O*NET and supplementary data sources. They are used directly by the classification pipeline.

## Files

### `onet_tasks_full_18k.csv`
All ~18,796 O*NET tasks across ~923 occupations. Each row contains:
- `task_id` — O*NET task identifier
- `onet_soc_code` — Standard Occupational Classification code (e.g., "29-1141.00")
- `occupation_title` — Human-readable occupation name
- `task_description` — Full task text

### `occupation_profiles.csv`
Pre-built occupation profiles with contextual enrichment. Each row contains:
- O*NET fields: SOC code, title, job zone, top work activities, physical context
- **RAPIDS apprenticeship data:** Whether the occupation has a registered apprenticeship, and term hours
- **Carollo licensing data:** Whether the occupation requires state licensing, and in how many states

The licensing and apprenticeship data directly inform R-axis (Regulatory restrictions) classification. They were pre-compiled from:
- **[RAPIDS](https://www.apprenticeship.gov/help/what-rapids)** (Registered Apprenticeship Partners Information Data System) — U.S. Department of Labor ([dataset catalog](https://catalog.data.gov/dataset/registered-apprenticeship-partners-information-database-system-rapids-dataset))
- **[Carollo Licensing Data](https://github.com/ncarollo/licensing-data)** — Historical occupational licensing across 50 states + DC, from Carollo et al., "The Origins and Evolution of Occupational Licensing in the United States" ([NBER w33580](https://www.nber.org/papers/w33580))
- **[CareerOneStop License Finder](https://www.careeronestop.org/Toolkit/Training/find-licenses.aspx)** — DOL-sponsored state licensing requirements ([overview](https://www.careeronestop.org/ExploreCareers/Plan/licensed-occupations.aspx))
