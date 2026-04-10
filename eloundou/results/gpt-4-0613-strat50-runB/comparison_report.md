# Eloundou Replication Comparison

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 58.0%
**Cohen's kappa:** 0.389

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 378 | 46 | 14 |
| **E1** | 18 | 104 | 8 |
| **E2** | 84 | 255 | 104 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.787 | 0.863 |
| E1 | 0.257 | 0.800 |
| E2 | 0.825 | 0.235 |

---

## Comparison vs gpt4_exposure_alt_rubric

**Tasks matched:** 1011
**Accuracy:** 56.7%
**Cohen's kappa:** 0.328

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 428 | 101 | 46 |
| **E1** | 13 | 84 | 19 |
| **E2** | 39 | 220 | 61 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.892 | 0.744 |
| E1 | 0.207 | 0.724 |
| E2 | 0.484 | 0.191 |

---

## Comparison vs human_exposure_agg

**Tasks matched:** 1011
**Accuracy:** 57.2%
**Cohen's kappa:** 0.340

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 399 | 102 | 37 |
| **E1** | 16 | 111 | 21 |
| **E2** | 65 | 192 | 68 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.831 | 0.742 |
| E1 | 0.274 | 0.750 |
| E2 | 0.540 | 0.209 |
