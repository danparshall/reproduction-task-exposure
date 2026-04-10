# Eloundou Replication Comparison

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 56.5%
**Cohen's kappa:** 0.363

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 412 | 23 | 3 |
| **E1** | 18 | 112 | 0 |
| **E2** | 144 | 252 | 47 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.718 | 0.941 |
| E1 | 0.289 | 0.862 |
| E2 | 0.940 | 0.106 |

---

## Comparison vs gpt4_exposure_alt_rubric

**Tasks matched:** 1011
**Accuracy:** 61.1%
**Cohen's kappa:** 0.371

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 488 | 78 | 9 |
| **E1** | 15 | 95 | 6 |
| **E2** | 71 | 214 | 35 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.850 | 0.849 |
| E1 | 0.245 | 0.819 |
| E2 | 0.700 | 0.109 |

---

## Comparison vs human_exposure_agg

**Tasks matched:** 1011
**Accuracy:** 58.4%
**Cohen's kappa:** 0.335

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 448 | 80 | 10 |
| **E1** | 24 | 113 | 11 |
| **E2** | 102 | 194 | 29 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.780 | 0.833 |
| E1 | 0.292 | 0.764 |
| E2 | 0.580 | 0.089 |

---

# gpt-4-turbo-2024-04-09-per-task-strat50

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 72.7%
**Cohen's kappa:** 0.557

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 429 | 4 | 5 |
| **E1** | 27 | 88 | 15 |
| **E2** | 147 | 78 | 218 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.711 | 0.979 |
| E1 | 0.518 | 0.677 |
| E2 | 0.916 | 0.492 |

---

## gpt-4-turbo-2024-04-09 vs gpt-4-turbo-2024-04-09-per-task-strat50

**Tasks compared:** 1014
**Agreement:** 70.1%
**Cohen's kappa:** 0.490

### Label Distributions

| Label | gpt-4-turbo-2024-04-09 | gpt-4-turbo-2024-04-09-per-task-strat50 |
|---|---|---|
| E0 | 574 | 605 |
| E1 | 390 | 171 |
| E2 | 50 | 238 |

### Confusion Matrix (rows=gpt-4-turbo-2024-04-09, cols=gpt-4-turbo-2024-04-09-per-task-strat50)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 522 | 11 | 41 |
| **E1** | 70 | 156 | 164 |
| **E2** | 13 | 4 | 33 |

### Disagreement Analysis (vs Eloundou)

On 301 disagreements:
- gpt-4-turbo-2024-04-09 correct: 47
- gpt-4-turbo-2024-04-09-per-task-strat50 correct: 211
- Neither correct: 43
