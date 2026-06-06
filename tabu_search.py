# tabu_search.py
# Tabu Search for SMPTSP using the worker-elimination scheme.

import random
import time

from smptsp import Solution


# Algorithm parameters
TABU_TENURE = 12
PHASE_LIMIT = 400        # max inner repair iterations per elimination attempt


def greedy_init(inst, rng):
    """Greedy: process tasks by start time, prefer already-active workers."""
    sol = Solution(inst)
    order = sorted(range(inst.J), key=lambda j: inst.jobs[j][0])
    for j in order:
        chosen = None
        # 1) try active workers with no added conflict
        for w in inst.Wj[j]:
            if w in sol.active and not (inst.overlap[j] & sol.worker_tasks[w]):
                chosen = w
                break
        # 2) otherwise open a new (inactive) qualified worker
        if chosen is None:
            inactive = [w for w in inst.Wj[j] if w not in sol.active]
            if inactive:
                chosen = rng.choice(inactive)
            else:
                # all qualified workers active and full; accept best-conflict spot
                chosen = min(inst.Wj[j],
                             key=lambda w: len(inst.overlap[j] & sol.worker_tasks[w]))
        sol.assign_task(j, chosen)
    return sol


def force_close(sol, target, rng):
    """Move every task currently at `target` to another active qualified worker."""
    for j in list(sol.worker_tasks[target]):
        others = [w for w in sol.inst.Wj[j] if w != target]
        active_others = [w for w in others if w in sol.active]
        if active_others:
            wn = min(active_others,
                     key=lambda w: (len(sol.inst.overlap[j] & sol.worker_tasks[w]),
                                    rng.random()))
        else:
            wn = rng.choice(others)
        sol.assign_task(j, wn)


def repair(sol, forbidden, allowed, rng, deadline, phase_limit):
    """Inner Tabu Search: drive total_conflicts to 0.

    forbidden : worker that must stay inactive (-1 to allow any)
    allowed   : if not None, restrict move destinations to this set
    Returns True if feasibility was restored within the budget.
    """
    tabu = {}                              # (task, worker) -> iter when legal again

    for it in range(1, phase_limit + 1):
        if sol.total_conflicts == 0:
            return True
        if time.time() > deadline:
            return False

        best_move = None
        best_delta = 10 ** 9
        cur = sol.total_conflicts

        # Look at every task involved in a conflict, try every qualified destination.
        for w in list(sol.active):
            if sol.conflicts_at[w] == 0:
                continue
            tasks_w = sol.worker_tasks[w]
            for j in list(tasks_w):
                ov = sol.inst.overlap[j]
                if not (ov & tasks_w):
                    continue                    # j has no conflict at w
                removed = len(ov & tasks_w)
                for wn in sol.inst.Wj[j]:
                    if wn == w or wn == forbidden:
                        continue
                    if allowed is not None and wn not in allowed:
                        continue
                    added = len(ov & sol.worker_tasks.get(wn, set()))
                    delta = added - removed
                    is_tabu = tabu.get((j, wn), 0) > it
                    aspires = (cur + delta == 0)
                    if is_tabu and not aspires:
                        continue
                    if delta < best_delta:
                        best_delta = delta
                        best_move = (j, w, wn)

        if best_move is None:
            return False

        j, w_old, w_new = best_move
        sol.assign_task(j, w_new)
        tabu[(j, w_old)] = it + TABU_TENURE

    return sol.total_conflicts == 0


def tabu_search(inst, seed, time_limit):
    """Main Tabu Search loop. Returns (best_solution, elapsed_seconds)."""
    rng = random.Random(seed)
    start = time.time()
    deadline = start + time_limit

    # Build initial solution; repair if greedy left any conflicts.
    sol = greedy_init(inst, rng)
    if sol.total_conflicts > 0:
        repair(sol, forbidden=-1, allowed=None, rng=rng,
               deadline=deadline, phase_limit=PHASE_LIMIT * 5)

    best = sol.copy()
    blacklist = set()           # targets that recently failed to be eliminated

    while time.time() < deadline and best.num_active() > inst.lb:
        # Refresh candidate list; if all are blacklisted, restart from a
        # fresh greedy (rng has progressed, so we get a different start).
        candidates = [w for w in sol.active if w not in blacklist]
        if not candidates:
            blacklist.clear()
            sol = greedy_init(inst, rng)
            if sol.total_conflicts > 0:
                repair(sol, forbidden=-1, allowed=None, rng=rng,
                       deadline=deadline, phase_limit=PHASE_LIMIT * 5)
            if sol.num_active() < best.num_active():
                best = sol.copy()
            continue

        # Pick the least-loaded active worker as elimination target.
        target = min(candidates, key=lambda w: len(sol.worker_tasks[w]))
        snapshot = sol.copy()

        force_close(sol, target, rng)
        allowed = set(snapshot.active) - {target}

        ok = repair(sol, forbidden=target, allowed=allowed,
                    rng=rng, deadline=deadline, phase_limit=PHASE_LIMIT)
        # Only count it as a real success if the active count actually went down.
        # (force_close may have had to open a previously-inactive worker because
        # the moved task was qualified for `target` only or for inactive workers;
        # then we close one but open another and gain nothing.)
        if ok and sol.num_active() < snapshot.num_active():
            best = sol.copy()
            blacklist.clear()
        else:
            sol = snapshot
            blacklist.add(target)

    return best, time.time() - start
