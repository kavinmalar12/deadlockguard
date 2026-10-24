"""
Discrete-Event Deadlock Simulator for DeadlockGuard (Module 1: Live Lab).
Models processes and resources interacting under different workload patterns.
"""

import random
from typing import Dict, List, Optional, Set, Tuple
from rag import ResourceAllocationGraph
from recovery import RecoveryEngine, CostConfig


class Process:
    def __init__(self, pid: str, priority: int = 2, total_steps: int = 15):
        self.pid = pid
        self.priority = priority
        self.current_step = 0
        self.total_steps = total_steps
        self.checkpoint_step = 0
        self.held_resources: Set[str] = set()
        self.requested_resource: Optional[str] = None
        self.preempt_count = 0
        self.status = "READY"  # READY, RUNNING, WAITING, DEADLOCKED, FINISHED, TERMINATED

    @property
    def progress(self) -> float:
        return min(1.0, round(self.current_step / max(1, self.total_steps), 2))

    def to_dict(self) -> dict:
        return {
            "name": self.pid,
            "priority": self.priority,
            "progress": self.progress,
            "step": self.current_step,
            "total_steps": self.total_steps,
            "checkpoint_step": self.checkpoint_step,
            "preempt_count": self.preempt_count,
            "status": self.status,
            "held_resources": list(self.held_resources),
            "requested_resource": self.requested_resource,
        }


