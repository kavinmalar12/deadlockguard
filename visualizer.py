"""
Visualization Engine for DeadlockGuard using Plotly.
Builds interactive, high-contrast graphs for Resource Allocation Graphs (RAG)
and Wait-For Graphs (WFG), with deadlocked cycle highlighting.
"""

from typing import Dict, List, Optional, Set, Tuple
import math
import networkx as nx
import plotly.graph_objects as go
from rag import ResourceAllocationGraph


def create_rag_plot(rag: ResourceAllocationGraph, deadlock_info: Optional[dict] = None) -> go.Figure:
    """
    Render a bipartite Resource Allocation Graph (RAG) using Plotly.
    - Process nodes: Circles (Blue / Cyan, or Red if in cycle)
    - Resource nodes: Squares (Amber / Orange, or Red if in cycle)
    - Allocation edges: Solid arrows (Resource -> Process)
    - Request edges: Dashed arrows (Process -> Resource)
    - Cycle edges: Thick glowing crimson lines
    """
    cycle_processes = set(deadlock_info.get("cycle_processes", [])) if deadlock_info else set()
    cycle_resources = set(deadlock_info.get("cycle_resources", [])) if deadlock_info else set()
    rag_cycle_edges = deadlock_info.get("rag_cycle_edges", set()) if deadlock_info else set()

    processes = list(rag.processes.keys())
    resources = list(rag.resources.keys())

    # Circular layout: processes on left circle/semi-circle, resources on right
    total_nodes = len(processes) + len(resources)
    pos: Dict[str, Tuple[float, float]] = {}

    # Place processes on a circular arc
    for i, pid in enumerate(processes):
        angle = (2 * math.pi * i) / max(1, len(processes)) + (math.pi / 4)
        pos[pid] = (math.cos(angle) * 1.8 - 0.5, math.sin(angle) * 1.8)

    # Place resources on a concentric or opposite arc
    for j, rid in enumerate(resources):
        angle = (2 * math.pi * j) / max(1, len(resources)) - (math.pi / 4)
        pos[rid] = (math.cos(angle) * 1.8 + 0.5, math.sin(angle) * 1.8)

    fig = go.Figure()

    # Draw edges
    # Allocation edges: Resource -> Process
    for rid, pids in rag.allocations.items():
        for pid in pids:
            if rid not in pos or pid not in pos:
                continue
            x0, y0 = pos[rid]
            x1, y1 = pos[pid]
            is_cycle = (rid, pid) in rag_cycle_edges

            color = "#FF1744" if is_cycle else "#00E676"
            width = 4.0 if is_cycle else 2.0
            dash = "solid"

            # Draw edge line
            fig.add_trace(go.Scatter(
                x=[x0, (x0 + x1) / 2, x1],
                y=[y0, (y0 + y1) / 2, y1],
                mode="lines",
                line=dict(color=color, width=width, dash=dash),
                hoverinfo="text",
                text=f"ALLOCATED: {rid} held by {pid}",
                showlegend=False,
            ))

    # Request edges: Process -> Resource
    for pid, rids in rag.requests.items():
        for rid in rids:
            if pid not in pos or rid not in pos:
                continue
            x0, y0 = pos[pid]
            x1, y1 = pos[rid]
            is_cycle = (pid, rid) in rag_cycle_edges

            color = "#FF1744" if is_cycle else "#FFA000"
            width = 4.0 if is_cycle else 2.0
            dash = "solid" if is_cycle else "dash"

            fig.add_trace(go.Scatter(
                x=[x0, (x0 + x1) / 2, x1],
                y=[y0, (y0 + y1) / 2, y1],
                mode="lines",
                line=dict(color=color, width=width, dash=dash),
                hoverinfo="text",
                text=f"REQUESTING: {pid} waits for {rid}",
                showlegend=False,
            ))

    # Draw Process Nodes (Circles)
    p_x = [pos[p][0] for p in processes if p in pos]
    p_y = [pos[p][1] for p in processes if p in pos]
    p_colors = ["#FF1744" if p in cycle_processes else "#2979FF" for p in processes if p in pos]
    p_labels = [p for p in processes if p in pos]
    p_hovers = [
        f"<b>Process {p}</b><br>Priority: {rag.processes[p].get('priority', 1)}<br>Progress: {int(rag.processes[p].get('progress', 0)*100)}%<br>Preempts: {rag.processes[p].get('preempt_count', 0)}"
        for p in processes if p in pos
    ]

    fig.add_trace(go.Scatter(
        x=p_x,
        y=p_y,
        mode="markers+text",
        marker=dict(symbol="circle", size=38, color=p_colors, line=dict(color="#FFFFFF", width=2)),
        text=p_labels,
        textfont=dict(color="#FFFFFF", size=13, family="monospace"),
        textposition="middle center",
        hoverinfo="text",
        hovertext=p_hovers,
        name="Processes",
    ))

    # Draw Resource Nodes (Squares)
    r_x = [pos[r][0] for r in resources if r in pos]
    r_y = [pos[r][1] for r in resources if r in pos]
    r_colors = ["#FF1744" if r in cycle_resources else "#FF9100" for r in resources if r in pos]
    r_labels = [r for r in resources if r in pos]
    r_hovers = [
        f"<b>Resource {r}</b><br>Held by: {list(rag.allocations.get(r, [])) or 'None'}"
        for r in resources if r in pos
    ]

    fig.add_trace(go.Scatter(
        x=r_x,
        y=r_y,
        mode="markers+text",
        marker=dict(symbol="square", size=34, color=r_colors, line=dict(color="#FFFFFF", width=2)),
        text=r_labels,
        textfont=dict(color="#FFFFFF", size=12, family="monospace"),
        textposition="middle center",
        hoverinfo="text",
        hovertext=r_hovers,
        name="Resources",
    ))

    title_text = "Resource Allocation Graph (RAG) — ⚠️ DEADLOCK CYCLE" if cycle_processes else "Resource Allocation Graph (RAG) — System Normal"
    fig.update_layout(
        title=dict(text=title_text, font=dict(size=15, color="#E0E0E0")),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#E0E0E0")),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="#121620",
        paper_bgcolor="#121620",
        height=420,
    )

    return fig


