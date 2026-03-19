# O*NET Data Files

These files are from the **O*NET 30.1 Database** (Excel format), published by the U.S. Department of Labor.

## Source

- **Publisher:** National Center for O*NET Development, U.S. Department of Labor
- **Version:** O*NET 30.1
- **URL:** https://www.onetcenter.org/database.html
- **License:** Public domain (U.S. government work product)

## Files Used

| File | Records | Purpose |
|------|---------|---------|
| `Occupation Data.xlsx` | ~923 | SOC code to occupation description mapping |
| `Tasks to DWAs.xlsx` | ~42k | Links each O*NET task to its Detailed Work Activities |
| `Abilities.xlsx` | ~48k | Cognitive, physical, sensory, psychomotor abilities per occupation |
| `Work Context.xlsx` | ~27k | Working conditions (indoor/outdoor, physical demands, hazards) |

## How They're Used

The classification pipeline enriches each occupation's prompt with:
1. **Occupation description** — from `Occupation Data.xlsx`
2. **DWA decomposition** — from `Tasks to DWAs.xlsx`, splits compound tasks into atomic units
3. **Top abilities** — from `Abilities.xlsx`, helps calibrate C and D axis ratings
4. **Work context** — from `Work Context.xlsx`, informs D axis (physical/deployment) ratings

See the paper for details on why DWA decomposition matters for classification accuracy.
