# Eloundou Replication Comparison

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 65.3%
**Cohen's kappa:** 0.473

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 402 | 19 | 17 |
| **E1** | 17 | 100 | 13 |
| **E2** | 94 | 191 | 158 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.784 | 0.918 |
| E1 | 0.323 | 0.769 |
| E2 | 0.840 | 0.357 |

---

## Comparison vs gpt4_exposure_alt_rubric

**Tasks matched:** 1011
**Accuracy:** 62.7%
**Cohen's kappa:** 0.396

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 459 | 50 | 66 |
| **E1** | 17 | 76 | 23 |
| **E2** | 37 | 184 | 99 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.895 | 0.798 |
| E1 | 0.245 | 0.655 |
| E2 | 0.527 | 0.309 |

---

## Comparison vs human_exposure_agg

**Tasks matched:** 1011
**Accuracy:** 62.6%
**Cohen's kappa:** 0.402

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 433 | 52 | 53 |
| **E1** | 23 | 95 | 30 |
| **E2** | 57 | 163 | 105 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.844 | 0.805 |
| E1 | 0.306 | 0.642 |
| E2 | 0.559 | 0.323 |
