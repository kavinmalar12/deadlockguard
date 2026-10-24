"""
Dataset Generator for DeadlockGuard.
Generates 6,000 realistic deadlock scenarios across varying cycle lengths,
process priorities, checkpoint distances, and preemption histories.
Evaluates ground-truth costs for TERMINATE, ROLLBACK, and PREEMPT strategies.
"""

import random
from typing import Dict, List, Tuple, Optional
import numpy as np
import pandas as pd
from recovery import RecoveryEngine, CostConfig


DEFAULT_CONFIG = CostConfig(
    kill_base_overhead=3.0,
    priority_weight=2.5,
    progress_weight=8.0,
    rollback_base_overhead=3.2,
    rollback_unit_cost=1.6,
    preempt_base_cost=4.2,
    preempt_holding_rate=0.8,
    starvation_factor=3.2,
)


def generate_deadlock_scenario(
    cycle_length: int,
    rng: random.Random,
    config: Optional[CostConfig] = None,
) -> dict:
    """Simulate a single deadlock cycle with realistic process and resource metadata."""
    cfg = config or DEFAULT_CONFIG
    engine = RecoveryEngine(cfg)

    processes = {}
    dependencies = []
    cycle_processes = [f"P{i}" for i in range(cycle_length)]

    for i in range(cycle_length):
        pid = cycle_processes[i]
        next_pid = cycle_processes[(i + 1) % cycle_length]
        rid = f"R{i}"

        priority = rng.choice([1, 1, 2, 3, 4, 5])
        
        # 22% are early-stage processes (step 1 or 2, 0% to 10% progress, ideal for TERMINATE)
        if rng.random() < 0.22:
            current_step = rng.randint(1, 2)
            total_steps = rng.randint(15, 25)
            checkpoint_step = 0
        else:
            total_steps = rng.randint(10, 25)
            current_step = rng.randint(3, total_steps)
            # Distance to checkpoint
            checkpoint_step = max(0, current_step - rng.choice([1, 2, 3, 5, 8, current_step]))

        progress = round(current_step / total_steps, 2)
        preempt_count = rng.choices([0, 1, 2, 3], weights=[0.55, 0.25, 0.12, 0.08])[0]

        processes[pid] = {
            "name": pid,
            "priority": priority,
            "progress": progress,
            "step": current_step,
            "total_steps": total_steps,
            "checkpoint_step": checkpoint_step,
            "preempt_count": preempt_count,
        }

        dependencies.append({
            "waiter": pid,
            "resource": rid,
            "holder": next_pid,
        })

    deadlock_info = {
        "cycle_processes": cycle_processes,
        "dependencies": dependencies,
    }

    eval_result = engine.evaluate_all_candidates(deadlock_info, processes)

    priorities = [p["priority"] for p in processes.values()]
    progresses = [p["progress"] for p in processes.values()]
    ckpt_dists = [p["step"] - p["checkpoint_step"] for p in processes.values()]
    preempt_counts = [p["preempt_count"] for p in processes.values()]

    c_term = eval_result["all_options"]["TERMINATE"]["cost"]
    c_roll = eval_result["all_options"]["ROLLBACK"]["cost"]
    c_prmp = eval_result["all_options"]["PREEMPT"]["cost"]

    features = {
        "cycle_length": cycle_length,
        "min_priority": min(priorities),
        "max_priority": max(priorities),
        "avg_priority": round(float(np.mean(priorities)), 2),
        "min_progress": min(progresses),
        "max_progress": max(progresses),
        "avg_progress": round(float(np.mean(progresses)), 2),
        "min_checkpoint_distance": min(ckpt_dists),
        "avg_checkpoint_distance": round(float(np.mean(ckpt_dists)), 2),
        "max_preempt_count": max(preempt_counts),
        "avg_preempt_count": round(float(np.mean(preempt_counts)), 2),
        # Telemetry proxy heuristics observable by the operating system / DBMS
        "heuristic_term_proxy": round(min(priorities) * 2.2 + min(progresses) * 7.0, 2),
        "heuristic_roll_proxy": round(min(ckpt_dists) * 1.5, 2),
        "heuristic_prmp_proxy": round(max(preempt_counts) * 2.8, 2),
        "cost_term": c_term,
        "cost_roll": c_roll,
        "cost_prmp": c_prmp,
        "best_fix": eval_result["cheapest_strategy"],
        "oracle_cost": eval_result["cheapest_cost"],
    }
    return features


def generate_dataset(
    num_samples: int = 6000,
    seed: int = 42,
    config: Optional[CostConfig] = None,
) -> pd.DataFrame:
    """Generate dataframe of synthetic deadlock scenarios."""
    rng = random.Random(seed)
    cfg = config or DEFAULT_CONFIG
    rows = []

    cycle_lengths = [2, 2, 2, 3, 3, 4]
    for _ in range(num_samples):
        clen = rng.choice(cycle_lengths)
        row = generate_deadlock_scenario(clen, rng, cfg)
        rows.append(row)

    df = pd.DataFrame(rows)
    return df


if __name__ == "__main__":
    print("Generating 6,000 deadlock cases...")
    df = generate_dataset(6000)
    df.to_csv("dataset.csv", index=False)
    print(f"Dataset saved to dataset.csv with {len(df)} rows.")
    print("Distribution of best fixes:")
    print(df["best_fix"].value_counts(normalize=True).round(3))
