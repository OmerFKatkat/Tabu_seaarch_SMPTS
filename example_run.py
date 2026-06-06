# example_run.py
# Sanity check on the 6-task / 5-worker example from Phase 2, Section 4.
# Known optimum = 3 active workers.

from smptsp import Instance
from tabu_search import tabu_search


# Build the Phase-2 toy instance directly (no file needed).
jobs = [
    (0, 4),    # J1
    (2, 6),    # J2
    (5, 9),    # J3
    (7, 10),   # J4
    (1, 5),    # J5
    (6, 8),    # J6
]
Qw = [
    [0, 2, 5],     # W1 qualified for J1, J3, J6
    [1, 3],        # W2 qualified for J2, J4
    [0, 4, 5],     # W3 qualified for J1, J5, J6
    [1, 2, 3],     # W4 qualified for J2, J3, J4
    [3, 4, 5],     # W5 qualified for J4, J5, J6
]
inst = Instance("example", jobs, Qw)

print(f"Example instance: J={inst.J}, W={inst.W}, LB={inst.lb}")
print(f"Known optimum (from Phase 2 report) = 3")
print()

for seed in range(5):
    best, elapsed = tabu_search(inst, seed=seed, time_limit=2)
    status = "OPT" if best.num_active() == 3 else "not optimal"
    print(f"seed={seed}: active={best.num_active()} [{status}] "
          f"time={elapsed * 1000:.1f}ms")

    # Print the schedule
    per_w = {}
    for j, w in enumerate(best.assign):
        per_w.setdefault(w, []).append(j)
    for w in sorted(per_w):
        tasks = sorted(per_w[w])
        print(f"  W{w + 1} -> " + ", ".join(f"J{j + 1}" for j in tasks))
