# Eloundou Replication Comparison

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 59.1%
**Cohen's kappa:** 0.409

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 372 | 56 | 10 |
| **E1** | 8 | 115 | 7 |
| **E2** | 85 | 248 | 110 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.800 | 0.849 |
| E1 | 0.274 | 0.885 |
| E2 | 0.866 | 0.248 |

---

## Comparison vs gpt4_exposure_alt_rubric

**Tasks matched:** 1011
**Accuracy:** 57.8%
**Cohen's kappa:** 0.351

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 422 | 110 | 43 |
| **E1** | 8 | 93 | 15 |
| **E2** | 35 | 216 | 69 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.908 | 0.734 |
| E1 | 0.222 | 0.802 |
| E2 | 0.543 | 0.216 |

---

## Comparison vs human_exposure_agg

**Tasks matched:** 1011
**Accuracy:** 58.0%
**Cohen's kappa:** 0.357

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 396 | 108 | 34 |
| **E1** | 13 | 116 | 19 |
| **E2** | 56 | 195 | 74 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.852 | 0.736 |
| E1 | 0.277 | 0.784 |
| E2 | 0.583 | 0.228 |