def create_wfg_plot(wfg: nx.DiGraph, cycle_nodes: List[str]) -> go.Figure:
    """
    Render a Wait-For Graph (WFG) showing process-to-process wait dependencies.
    """
    cycle_set = set(cycle_nodes)
    nodes = list(wfg.nodes())
    pos: Dict[str, Tuple[float, float]] = {}

    for i, node in enumerate(nodes):
        angle = (2 * math.pi * i) / max(1, len(nodes))
        pos[node] = (math.cos(angle) * 2.0, math.sin(angle) * 2.0)

    fig = go.Figure()

    # Draw wait edges
    cycle_edges = set()
    if len(cycle_nodes) > 1:
        for idx in range(len(cycle_nodes)):
            cycle_edges.add((cycle_nodes[idx], cycle_nodes[(idx + 1) % len(cycle_nodes)]))

    for u, v, data in wfg.edges(data=True):
        if u not in pos or v not in pos:
            continue
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        is_cycle = (u, v) in cycle_edges

        color = "#FF1744" if is_cycle else "#00E5FF"
        width = 4.0 if is_cycle else 2.0
        label = data.get("lock") or data.get("label") or "waits for"

        # Edge line
        fig.add_trace(go.Scatter(
            x=[x0, (x0 + x1) / 2, x1],
            y=[y0, (y0 + y1) / 2, y1],
            mode="lines",
            line=dict(color=color, width=width),
            hoverinfo="text",
            text=f"{u} → {v} ({label})",
            showlegend=False,
        ))

    # Draw nodes
    n_x = [pos[n][0] for n in nodes if n in pos]
    n_y = [pos[n][1] for n in nodes if n in pos]
    n_colors = ["#FF1744" if n in cycle_set else "#2979FF" for n in nodes if n in pos]
    n_labels = [n for n in nodes if n in pos]

    fig.add_trace(go.Scatter(
        x=n_x,
        y=n_y,
        mode="markers+text",
        marker=dict(symbol="circle", size=42, color=n_colors, line=dict(color="#FFFFFF", width=2)),
        text=n_labels,
        textfont=dict(color="#FFFFFF", size=13, family="monospace"),
        textposition="middle center",
        hoverinfo="text",
        hovertext=[f"<b>{n}</b>" for n in nodes if n in pos],
        name="Transactions / Processes",
    ))

    fig.update_layout(
        title=dict(text="Wait-For Graph (WFG) — Process Wait Dependencies", font=dict(size=15, color="#E0E0E0")),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(color="#E0E0E0")),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=20, r=20, t=50, b=20),
        plot_bgcolor="#121620",
        paper_bgcolor="#121620",
        height=400,
    )

    return fig
