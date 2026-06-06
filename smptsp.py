# smptsp.py
# Instance and Solution classes for the SMPTSP problem.

import os


class Instance:
    def __init__(self, name, jobs, Qw):
        # jobs: list of (start, end) tuples
        # Qw:   list of lists, Qw[w] = task indices worker w is qualified for
        self.name = name
        self.J = len(jobs)
        self.W = len(Qw)
        self.jobs = jobs
        self.Qw = Qw

        # Wj[j] = list of workers qualified for task j
        self.Wj = [[] for _ in range(self.J)]
        for w in range(self.W):
            for j in Qw[w]:
                self.Wj[j].append(w)

        # overlap[j] = set of tasks that conflict in time with task j
        self.overlap = [set() for _ in range(self.J)]
        for i in range(self.J):
            si, ei = jobs[i]
            for k in range(i + 1, self.J):
                sk, ek = jobs[k]
                if si < ek and sk < ei:        # half-open [s, e) overlap
                    self.overlap[i].add(k)
                    self.overlap[k].add(i)

        # Lower bound = max number of tasks active at any single time point
        events = []
        for s, e in jobs:
            events.append((s, +1))
            events.append((e, -1))
        events.sort()
        cur, mx = 0, 0
        for _, d in events:
            cur += d
            if cur > mx:
                mx = cur
        self.lb = mx

    @classmethod
    def load(cls, path):
        with open(path) as f:
            lines = [ln.strip() for ln in f if ln.strip() and not ln.startswith("#")]
        # lines[0] = "Type = 1"
        J = int(lines[1].split("=")[1])
        jobs = []
        for j in range(J):
            s, e = lines[2 + j].split()
            jobs.append((int(s), int(e)))
        # lines[2 + J] = "Qualifications = W"
        W = int(lines[2 + J].split("=")[1])
        Qw = []
        for w in range(W):
            _, jlist = lines[3 + J + w].split(":")
            Qw.append([int(x) for x in jlist.split()])
        name = os.path.basename(path).replace(".dat", "")
        return cls(name, jobs, Qw)


class Solution:
    def __init__(self, inst):
        self.inst = inst
        self.assign = [-1] * inst.J          # assign[j] = worker doing task j
        self.worker_tasks = {}               # w -> set of tasks at w
        self.active = set()                  # set of active workers
        self.conflicts_at = {}               # w -> number of conflict pairs at w
        self.total_conflicts = 0

    def num_active(self):
        return len(self.active)

    def assign_task(self, j, w):
        """Move task j to worker w (handles incremental conflict bookkeeping)."""
        old = self.assign[j]
        if old == w:
            return
        ov = self.inst.overlap[j]

        # Remove j from old worker
        if old != -1:
            removed = len(ov & self.worker_tasks[old])
            self.conflicts_at[old] -= removed
            self.total_conflicts -= removed
            self.worker_tasks[old].discard(j)
            if not self.worker_tasks[old]:
                self.active.discard(old)

        # Add j to new worker
        if w not in self.worker_tasks:
            self.worker_tasks[w] = set()
            self.conflicts_at[w] = 0
        added = len(ov & self.worker_tasks[w])
        self.conflicts_at[w] += added
        self.total_conflicts += added
        self.worker_tasks[w].add(j)
        self.active.add(w)

        self.assign[j] = w

    def copy(self):
        c = Solution(self.inst)
        c.assign = self.assign[:]
        c.worker_tasks = {w: s.copy() for w, s in self.worker_tasks.items()}
        c.active = self.active.copy()
        c.conflicts_at = self.conflicts_at.copy()
        c.total_conflicts = self.total_conflicts
        return c