class DeadlockSimulator:
    def __init__(
        self,
        num_processes: int = 4,
        num_resources: int = 4,
        workload_type: str = "circular_wait",
        seed: Optional[int] = 42,
    ):
        self.num_processes = num_processes
        self.num_resources = num_resources
        self.workload_type = workload_type
        self.seed = seed
        self.tick = 0
        self.is_deadlocked = False
        self.deadlock_info: Optional[dict] = None
        self.event_log: List[dict] = []
        self.processes: Dict[str, Process] = {}
        self.resource_holders: Dict[str, Optional[str]] = {}
        self.resource_holding_ticks: Dict[str, int] = {}
        self.rag = ResourceAllocationGraph()
        self.recovery_engine = RecoveryEngine()

        self.reset(seed)

    def log_event(self, action: str, details: str, severity: str = "info"):
        self.event_log.append({
            "tick": self.tick,
            "action": action,
            "details": details,
            "severity": severity,
        })
        # Keep recent 100 events
        if len(self.event_log) > 100:
            self.event_log.pop(0)

    def reset(self, seed: Optional[int] = None):
        if seed is not None:
            self.seed = seed
            random.seed(seed)

        self.tick = 0
        self.is_deadlocked = False
        self.deadlock_info = None
        self.event_log = []
        self.processes = {}
        self.resource_holders = {}
        self.resource_holding_ticks = {}
        self.rag = ResourceAllocationGraph()

        # Initialize Resources
        for r_idx in range(self.num_resources):
            rid = f"R{r_idx}"
            self.resource_holders[rid] = None
            self.resource_holding_ticks[rid] = 0
            self.rag.add_resource(rid)

        # Initialize Processes
        priorities = [1, 2, 3, 4, 5]
        for p_idx in range(self.num_processes):
            pid = f"P{p_idx}"
            prio = priorities[p_idx % len(priorities)]
            total = random.randint(12, 20)
            proc = Process(pid=pid, priority=prio, total_steps=total)
            self.processes[pid] = proc
            self.rag.add_process(pid, priority=prio, progress=0.0)

        self.log_event("SYSTEM_START", f"Initialized {self.num_processes} processes and {self.num_resources} resources ({self.workload_type})")

        # Setup initial workload pattern
        self._setup_workload()

    def _setup_workload(self):
        """Prepare workload scenario so deadlocks form intuitively."""
        p_ids = list(self.processes.keys())
        r_ids = list(self.resource_holders.keys())

        if self.workload_type == "circular_wait":
            # Dining philosophers / circular wait:
            # P_i holds R_i, and will later request R_{(i+1)%n}
            count = min(len(p_ids), len(r_ids))
            for i in range(count):
                pid = p_ids[i]
                rid = r_ids[i]
                self._grant_resource(pid, rid)
                self.processes[pid].current_step = (i + 1) * 2
                self.processes[pid].checkpoint_step = max(0, self.processes[pid].current_step - 2)

        elif self.workload_type == "bank_transaction":
            # Two transactions swap accounts: P0 holds R0, wants R1; P1 holds R1, wants R0
            if len(p_ids) >= 2 and len(r_ids) >= 2:
                self._grant_resource(p_ids[0], r_ids[0])
                self._grant_resource(p_ids[1], r_ids[1])
                self.processes[p_ids[0]].current_step = 6
                self.processes[p_ids[0]].checkpoint_step = 4
                self.processes[p_ids[1]].current_step = 3
                self.processes[p_ids[1]].checkpoint_step = 2

        elif self.workload_type == "high_contention":
            # Multiple processes immediately grab first few resources
            for i in range(min(len(p_ids), len(r_ids))):
                self._grant_resource(p_ids[i], r_ids[i % len(r_ids)])
                self.processes[p_ids[i]].current_step = random.randint(2, 6)

    def _grant_resource(self, pid: str, rid: str):
        self.resource_holders[rid] = pid
        self.resource_holding_ticks[rid] = 1
        self.processes[pid].held_resources.add(rid)
        if self.processes[pid].requested_resource == rid:
            self.processes[pid].requested_resource = None
            self.processes[pid].status = "RUNNING"
        self.rag.allocate(rid, pid)
        self.log_event("ALLOCATE", f"{pid} acquired {rid}")

    def _release_resource(self, pid: str, rid: str):
        if rid in self.processes[pid].held_resources:
            self.processes[pid].held_resources.remove(rid)
        if self.resource_holders.get(rid) == pid:
            self.resource_holders[rid] = None
            self.resource_holding_ticks[rid] = 0
        self.rag.release(rid, pid)
        self.log_event("RELEASE", f"{pid} released {rid}")

    def step(self) -> bool:
        """
        Advance the simulation by one discrete tick.
        Returns True if simulation is ongoing, False if deadlocked or finished.
        """
        if self.is_deadlocked:
            return False

        self.tick += 1

        # Check if all processes finished
        all_done = all(p.status in ["FINISHED", "TERMINATED"] for p in self.processes.values())
        if all_done:
            self.log_event("COMPLETE", "All processes completed successfully!", "success")
            return False

        p_ids = list(self.processes.keys())
        r_ids = list(self.resource_holders.keys())

        # Advance holding ticks
        for rid in r_ids:
            if self.resource_holders[rid] is not None:
                self.resource_holding_ticks[rid] += 1

        # Workload-specific step logic
        if self.workload_type == "circular_wait":
            # Drive towards circular wait
            count = min(len(p_ids), len(r_ids))
            for i in range(count):
                pid = p_ids[i]
                next_rid = r_ids[(i + 1) % count]
                proc = self.processes[pid]
                if proc.status not in ["FINISHED", "TERMINATED"] and proc.requested_resource is None:
                    # Make the circular request
                    proc.requested_resource = next_rid
                    proc.status = "WAITING"
                    self.rag.request(pid, next_rid)
                    self.log_event("REQUEST", f"{pid} requested {next_rid} (held by {self.resource_holders.get(next_rid, 'none')})", "warning")

        elif self.workload_type == "bank_transaction":
            # P0 requests R1, P1 requests R0
            if len(p_ids) >= 2 and len(r_ids) >= 2:
                if self.processes[p_ids[0]].requested_resource is None:
                    self.processes[p_ids[0]].requested_resource = r_ids[1]
                    self.processes[p_ids[0]].status = "WAITING"
                    self.rag.request(p_ids[0], r_ids[1])
                    self.log_event("REQUEST", f"{p_ids[0]} requests {r_ids[1]}", "warning")
                if self.processes[p_ids[1]].requested_resource is None:
                    self.processes[p_ids[1]].requested_resource = r_ids[0]
                    self.processes[p_ids[1]].status = "WAITING"
                    self.rag.request(p_ids[1], r_ids[0])
                    self.log_event("REQUEST", f"{p_ids[1]} requests {r_ids[0]}", "warning")

        else:
            # Random / High contention workload
            active_procs = [p for p in self.processes.values() if p.status in ["READY", "RUNNING"]]
            if active_procs:
                proc = random.choice(active_procs)
                action = random.choices(["work", "request", "release"], weights=[0.45, 0.40, 0.15])[0]

                if action == "work":
                    proc.current_step += 1
                    # Occasionally take a checkpoint
                    if proc.current_step % 4 == 0:
                        proc.checkpoint_step = proc.current_step
                        self.log_event("CHECKPOINT", f"{proc.pid} established checkpoint at step {proc.checkpoint_step}")
                    if proc.current_step >= proc.total_steps:
                        proc.status = "FINISHED"
                        for held in list(proc.held_resources):
                            self._release_resource(proc.pid, held)
                        self.log_event("FINISH", f"{proc.pid} completed all tasks", "success")

                elif action == "request":
                    available_rids = [r for r in r_ids if r not in proc.held_resources]
                    if available_rids:
                        target_rid = random.choice(available_rids)
                        holder = self.resource_holders.get(target_rid)
                        if holder is None:
                            self._grant_resource(proc.pid, target_rid)
                        else:
                            proc.requested_resource = target_rid
                            proc.status = "WAITING"
                            self.rag.request(proc.pid, target_rid)
                            self.log_event("REQUEST", f"{proc.pid} waiting for {target_rid} (held by {holder})", "warning")

                elif action == "release":
                    if proc.held_resources:
                        rid = random.choice(list(proc.held_resources))
                        self._release_resource(proc.pid, rid)

        # Update process attributes in RAG
        for pid, p in self.processes.items():
            self.rag.add_process(
                pid=pid,
                priority=p.priority,
                progress=p.progress,
                step=p.current_step,
                checkpoint_step=p.checkpoint_step,
                preempt_count=p.preempt_count,
            )

        # Detect deadlocks
        deadlock = self.rag.get_deadlock_details()
        if deadlock:
            self.is_deadlocked = True
            self.deadlock_info = deadlock
            for pid in deadlock["cycle_processes"]:
                if pid in self.processes:
                    self.processes[pid].status = "DEADLOCKED"
            cycle_str = " -> ".join(deadlock["cycle_loop"])
            self.log_event("DEADLOCK_DETECTED", f"Deadlock cycle identified: {cycle_str}", "danger")
            return False

        return True

    def apply_recovery(self, strategy: str, candidate_details: dict) -> bool:
        """
        Execute chosen recovery action:
        - TERMINATE: abort process, release all locks.
        - ROLLBACK: rewind process to checkpoint, release acquired locks.
        - PREEMPT: seize specific resource and reassign to waiter.
        """
        pid = candidate_details.get("process")
        if not pid or pid not in self.processes:
            return False

        proc = self.processes[pid]

        if strategy == "TERMINATE":
            proc.status = "TERMINATED"
            # Release all held locks
            for rid in list(proc.held_resources):
                self._release_resource(pid, rid)
            proc.requested_resource = None
            self.rag.remove_process(pid)
            self.log_event("RECOVERY_APPLIED", f"Terminated {pid}. All locks released.", "success")

        elif strategy == "ROLLBACK":
            # Rewind step to checkpoint
            proc.current_step = proc.checkpoint_step
            proc.status = "READY"
            # Release locks acquired after checkpoint
            for rid in list(proc.held_resources):
                self._release_resource(pid, rid)
            proc.requested_resource = None
            self.log_event("RECOVERY_APPLIED", f"Rolled back {pid} to step {proc.checkpoint_step}.", "success")

        elif strategy == "PREEMPT":
            target_res = candidate_details.get("resource")
            if target_res and target_res in proc.held_resources:
                self._release_resource(pid, target_res)
                proc.preempt_count += 1
                proc.status = "READY"
                self.log_event("RECOVERY_APPLIED", f"Preempted {target_res} from {pid} (preempt count: {proc.preempt_count}).", "success")
            else:
                # Fallback to releasing any held resource
                if proc.held_resources:
                    res = list(proc.held_resources)[0]
                    self._release_resource(pid, res)
                    proc.preempt_count += 1
                    proc.status = "READY"

        # Re-check deadlock
        self.deadlock_info = self.rag.get_deadlock_details()
        if not self.deadlock_info:
            self.is_deadlocked = False
            for p in self.processes.values():
                if p.status == "DEADLOCKED":
                    p.status = "WAITING" if p.requested_resource else "RUNNING"
            self.log_event("DEADLOCK_RESOLVED", "Cycle resolved! System resumed execution.", "success")
            return True
        else:
            self.log_event("DEADLOCK_PARTIAL", "Cycle broken, but secondary cycle remains.", "warning")
            return False
