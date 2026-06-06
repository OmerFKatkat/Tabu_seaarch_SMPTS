# Tabu Search for SMPTSP — CSE480/586 Phase 3

**Author:** Ömer Faruk Katkat  
**Team ID:** 11  
**Course:** CSE480/586 Algorithms and Operation Research, Spring 2026

This package implements a Tabu Search metaheuristic for the Shift
Minimization Personnel Task Scheduling Problem (SMPTSP), evaluated on
30 instances from the OR-Library benchmark.

---

## Files

| File              | Purpose                                                      |
|-------------------|--------------------------------------------------------------|
| `smptsp.py`       | `Instance` (parses `.dat` files) and `Solution` data classes |
| `tabu_search.py`  | The Tabu Search algorithm (outer elimination loop + inner repair) |
| `example_run.py`  | Correctness check on the 6-task / 5-worker example from §4 of the report |
| `experiment.py`   | Runs the algorithm on all 30 selected instances × 5 seeds and produces `results.csv` |

---

## Requirements

- Python 3.10 or newer (developed and tested on Python 3.14.3)
- No external libraries — the standard library is sufficient

---

## How to Run

### 1. Place the benchmark data

The OR-Library `.dat` files must be in a folder named `ptask` next to the
Python files:

```
.
├── smptsp.py
├── tabu_search.py
├── example_run.py
├── experiment.py
└── ptask/
    ├── data_1_23_40_66.dat
    ├── data_2_24_40_33.dat
    └── ...
```

### 2. Sanity check on the Phase-2 example

```
python example_run.py
```

Expected output: all five seeds return `active=3` (the known optimum) with
valid schedules. This run takes less than a second.

### 3. Full experiment on the 30 benchmark instances

```
python experiment.py
```

This runs Tabu Search on every selected instance with 5 different random
seeds. Total wall-clock time is approximately 30–50 minutes on an Apple M3.
A progress line is printed for every seed. At the end, the per-instance
summary table is printed and the same data is saved to `results.csv`.

---

## Algorithm Parameters

All parameters are defined as constants at the top of the relevant files
and can be edited directly:

| Constant                     | Default | File              |
|------------------------------|---------|-------------------|
| `TABU_TENURE`                | 12      | `tabu_search.py`  |
| `PHASE_LIMIT`                | 400     | `tabu_search.py`  |
| `SEEDS`                      | `[0,1,2,3,4]` | `experiment.py` |
| `TIME_LIMITS["small"]`       | 5 s     | `experiment.py`  |
| `TIME_LIMITS["medium"]`      | 20 s    | `experiment.py`  |
| `TIME_LIMITS["large"]`       | 40 s    | `experiment.py`  |
| `DATA_DIR`                   | `./ptask` | `experiment.py` |