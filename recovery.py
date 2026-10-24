"""
Recovery Engine for DeadlockGuard.
Calculates costs for the three classic recovery strategies:
1. TERMINATE (Kill): Terminate a deadlocked process to release all its locks.
2. ROLLBACK: Rewind a process to its last safe checkpoint.
3. PREEMPT: Temporarily seize a specific resource from a process and assign it to the waiter.

Also generates transparent plain-English justifications (Innovation A).
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Any


@dataclass
class CostConfig:
    """Configurable cost settings for What-If analysis (Module 3 & Innovation C)."""
    # Terminate (Kill) weights
    kill_base_overhead: float = 5.0
    priority_weight: float = 4.0
    progress_weight: float = 8.0

    # Rollback weights
    rollback_base_overhead: float = 3.0
    rollback_unit_cost: float = 1.2

    # Preempt weights
    preempt_base_cost: float = 2.0
    preempt_holding_rate: float = 0.6
    starvation_factor: float = 2.5


class RecoveryEngine:
    def __init__(self, config: Optional[CostConfig] = None):
        self.config = config or CostConfig()

    def evaluate_terminate(self, process_attrs: dict) -> Tuple[float, dict]:
        """
        Calculate cost to terminate (kill) a process.
        Destroys all work done and incurs transaction abort/restart penalties.
        """
        priority = process_attrs.get("priority", 1)
        progress = float(process_attrs.get("progress", 0.0))
        base = self.config.kill_base_overhead
        prio_cost = priority * self.config.priority_weight
        work_cost = progress * self.config.progress_weight
        total = round(base + prio_cost + work_cost, 2)

        details = {
            "type": "TERMINATE",
            "process": process_attrs.get("name", "unknown"),
            "total_cost": total,
            "breakdown": {
                "base_overhead": base,
                "priority_penalty": round(prio_cost, 2),
                "destroyed_work": round(work_cost, 2),
                "progress_pct": int(progress * 100),
                "priority_level": priority,
            },
        }
        return total, details

    def evaluate_rollback(self, process_attrs: dict) -> Tuple[float, dict]:
        """
        Calculate cost to roll back a process to its latest checkpoint.
        Replays undo logs and loses work since the checkpoint.
        """
        current_step = process_attrs.get("step", 5)
        checkpoint_step = process_attrs.get("checkpoint_step", 1)
        steps_lost = max(1, current_step - checkpoint_step)

        base = self.config.rollback_base_overhead
        rework_cost = steps_lost * self.config.rollback_unit_cost
        priority = process_attrs.get("priority", 1)
        # Higher priority transactions incur slight delay penalty
        delay_cost = priority * 0.4
        total = round(base + rework_cost + delay_cost, 2)

        details = {
            "type": "ROLLBACK",
            "process": process_attrs.get("name", "unknown"),
            "total_cost": total,
            "breakdown": {
                "base_overhead": base,
                "steps_lost": steps_lost,
                "rework_cost": round(rework_cost, 2),
                "priority_delay_cost": round(delay_cost, 2),
                "checkpoint_step": checkpoint_step,
            },
        }
        return total, details

    def evaluate_preempt(self, process_attrs: dict, resource_name: str, holding_time: int = 2) -> Tuple[float, dict]:
        """
        Calculate cost to preempt a specific resource from a process.
        Process is suspended or lock is revoked; starvation penalty increases if repeated.
        """
        preempt_count = process_attrs.get("preempt_count", 0)
        base = self.config.preempt_base_cost
        holding_cost = holding_time * self.config.preempt_holding_rate
        starvation_penalty = preempt_count * self.config.starvation_factor
        total = round(base + holding_cost + starvation_penalty, 2)

        details = {
            "type": "PREEMPT",
            "process": process_attrs.get("name", "unknown"),
            "resource": resource_name,
            "total_cost": total,
            "breakdown": {
                "base_cost": base,
                "holding_overhead": round(holding_cost, 2),
                "starvation_penalty": round(starvation_penalty, 2),
                "preempt_count": preempt_count,
            },
        }
        return total, details

    def evaluate_all_candidates(self, deadlock_info: dict, processes: Dict[str, dict]) -> dict:
        """
        Evaluate all candidate processes and resources within the deadlock cycle.
        Finds the minimum cost for each of the 3 strategies and the overall winner.
        """
        cycle_processes = deadlock_info.get("cycle_processes", [])
        dependencies = deadlock_info.get("dependencies", [])

        # 1. Best TERMINATE candidate in the cycle
        best_term_cost = float("inf")
        best_term_details = None
        for pid in cycle_processes:
            p_attrs = processes.get(pid, {"name": pid, "priority": 1, "progress": 0.5})
            cost, details = self.evaluate_terminate(p_attrs)
            if cost < best_term_cost:
                best_term_cost = cost
                best_term_details = details

        # 2. Best ROLLBACK candidate in the cycle
        best_roll_cost = float("inf")
        best_roll_details = None
        for pid in cycle_processes:
            p_attrs = processes.get(pid, {"name": pid, "priority": 1, "progress": 0.5})
            cost, details = self.evaluate_rollback(p_attrs)
            if cost < best_roll_cost:
                best_roll_cost = cost
                best_roll_details = details

        # 3. Best PREEMPT candidate in the cycle
        best_prmp_cost = float("inf")
        best_prmp_details = None
        for dep in dependencies:
            holder_pid = dep["holder"]
            rid = dep["resource"]
            p_attrs = processes.get(holder_pid, {"name": holder_pid, "priority": 1, "progress": 0.5})
            cost, details = self.evaluate_preempt(p_attrs, rid, holding_time=2)
            if cost < best_prmp_cost:
                best_prmp_cost = cost
                best_prmp_details = details

        # If no dependencies found, fallback to first cycle node
        if best_prmp_details is None and cycle_processes:
            pid = cycle_processes[0]
            p_attrs = processes.get(pid, {"name": pid, "priority": 1, "progress": 0.5})
            best_prmp_cost, best_prmp_details = self.evaluate_preempt(p_attrs, "Resource", 2)

        options = {
            "TERMINATE": (best_term_cost, best_term_details),
            "ROLLBACK": (best_roll_cost, best_roll_details),
            "PREEMPT": (best_prmp_cost, best_prmp_details),
        }

        # Find absolute lowest cost (Oracle / Perfect choice)
        sorted_options = sorted(options.items(), key=lambda x: x[1][0])
        cheapest_strategy, (cheapest_cost, cheapest_details) = sorted_options[0]

        # Generate Plain-English Explanation (Innovation A)
        explanation = self.generate_plain_english_reason(sorted_options)

        return {
            "cheapest_strategy": cheapest_strategy,
            "cheapest_cost": cheapest_cost,
            "cheapest_details": cheapest_details,
            "all_options": {
                "TERMINATE": {"cost": best_term_cost, "details": best_term_details},
                "ROLLBACK": {"cost": best_roll_cost, "details": best_roll_details},
                "PREEMPT": {"cost": best_prmp_cost, "details": best_prmp_details},
            },
            "ranking": [k for k, v in sorted_options],
            "explanation": explanation,
        }

    def generate_plain_english_reason(self, sorted_options: list) -> str:
        """
        Produce a human-readable, explainable reason for the selected recovery action.
        Explains why the winner won and why the other two options were rejected.
        """
        winner_strat, (winner_cost, winner_details) = sorted_options[0]
        second_strat, (second_cost, second_details) = sorted_options[1]
        third_strat, (third_cost, third_details) = sorted_options[2]

        savings_vs_second = round(second_cost - winner_cost, 2)
        pct_savings = round((savings_vs_second / second_cost) * 100, 1) if second_cost > 0 else 0

        winner_proc = winner_details.get("process", "process")

        if winner_strat == "PREEMPT":
            res = winner_details.get("resource", "resource")
            reason = (
                f"**Preempt** {winner_proc} holding {res} (Cost: {winner_cost}). "
                f"Taking this resource away is the cheapest path because lock revocation costs only {winner_cost} "
                f"units. In comparison, Rollback costs {second_cost} (re-executing past checkpoint), and "
                f"Terminating costs {third_cost} (losing all completed work and high priority state). "
                f"Preemption saves {savings_vs_second} cost units ({pct_savings}% cheaper than next best option)."
            )
        elif winner_strat == "ROLLBACK":
            lost = winner_details.get("breakdown", {}).get("steps_lost", 1)
            reason = (
                f"**Rollback** {winner_proc} to its checkpoint (Cost: {winner_cost}). "
                f"The process is only {lost} step(s) ahead of a safe checkpoint, making undo/replay "
                f"significantly cheaper than completely terminating the transaction (Cost: {third_cost}), "
                f"while preemption incurs a higher overhead ({second_cost}) due to starvation and holding time."
            )
        else:  # TERMINATE
            prio = winner_details.get("breakdown", {}).get("priority_level", 1)
            prog = winner_details.get("breakdown", {}).get("progress_pct", 0)
            reason = (
                f"**Terminate** {winner_proc} (Cost: {winner_cost}). "
                f"This process has low priority ({prio}) and has only completed {prog}% of its work, "
                f"meaning aborting it wastes minimal progress. Rolling back is more expensive ({second_cost}) "
                f"due to distant checkpoints, and Preempting repeatedly risks high starvation penalties ({third_cost})."
            )

        return reason
