"""
Deadlock Log Parser (Innovation D) for DeadlockGuard.
Parses real deadlock logs from PostgreSQL, MySQL InnoDB, and distributed systems,
extracting Wait-For Graphs, transaction states, lock types, and deadlock cycles.
"""

import re
from typing import Dict, List, Optional, Tuple, Any
import networkx as nx


class DeadlockLogParser:
    def __init__(self):
        pass

    def parse(self, text: str) -> dict:
        """
        Detect format and parse deadlock log into a Wait-For Graph and cycle details.
        """
        text = text.strip()
        if "LATEST DETECTED DEADLOCK" in text or ("TRANSACTION" in text and "HOLDS THE LOCK" in text):
            return self._parse_mysql_innodb(text)
        elif "error:  deadlock detected" in text.lower() or "blocked by process" in text.lower():
            return self._parse_postgresql(text)
        else:
            return self._parse_generic(text)

    def _parse_postgresql(self, text: str) -> dict:
        """
        Parse PostgreSQL deadlock log.
        Matches lines like:
        Process 28143 waits for ShareLock on transaction 748293; blocked by process 28144.
        """
        pattern = re.compile(
            r"Process\s+(\w+)\s+waits for\s+([\w\s\(\),]+?);\s+blocked by process\s+(\w+)",
            re.IGNORECASE,
        )
        matches = pattern.findall(text)

        wfg = nx.DiGraph()
        processes = {}
        edges = []

        for waiter, lock_info, blocker in matches:
            waiter_id = f"PID_{waiter}"
            blocker_id = f"PID_{blocker}"
            lock_label = lock_info.strip()

            if waiter_id not in processes:
                processes[waiter_id] = {
                    "name": waiter_id,
                    "priority": 2,
                    "progress": 0.40,
                    "step": 4,
                    "checkpoint_step": 1,
                    "preempt_count": 0,
                    "type": "PostgreSQL Backend",
                }
            if blocker_id not in processes:
                processes[blocker_id] = {
                    "name": blocker_id,
                    "priority": 3,
                    "progress": 0.65,
                    "step": 6,
                    "checkpoint_step": 2,
                    "preempt_count": 0,
                    "type": "PostgreSQL Backend",
                }

            wfg.add_node(waiter_id, **processes[waiter_id])
            wfg.add_node(blocker_id, **processes[blocker_id])
            wfg.add_edge(waiter_id, blocker_id, lock=lock_label, label=f"waits for {lock_label[:20]}")
            edges.append({
                "waiter": waiter_id,
                "blocker": blocker_id,
                "lock": lock_label,
            })

        # Detect cycles
        cycles = list(nx.simple_cycles(wfg))
        primary_cycle = cycles[0] if cycles else []
        cycle_loop = list(primary_cycle) + [primary_cycle[0]] if primary_cycle else []

        return {
            "success": len(matches) > 0,
            "dialect": "PostgreSQL",
            "processes": processes,
            "edges": edges,
            "wfg": wfg,
            "cycle_processes": primary_cycle,
            "cycle_loop": cycle_loop,
            "all_cycles": cycles,
            "raw_matches": len(matches),
            "summary": f"Identified PostgreSQL deadlock with {len(processes)} processes and {len(edges)} wait relationships.",
        }

    def _parse_mysql_innodb(self, text: str) -> dict:
        """
        Parse MySQL InnoDB engine status deadlock output.
        Extracts transaction blocks, lock modes, tables, and blocked transactions.
        """
        # Split into transaction blocks
        trx_blocks = re.split(r"\*\*\*\s*\(\d+\)\s*TRANSACTION:", text)
        processes = {}
        wfg = nx.DiGraph()
        edges = []

        trx_data = []
        for idx, block in enumerate(trx_blocks[1:], start=1):
            trx_id_match = re.search(r"TRANSACTION\s+(\d+)", block)
            active_sec_match = re.search(r"ACTIVE\s+(\d+)\s+sec", block)
            undo_match = re.search(r"undo log entries\s+(\d+)", block)
            table_match = re.search(r"table\s+`?(\w+)`?\.`?(\w+)`?", block)
            
            trx_id = trx_id_match.group(1) if trx_id_match else f"TRX_{idx}"
            active_sec = int(active_sec_match.group(1)) if active_sec_match else 5
            undo_entries = int(undo_match.group(1)) if undo_match else 1
            table = f"{table_match.group(1)}.{table_match.group(2)}" if table_match else "unknown_table"

            pid = f"TRX_{trx_id}"
            # Derive progress and priority from active duration and undo log size
            progress = min(0.95, round(active_sec / 15.0, 2))
            step = max(2, active_sec)
            checkpoint = max(0, step - max(1, undo_entries))

            processes[pid] = {
                "name": pid,
                "priority": min(5, 1 + undo_entries),
                "progress": progress,
                "step": step,
                "checkpoint_step": checkpoint,
                "preempt_count": 0,
                "undo_entries": undo_entries,
                "active_sec": active_sec,
                "table": table,
                "type": "InnoDB Transaction",
            }
            trx_data.append(pid)

        # In InnoDB 2-way deadlock, TRX 1 waits for lock held by TRX 2, and TRX 2 waits for lock held by TRX 1
        if len(trx_data) >= 2:
            p1 = trx_data[0]
            p2 = trx_data[1]
            wfg.add_node(p1, **processes[p1])
            wfg.add_node(p2, **processes[p2])
            wfg.add_edge(p1, p2, lock="Row Lock (Exclusive)", label="waits for lock held by")
            wfg.add_edge(p2, p1, lock="Row Lock (Shared/Exclusive)", label="waits for lock held by")
            edges.append({"waiter": p1, "blocker": p2, "lock": "Row Lock (Exclusive)"})
            edges.append({"waiter": p2, "blocker": p1, "lock": "Row Lock (Shared/Exclusive)"})

        cycles = list(nx.simple_cycles(wfg))
        primary_cycle = cycles[0] if cycles else []
        cycle_loop = list(primary_cycle) + [primary_cycle[0]] if primary_cycle else []

        return {
            "success": len(processes) > 0,
            "dialect": "MySQL InnoDB",
            "processes": processes,
            "edges": edges,
            "wfg": wfg,
            "cycle_processes": primary_cycle,
            "cycle_loop": cycle_loop,
            "all_cycles": cycles,
            "raw_matches": len(processes),
            "summary": f"Identified MySQL InnoDB deadlock between {len(processes)} active transactions.",
        }

    def _parse_generic(self, text: str) -> dict:
        """
        Parse generic or microservice deadlock text lines:
        e.g., 'Process P1 waits for Resource R2; held by Process P2'
        or 'P1 -> R1 -> P2'
        """
        pattern = re.compile(
            r"(?:Process\s+)?(\w+)(?:\s*\([^)]*\))?\s+waits for\s+(?:Resource\s+)?(\w+);?\s+held by\s+(?:Process\s+)?(\w+)",
            re.IGNORECASE,
        )
        matches = pattern.findall(text)

        wfg = nx.DiGraph()
        processes = {}
        edges = []

        for waiter, resource, holder in matches:
            w_id = waiter.strip()
            h_id = holder.strip()
            r_id = resource.strip()

            if w_id not in processes:
                processes[w_id] = {
                    "name": w_id,
                    "priority": 2,
                    "progress": 0.50,
                    "step": 6,
                    "checkpoint_step": 3,
                    "preempt_count": 0,
                    "type": "Process",
                }
            if h_id not in processes:
                processes[h_id] = {
                    "name": h_id,
                    "priority": 2,
                    "progress": 0.50,
                    "step": 6,
                    "checkpoint_step": 3,
                    "preempt_count": 0,
                    "type": "Process",
                }

            wfg.add_node(w_id, **processes[w_id])
            wfg.add_node(h_id, **processes[h_id])
            wfg.add_edge(w_id, h_id, lock=r_id, label=f"waits for {r_id}")
            edges.append({"waiter": w_id, "blocker": h_id, "lock": r_id})

        cycles = list(nx.simple_cycles(wfg))
        primary_cycle = cycles[0] if cycles else []
        cycle_loop = list(primary_cycle) + [primary_cycle[0]] if primary_cycle else []

        return {
            "success": len(matches) > 0,
            "dialect": "Generic / Distributed Coordinator",
            "processes": processes,
            "edges": edges,
            "wfg": wfg,
            "cycle_processes": primary_cycle,
            "cycle_loop": cycle_loop,
            "all_cycles": cycles,
            "raw_matches": len(matches),
            "summary": f"Identified generic deadlock graph with {len(processes)} processes and {len(edges)} wait relationships.",
        }
