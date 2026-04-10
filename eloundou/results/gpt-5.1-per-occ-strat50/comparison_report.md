# Eloundou Replication Comparison

## Comparison vs gpt4_exposure

**Tasks matched:** 1011
**Accuracy:** 57.7%
**Cohen's kappa:** 0.402

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 370 | 50 | 18 |
| **E1** | 10 | 112 | 8 |
| **E2** | 35 | 307 | 101 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.892 | 0.845 |
| E1 | 0.239 | 0.862 |
| E2 | 0.795 | 0.228 |

---

## Comparison vs gpt4_exposure_alt_rubric

**Tasks matched:** 1011
**Accuracy:** 54.4%
**Cohen's kappa:** 0.323

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 401 | 123 | 51 |
| **E1** | 7 | 91 | 18 |
| **E2** | 7 | 255 | 58 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.966 | 0.697 |
| E1 | 0.194 | 0.784 |
| E2 | 0.457 | 0.181 |

---

## Comparison vs human_exposure_agg

**Tasks matched:** 1011
**Accuracy:** 55.9%
**Cohen's kappa:** 0.345

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 382 | 108 | 48 |
| **E1** | 6 | 123 | 19 |
| **E2** | 27 | 238 | 60 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.920 | 0.710 |
| E1 | 0.262 | 0.831 |
| E2 | 0.472 | 0.185 |
