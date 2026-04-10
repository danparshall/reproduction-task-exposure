# Eloundou Replication Comparison

## Comparison vs gpt4_exposure

**Tasks matched:** 18728
**Accuracy:** 57.0%
**Cohen's kappa:** 0.379

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 6836 | 1210 | 160 |
| **E1** | 243 | 2219 | 195 |
| **E2** | 1558 | 4680 | 1627 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.791 | 0.833 |
| E1 | 0.274 | 0.835 |
| E2 | 0.821 | 0.207 |

---

## Comparison vs gpt4_exposure_alt_rubric

**Tasks matched:** 18728
**Accuracy:** 57.1%
**Cohen's kappa:** 0.338

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 7795 | 2443 | 586 |
| **E1** | 215 | 1783 | 289 |
| **E2** | 627 | 3883 | 1107 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.903 | 0.720 |
| E1 | 0.220 | 0.780 |
| E2 | 0.559 | 0.197 |

---

## Comparison vs human_exposure_agg

**Tasks matched:** 18728
**Accuracy:** 56.9%
**Cohen's kappa:** 0.344

### Confusion Matrix (rows=Eloundou, cols=Replication)

|  | Pred E0 | Pred E1 | Pred E2 |
|---|---|---|---|
| **E0** | 7280 | 2032 | 557 |
| **E1** | 246 | 2261 | 313 |
| **E2** | 1111 | 3816 | 1112 |

### Per-Class Metrics

| Label | Precision | Recall |
|---|---|---|
| E0 | 0.843 | 0.738 |
| E1 | 0.279 | 0.802 |
| E2 | 0.561 | 0.184 |
