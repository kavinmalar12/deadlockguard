"""
Resource Allocation Graph (RAG) and Wait-For Graph (WFG) Engine for DeadlockGuard.
Provides graph representation, cycle detection, and WFG reduction.
"""

from typing import Dict, List, Set, Tuple, Optional
import networkx as nx


class ResourceAllocationGraph:
    """
    Bipartite Directed Graph containing Process nodes and Resource nodes.
    - Allocation Edge: Resource -> Process (Process holds Resource)
    - Request Edge: Process -> Resource (Process is waiting for Resource)
    """

    def __init__(self):
        # processes: dict of process_id -> dict of attributes
        self.processes: Dict[str, dict] = {}
        # resources: dict of resource_id -> dict of attributes
        self.resources: Dict[str, dict] = {}
        # allocations: resource_id -> set of process_ids holding it
        self.allocations: Dict[str, Set[str]] = {}
        # requests: process_id -> set of resource_ids requested
        self.requests: Dict[str, Set[str]] = {}

    def add_process(self, pid: str, priority: int = 1, progress: float = 0.0, **kwargs):
        """Add or update a process node."""
        self.processes[pid] = {
            "priority": priority,
            "progress": progress,
            "preempt_count": kwargs.get("preempt_count", 0),
            "step": kwargs.get("step", 0),
            "checkpoint_step": kwargs.get("checkpoint_step", 0),
            "name": kwargs.get("name", pid),
            **kwargs,
        }
        if pid not in self.requests:
            self.requests[pid] = set()

    def add_resource(self, rid: str, capacity: int = 1, **kwargs):
        """Add or update a resource node."""
        self.resources[rid] = {
            "capacity": capacity,
            "name": kwargs.get("name", rid),
            **kwargs,
        }
        if rid not in self.allocations:
            self.allocations[rid] = set()

    def allocate(self, rid: str, pid: str):
        """Record that process pid holds resource rid (removes pending request if present)."""
        if rid not in self.resources:
            self.add_resource(rid)
        if pid not in self.processes:
            self.add_process(pid)

        self.allocations[rid].add(pid)
        if pid in self.requests and rid in self.requests[pid]:
            self.requests[pid].remove(rid)

    def request(self, pid: str, rid: str):
        """Record that process pid is waiting for resource rid."""
        if rid not in self.resources:
            self.add_resource(rid)
        if pid not in self.processes:
            self.add_process(pid)

        self.requests[pid].add(rid)

    def release(self, rid: str, pid: str):
        """Process pid releases resource rid."""
        if rid in self.allocations and pid in self.allocations[rid]:
            self.allocations[rid].remove(pid)

    def remove_process(self, pid: str):
        """Remove a process and all its held resources and requests."""
        if pid in self.processes:
            del self.processes[pid]
        if pid in self.requests:
            del self.requests[pid]
        for rid in self.allocations:
            self.allocations[rid].discard(pid)

    def to_networkx(self) -> nx.DiGraph:
        """Construct a NetworkX directed graph representing the bipartite RAG."""
        G = nx.DiGraph()
        for pid, attrs in self.processes.items():
            G.add_node(pid, node_type="process", label=pid, **attrs)
        for rid, attrs in self.resources.items():
            G.add_node(rid, node_type="resource", label=rid, **attrs)

        # Allocation edges: Resource -> Process
        for rid, pids in self.allocations.items():
            for pid in pids:
                G.add_edge(rid, pid, edge_type="allocation", label="holds")

        # Request edges: Process -> Resource
        for pid, rids in self.requests.items():
            for rid in rids:
                G.add_edge(pid, rid, edge_type="request", label="requests")

        return G

    def build_wait_for_graph(self) -> nx.DiGraph:
        """
        Reduce the RAG to a Wait-For Graph (WFG) containing only processes.
        If Process A requests Resource R, and Resource R is held by Process B,
        then Process A waits for Process B (Edge: A -> B, labeled with R).
        """
        wfg = nx.DiGraph()
        for pid, attrs in self.processes.items():
            wfg.add_node(pid, **attrs)

        for p_from, rids in self.requests.items():
            for rid in rids:
                holders = self.allocations.get(rid, set())
                for p_to in holders:
                    if p_from != p_to:
                        wfg.add_edge(p_from, p_to, resource=rid, label=f"waits for {rid}")

        return wfg

    def find_deadlock_cycles(self) -> List[List[str]]:
        """
        Detect deadlock cycles in the Wait-For Graph.
        Returns a list of cycles, each cycle is a list of process IDs forming the cycle.
        """
        wfg = self.build_wait_for_graph()
        try:
            cycles = list(nx.simple_cycles(wfg))
            return cycles
        except Exception:
            return []

    def get_deadlock_details(self) -> Optional[dict]:
        """
        Analyze the graph for deadlock. If a cycle exists, return full breakdown
        including the cycle nodes, cycle edges in RAG, and involved resources.
        """
        cycles = self.find_deadlock_cycles()
        if not cycles:
            return None

        primary_cycle = cycles[0]  # First cycle
        # Complete cycle loop for display
        cycle_loop = list(primary_cycle) + [primary_cycle[0]]

        # Determine involved resources and dependencies
        dependencies = []
        cycle_resources = set()
        for i in range(len(primary_cycle)):
            p_from = primary_cycle[i]
            p_to = primary_cycle[(i + 1) % len(primary_cycle)]

            # Find which resource p_from requests that p_to holds
            for rid in self.requests.get(p_from, set()):
                if p_to in self.allocations.get(rid, set()):
                    dependencies.append({
                        "waiter": p_from,
                        "resource": rid,
                        "holder": p_to,
                    })
                    cycle_resources.add(rid)

        # Identify cycle edges in RAG
        rag_cycle_edges = set()
        for dep in dependencies:
            # p_from requests rid (p_from -> rid)
            rag_cycle_edges.add((dep["waiter"], dep["resource"]))
            # rid is held by p_to (rid -> p_to)
            rag_cycle_edges.add((dep["resource"], dep["holder"]))

        return {
            "cycle_processes": primary_cycle,
            "cycle_loop": cycle_loop,
            "cycle_resources": list(cycle_resources),
            "dependencies": dependencies,
            "rag_cycle_edges": rag_cycle_edges,
            "all_cycles_count": len(cycles),
        }
