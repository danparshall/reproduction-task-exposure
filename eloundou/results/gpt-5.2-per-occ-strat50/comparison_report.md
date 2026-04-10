# Eloundou Replication Comparison

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 73.8%
**Cohen's kappa:** 0.580

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 355 | 21 | 62 |
| **E1** | 4 | 75 | 51 |
| **E2** | 27 | 100 | 316 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.920 | 0.811 |
| E1 | 0.383 | 0.577 |
| E2 | 0.737 | 0.713 |

---

## Comparison vs gpt4_exposure_alt_rubric

**Tasks matched:** 1011
**Accuracy:** 64.2%
**Cohen's kappa:** 0.428

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 375 | 40 | 160 |
| **E1** | 5 | 58 | 53 |
| **E2** | 6 | 98 | 216 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.972 | 0.652 |
| E1 | 0.296 | 0.500 |
| E2 | 0.503 | 0.675 |

---

## Comparison vs human_exposure_agg

**Tasks matched:** 1011
**Accuracy:** 63.5%
**Cohen's kappa:** 0.423

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 362 | 39 | 137 |
| **E1** | 8 | 64 | 76 |
| **E2** | 16 | 93 | 216 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.938 | 0.673 |
| E1 | 0.327 | 0.432 |
| E2 | 0.503 | 0.665 |
