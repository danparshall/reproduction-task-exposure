# Eloundou Replication Comparison

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 75.0%
**Cohen's kappa:** 0.596

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 417 | 11 | 10 |
| **E1** | 23 | 78 | 29 |
| **E2** | 87 | 93 | 263 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.791 | 0.952 |
| E1 | 0.429 | 0.600 |
| E2 | 0.871 | 0.594 |

---

## Comparison vs gpt4_exposure_alt_rubric

**Tasks matched:** 1011
**Accuracy:** 73.8%
**Cohen's kappa:** 0.554

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 487 | 22 | 66 |
| **E1** | 19 | 60 | 37 |
| **E2** | 21 | 100 | 199 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.924 | 0.847 |
| E1 | 0.330 | 0.517 |
| E2 | 0.659 | 0.622 |

---

## Comparison vs human_exposure_agg

**Tasks matched:** 1011
**Accuracy:** 68.4%
**Cohen's kappa:** 0.474

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 446 | 28 | 64 |
| **E1** | 18 | 69 | 61 |
| **E2** | 63 | 85 | 177 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.846 | 0.829 |
| E1 | 0.379 | 0.466 |
| E2 | 0.586 | 0.545 |

---

# gpt-5.4-per-task-strat50-runB

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 75.1%
**Cohen's kappa:** 0.597

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 418 | 10 | 10 |
| **E1** | 22 | 79 | 29 |
| **E2** | 91 | 90 | 262 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.787 | 0.954 |
| E1 | 0.441 | 0.608 |
| E2 | 0.870 | 0.591 |

---

## gpt-5.4-per-task-strat50 vs gpt-5.4-per-task-strat50-runB

**Tasks compared:** 1014
**Agreement:** 95.2%
**Cohen's kappa:** 0.920

### Label Distributions

| Label | gpt-5.4-per-task-strat50 | gpt-5.4-per-task-strat50-runB |
|---|---|---|
| E0 | 528 | 533 |
| E1 | 183 | 180 |
| E2 | 303 | 301 |

### Confusion Matrix (rows=gpt-5.4-per-task-strat50, cols=gpt-5.4-per-task-strat50-runB)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 516 | 6 | 6 |
| **E1** | 7 | 165 | 11 |
| **E2** | 10 | 9 | 284 |

### Disagreement Analysis (vs Eloundou)

On 48 disagreements:
- gpt-5.4-per-task-strat50 correct: 21
- gpt-5.4-per-task-strat50-runB correct: 22
- Neither correct: 5
