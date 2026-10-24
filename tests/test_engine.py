"""
Unit Test Suite for DeadlockGuard Engine.
Fulfills Section 9: 13+ formal correctness checks covering graph representation,
cycle detection, recovery cost calculation, explainability, safety net, and log parsing.
"""

import unittest
import networkx as nx
from rag import ResourceAllocationGraph
from recovery import RecoveryEngine, CostConfig
from simulator import DeadlockSimulator
from log_parser import DeadlockLogParser
from hybrid import evaluate_safety_net
import joblib


class TestDeadlockGuardEngine(unittest.TestCase):

    def setUp(self):
        self.config = CostConfig(
            kill_base_overhead=3.0,
            priority_weight=2.5,
            progress_weight=8.0,
            rollback_base_overhead=3.2,
            rollback_unit_cost=1.6,
            preempt_base_cost=4.2,
            preempt_holding_rate=0.8,
            starvation_factor=3.2,
        )
        self.engine = RecoveryEngine(self.config)

    # 1. RAG process node addition
    def test_01_rag_add_process(self):
        rag = ResourceAllocationGraph()
        rag.add_process("P0", priority=3, progress=0.45)
        self.assertIn("P0", rag.processes)
        self.assertEqual(rag.processes["P0"]["priority"], 3)
        self.assertEqual(rag.processes["P0"]["progress"], 0.45)

    # 2. RAG resource node addition
    def test_02_rag_add_resource(self):
        rag = ResourceAllocationGraph()
        rag.add_resource("R0", capacity=1)
        self.assertIn("R0", rag.resources)
        self.assertEqual(rag.resources["R0"]["capacity"], 1)

    # 3. RAG allocation and request edges
    def test_03_rag_allocation_and_request(self):
        rag = ResourceAllocationGraph()
        rag.allocate("R0", "P0")
        rag.request("P1", "R0")
        self.assertIn("P0", rag.allocations["R0"])
        self.assertIn("R0", rag.requests["P1"])

    # 4. RAG release mechanism
    def test_04_rag_release(self):
        rag = ResourceAllocationGraph()
        rag.allocate("R0", "P0")
        rag.release("R0", "P0")
        self.assertNotIn("P0", rag.allocations["R0"])

    # 5. Wait-For Graph reduction
    def test_05_wfg_reduction(self):
        rag = ResourceAllocationGraph()
        # P0 holds R0; P1 requests R0 -> P1 waits for P0
        rag.allocate("R0", "P0")
        rag.request("P1", "R0")
        wfg = rag.build_wait_for_graph()
        self.assertTrue(wfg.has_edge("P1", "P0"))
        self.assertFalse(wfg.has_edge("P0", "P1"))

    # 6. Cycle detection - No cycle in DAG
    def test_06_no_cycle_in_dag(self):
        rag = ResourceAllocationGraph()
        rag.allocate("R0", "P0")
        rag.request("P1", "R0")
        rag.allocate("R1", "P1")
        rag.request("P2", "R1")
        cycles = rag.find_deadlock_cycles()
        self.assertEqual(len(cycles), 0)
        self.assertIsNone(rag.get_deadlock_details())

    # 7. Cycle detection - 2-process deadlock
    def test_07_two_process_deadlock_cycle(self):
        rag = ResourceAllocationGraph()
        # P0 holds R0, requests R1; P1 holds R1, requests R0
        rag.allocate("R0", "P0")
        rag.request("P0", "R1")
        rag.allocate("R1", "P1")
        rag.request("P1", "R0")

        details = rag.get_deadlock_details()
        self.assertIsNotNone(details)
        self.assertEqual(len(details["cycle_processes"]), 2)
        self.assertIn("P0", details["cycle_processes"])
        self.assertIn("P1", details["cycle_processes"])

    # 8. Cycle detection - 3-process circular wait
    def test_08_three_process_circular_wait(self):
        rag = ResourceAllocationGraph()
        rag.allocate("R0", "P0")
        rag.request("P0", "R1")
        rag.allocate("R1", "P1")
        rag.request("P1", "R2")
        rag.allocate("R2", "P2")
        rag.request("P2", "R0")

        details = rag.get_deadlock_details()
        self.assertIsNotNone(details)
        self.assertEqual(len(details["cycle_processes"]), 3)

    # 9. Recovery cost calculation: TERMINATE
    def test_09_terminate_cost_calculation(self):
        p_attrs = {"name": "P0", "priority": 2, "progress": 0.50}
        cost, details = self.engine.evaluate_terminate(p_attrs)
        # base (3.0) + priority (2*2.5=5.0) + progress (0.50*8.0=4.0) = 12.0
        self.assertEqual(cost, 12.0)
        self.assertEqual(details["type"], "TERMINATE")

    # 10. Recovery cost calculation: ROLLBACK
    def test_10_rollback_cost_calculation(self):
        p_attrs = {"name": "P0", "priority": 2, "step": 8, "checkpoint_step": 5}
        cost, details = self.engine.evaluate_rollback(p_attrs)
        # steps_lost = 3. base (3.2) + 3*1.6 (4.8) + prio*0.4 (0.8) = 8.8
        self.assertEqual(cost, 8.8)
        self.assertEqual(details["type"], "ROLLBACK")

    # 11. Recovery cost calculation: PREEMPT
    def test_11_preempt_cost_calculation(self):
        p_attrs = {"name": "P0", "preempt_count": 0}
        cost, details = self.engine.evaluate_preempt(p_attrs, "R0", holding_time=3)
        # base (4.2) + holding (3*0.8=2.4) + starvation (0) = 6.6
        self.assertEqual(cost, 6.6)
        self.assertEqual(details["type"], "PREEMPT")

    # 12. Smart Advisor candidate ranking & plain-English explanation (Innovation A)
    def test_12_advisor_ranking_and_explanation(self):
        procs = {
            "P0": {"name": "P0", "priority": 4, "progress": 0.85, "step": 12, "checkpoint_step": 2, "preempt_count": 0},
            "P1": {"name": "P1", "priority": 1, "progress": 0.10, "step": 2, "checkpoint_step": 0, "preempt_count": 0},
        }
        deps = [
            {"waiter": "P0", "resource": "R1", "holder": "P1"},
            {"waiter": "P1", "resource": "R0", "holder": "P0"},
        ]
        deadlock_info = {"cycle_processes": ["P0", "P1"], "dependencies": deps}
        res = self.engine.evaluate_all_candidates(deadlock_info, procs)

        self.assertIn(res["cheapest_strategy"], ["TERMINATE", "ROLLBACK", "PREEMPT"])
        self.assertIn("explanation", res)
        self.assertTrue(len(res["explanation"]) > 20)

    # 13. Confidence Safety Net fallback mechanism (Innovation B)
    def test_13_safety_net_evaluation(self):
        payload = joblib.load("model.joblib")
        test_df = payload["test_df"].head(100)
        s_df = evaluate_safety_net(payload, test_df, cutoffs=[0.0, 0.80])
        self.assertEqual(len(s_df), 2)
        # Cutoff 0.80 must have >= double-checks than no safety net
        self.assertGreaterEqual(s_df.iloc[1]["tries_all_pct"], s_df.iloc[0]["tries_all_pct"])

    # 14. Real database deadlock log parsing (Innovation D)
    def test_14_log_parser_postgresql_and_mysql(self):
        parser = DeadlockLogParser()
        with open("sample_logs/postgres_deadlock.log") as f:
            pg_res = parser.parse(f.read())
        self.assertTrue(pg_res["success"])
        self.assertEqual(pg_res["dialect"], "PostgreSQL")
        self.assertEqual(len(pg_res["cycle_processes"]), 2)

        with open("sample_logs/mysql_innodb_deadlock.log") as f:
            my_res = parser.parse(f.read())
        self.assertTrue(my_res["success"])
        self.assertEqual(my_res["dialect"], "MySQL InnoDB")
        self.assertEqual(len(my_res["cycle_processes"]), 2)


if __name__ == "__main__":
    unittest.main()
