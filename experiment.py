# experiment.py
# Run Tabu Search on the 30 selected SMPTSP instances, 5 seeds each,
# and print + save the results table.

import statistics
import time

from smptsp import Instance
from tabu_search import tabu_search


DATA_DIR = "./ptask"
SEEDS = [0, 1, 2, 3, 4]
TIME_LIMITS = {"small": 5, "medium": 20, "large": 40}    # seconds per seed

# The 30 instances from Phase 2 Table 1.
INSTANCES = [
    ("small",  "data_1_23_40_66"),
    ("small",  "data_2_24_40_33"),
    ("small",  "data_6_48_80_66"),
    ("small",  "data_9_49_104_33"),
    ("small",  "data_10_51_111_66"),
    ("small",  "data_13_25_120_33"),
    ("small",  "data_17_23_139_66"),
    ("small",  "data_21_93_175_33"),
    ("small",  "data_23_74_180_66"),
    ("small",  "data_29_22_219_66"),
    ("medium", "data_33_76_240_66"),
    ("medium", "data_34_152_240_33"),
    ("medium", "data_40_138_360_33"),
    ("medium", "data_41_144_360_66"),
    ("medium", "data_44_121_400_33"),
    ("medium", "data_48_120_434_66"),
    ("medium", "data_62_101_571_33"),
    ("medium", "data_64_176_595_66"),
    ("medium", "data_72_205_624_66"),
    ("medium", "data_74_209_664_33"),
    ("large",  "data_84_136_718_66"),
    ("large",  "data_86_178_721_33"),
    ("large",  "data_90_157_791_66"),
    ("large",  "data_94_93_881_33"),
    ("large",  "data_100_194_956_66"),
    ("large",  "data_104_181_1057_33"),
    ("large",  "data_110_183_1143_66"),
    ("large",  "data_118_180_1302_33"),
    ("large",  "data_136_216_2000_66"),
    ("large",  "data_137_245_2105_33"),
]


def run_instance(inst, time_limit):
    objs = []
    times = []
    for seed in SEEDS:
        best, elapsed = tabu_search(inst, seed=seed, time_limit=time_limit)
        objs.append(best.num_active())
        times.append(elapsed)
        print(f"  seed={seed}: obj={best.num_active()} time={elapsed:.2f}s")
    return objs, times


def main():
    results = []
    grand_start = time.time()

    for i, (tier, name) in enumerate(INSTANCES, 1):
        inst = Instance.load(f"{DATA_DIR}/{name}.dat")
        print(f"[{i}/{len(INSTANCES)}] {tier} {name}  "
              f"J={inst.J} W={inst.W} LB={inst.lb}")
        objs, times = run_instance(inst, TIME_LIMITS[tier])

        mean_obj = statistics.mean(objs)
        best_obj = min(objs)
        std_obj = statistics.stdev(objs)
        mean_time = statistics.mean(times)
        # Time of the seed that achieved the best objective
        best_time = times[objs.index(best_obj)]

        results.append({
            "tier": tier, "instance": name,
            "W": inst.W, "J": inst.J, "LB": inst.lb,
            "mean": mean_obj, "best": best_obj, "std": std_obj,
            "mean_time": mean_time, "best_time": best_time,
            "objs": objs, "times": times,
        })
        print(f"  -> mean={mean_obj:.2f} best={best_obj} "
              f"std={std_obj:.2f} mean_time={mean_time:.2f}s")

    elapsed = time.time() - grand_start

    # Print the final table
    print()
    print("=" * 90)
    print(f"{'Instance':<25} {'W':>4} {'J':>5} {'LB':>4} "
          f"{'Mean':>7} {'Best':>5} {'Std':>6} {'MeanT':>8} {'BestT':>8}")
    print("-" * 90)
    for r in results:
        print(f"{r['instance']:<25} {r['W']:>4} {r['J']:>5} {r['LB']:>4} "
              f"{r['mean']:>7.2f} {r['best']:>5} {r['std']:>6.2f} "
              f"{r['mean_time']:>8.2f} {r['best_time']:>8.2f}")
    print("=" * 90)
    print(f"Total wall-clock time: {elapsed:.1f}s ({elapsed / 60:.1f} min)")

    # Save CSV
    with open("results.csv", "w") as f:
        header = ["tier", "instance", "W", "J", "LB",
                  "mean_obj", "best_obj", "std_obj",
                  "mean_time", "best_time"]
        for s in SEEDS:
            header.append(f"obj_seed_{s}")
            header.append(f"time_seed_{s}")
        f.write(",".join(header) + "\n")
        for r in results:
            row = [r["tier"], r["instance"], r["W"], r["J"], r["LB"],
                   f"{r['mean']:.4f}", r["best"], f"{r['std']:.4f}",
                   f"{r['mean_time']:.4f}", f"{r['best_time']:.4f}"]
            for o, t in zip(r["objs"], r["times"]):
                row.append(str(o))
                row.append(f"{t:.4f}")
            f.write(",".join(str(x) for x in row) + "\n")
    print("Results saved to results.csv")


if __name__ == "__main__":
    main()
