# Eloundou Replication Comparison

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 68.8%
**Cohen's kappa:** 0.521

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 390 | 31 | 17 |
| **E1** | 10 | 92 | 28 |
| **E2** | 69 | 160 | 214 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.832 | 0.890 |
| E1 | 0.325 | 0.708 |
| E2 | 0.826 | 0.483 |

---

## Comparison vs gpt4_exposure_alt_rubric

**Tasks matched:** 1011
**Accuracy:** 66.5%
**Cohen's kappa:** 0.462

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 442 | 59 | 74 |
| **E1** | 13 | 74 | 29 |
| **E2** | 14 | 150 | 156 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.942 | 0.769 |
| E1 | 0.261 | 0.638 |
| E2 | 0.602 | 0.487 |

---

## Comparison vs human_exposure_agg

**Tasks matched:** 1011
**Accuracy:** 64.4%
**Cohen's kappa:** 0.435

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 410 | 62 | 66 |
| **E1** | 14 | 91 | 43 |
| **E2** | 45 | 130 | 150 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.874 | 0.762 |
| E1 | 0.322 | 0.615 |
| E2 | 0.579 | 0.462 |

---

# gpt-5.4-per-occ-strat50-runB

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 68.2%
**Cohen's kappa:** 0.513

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 388 | 35 | 15 |
| **E1** | 11 | 91 | 28 |
| **E2** | 71 | 161 | 211 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.826 | 0.886 |
| E1 | 0.317 | 0.700 |
| E2 | 0.831 | 0.476 |

---

## gpt-5.4-per-occ-strat50 vs gpt-5.4-per-occ-strat50-runB

**Tasks compared:** 1014
**Agreement:** 95.1%
**Cohen's kappa:** 0.923

### Label Distributions

| Label | gpt-5.4-per-occ-strat50 | gpt-5.4-per-occ-strat50-runB |
|---|---|---|
| E0 | 470 | 471 |
| E1 | 284 | 288 |
| E2 | 260 | 255 |

### Confusion Matrix (rows=gpt-5.4-per-occ-strat50, cols=gpt-5.4-per-occ-strat50-runB)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 458 | 4 | 8 |
| **E1** | 1 | 271 | 12 |
| **E2** | 12 | 13 | 235 |

### Disagreement Analysis (vs Eloundou)

On 50 disagreements:
- gpt-5.4-per-occ-strat50 correct: 27
- gpt-5.4-per-occ-strat50-runB correct: 21
- Neither correct: 2
