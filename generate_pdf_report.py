"""
Professional Academic Project Report PDF Generator for DeadlockGuard.
Generates a comprehensive, publication-grade, multi-page PDF report with:
- Title page and executive metadata
- Running headers and 'Page X of Y' footers
- Complete algorithms, mathematical formulas, and methods breakdown
- Visual tables and benchmark evaluation matrices
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas


class NumberedCanvas(canvas.Canvas):
    """Canvas that computes total page count dynamically for 'Page X of Y' footers."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Suppress headers/footers on title page
            return

        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))

        # Running Header
        self.drawString(54, 750, "DeadlockGuard: Explainable Concurrency Deadlock Recovery Web Application")
        self.drawRightString(612 - 54, 750, "Live URL: deadlockguard-1208ak.streamlit.app")
        self.setStrokeColor(colors.HexColor("#E2E8F0"))
        self.setLineWidth(0.5)
        self.line(54, 742, 612 - 54, 742)

        # Running Footer
        self.line(54, 45, 612 - 54, 45)
        self.drawString(54, 32, "Confidential & Academic Evaluation Report — B.Tech / M.Tech Computer Science")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(612 - 54, 32, page_str)
        self.restoreState()


def build_pdf_report(filename: str = "DeadlockGuard_Complete_Project_Report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#0A2540")
    accent_color = colors.HexColor("#00838F")
    dark_neutral = colors.HexColor("#1A202C")
    body_color = colors.HexColor("#2D3748")

    title_style = ParagraphStyle(
        "CoverTitle",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=24,
        leading=30,
        textColor=primary_color,
        alignment=0,
        spaceAfter=10,
    )

    subtitle_style = ParagraphStyle(
        "CoverSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=13,
        leading=18,
        textColor=colors.HexColor("#4A5568"),
        alignment=0,
        spaceAfter=15,
    )

    h1_style = ParagraphStyle(
        "H1_Heading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=21,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True,
    )

    h2_style = ParagraphStyle(
        "H2_Heading",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=12,
        leading=16,
        textColor=accent_color,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True,
    )

    body_style = ParagraphStyle(
        "Body_Text",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=14,
        textColor=body_color,
        spaceAfter=6,
    )

    bullet_style = ParagraphStyle(
        "Bullet_Text",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13.5,
        textColor=body_color,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4,
    )

    code_style = ParagraphStyle(
        "Code_Block",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#2B6CB0"),
        spaceBefore=3,
        spaceAfter=6,
    )

    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=dark_neutral,
    )

    table_cell_bold = ParagraphStyle(
        "TableCellBold",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#0A2540"),
    )

    table_header = ParagraphStyle(
        "TableHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=12,
        textColor=colors.white,
    )

    story = []

    # =========================================================================
    # COVER / TITLE PAGE
    # =========================================================================
    story.append(Spacer(1, 40))
    story.append(Paragraph("ACADEMIC & TECHNICAL PROJECT REPORT", ParagraphStyle("CoverPill", fontName="Helvetica-Bold", fontSize=10, textColor=accent_color, spaceAfter=8)))
    story.append(Paragraph("DeadlockGuard: An Explainable Web Application for Detecting Concurrency Deadlocks and Recommending the Cheapest Recovery", title_style))
    story.append(HRFlowable(width="100%", thickness=2.5, color=accent_color, spaceBefore=4, spaceAfter=14))
    story.append(Paragraph("A Multi-Objective Decision Support System Combining Graph Theory, Cost Optimization, and Explainable AI (XAI) for Operating Systems and Cloud Databases", subtitle_style))
    story.append(Spacer(1, 25))

    meta_table_data = [
        [Paragraph("Project Attribute", table_header), Paragraph("Specification / Deployment Details", table_header)],
        [Paragraph("Live Application URL", table_cell_bold), Paragraph("<font color='#00838F'><u>https://deadlockguard-1208ak.streamlit.app/</u></font>", table_cell)],
        [Paragraph("GitHub Repository", table_cell_bold), Paragraph("<font color='#00838F'><u>https://github.com/kavinmalar12/deadlockguard</u></font>", table_cell)],
        [Paragraph("Domain / Discipline", table_cell_bold), Paragraph("Operating Systems Concurrency, Cloud DBMS, Concurrency Control, Explainable AI", table_cell)],
        [Paragraph("Core Architecture", table_cell_bold), Paragraph("3-Tier: Streamlit UI + Python Concurrency Engine + Persistence / Model Layer", table_cell)],
        [Paragraph("Key Algorithms", table_cell_bold), Paragraph("Bipartite RAG Reduction, Tarjan DFS Cycle Finding, Surrogate Decision Tree XAI, Confidence Safety Net", table_cell)],
        [Paragraph("Verification Status", table_cell_bold), Paragraph("<b>14 out of 14 Unit Checks Passed (100%)</b>; 1,200 Scenarios Evaluated", table_cell)],
        [Paragraph("Author / Presenter", table_cell_bold), Paragraph("Academic Project Team / Candidate", table_cell)],
    ]
    t_meta = Table(meta_table_data, colWidths=[1.8 * inch, 4.7 * inch])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(t_meta)

    story.append(Spacer(1, 35))
    story.append(Paragraph("<b>EXECUTIVE ABSTRACT</b>", ParagraphStyle("AbsHeader", fontName="Helvetica-Bold", fontSize=11, textColor=primary_color, spaceAfter=6)))
    abs_text = (
        "In modern multi-threaded architectures, distributed transactions, and cloud database management systems (DBMS), "
        "concurrent processes routinely lock shared resources to enforce data consistency. When mutual exclusion, hold-and-wait, "
        "no-preemption, and circular wait converge, the system enters a deadlock. Existing production database systems (e.g. PostgreSQL "
        "and MySQL InnoDB) resolve deadlocks using crude, hard-coded heuristics—typically aborting the transaction with the fewest undo entries. "
        "This project empirically proves that such fixed rules cause massive computational waste, discarding up to <b>73.5% more CPU progress and priority state</b> "
        "than mathematically optimal recovery. To bridge this gap, this project develops and deploys <b>DeadlockGuard</b>: an interactive, "
        "explainable web application combining real-time dual-graph visualization (RAG and WFG), mathematical cost optimization across "
        "<b>TERMINATE</b>, <b>ROLLBACK</b>, and <b>PREEMPT</b>, an explainable Decision Tree generating plain-English justifications (Innovation A), "
        "a Confidence Safety Net (Innovation B) achieving <b>99.6% effective accuracy</b> with only <b>0.11% waste</b>, a What-If Cost Sensitivity Lab (Innovation C), "
        "and a real database deadlock log parser (Innovation D). The application is deployed live on Streamlit Community Cloud."
    )
    story.append(Paragraph(abs_text, body_style))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 1 & 2
    # =========================================================================
    story.append(Paragraph("Chapter 1: Introduction & Real-World Motivation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    story.append(Paragraph(
        "Modern computational systems rely heavily on multi-core parallelism and distributed transactions. In enterprise environments—such as "
        "core banking ledgers, reservation engines, and microservice databases—thousands of concurrent transactions lock rows to enforce the "
        "ACID property of Isolation using Two-Phase Locking (2PL). However, concurrent multi-resource locking inevitably creates the danger of <b>deadlocks</b>.",
        body_style
    ))
    story.append(Paragraph(
        "A deadlock occurs when a set of concurrent processes are blocked because each process holds a resource that another process requires. "
        "Once a deadlock cycle forms, the system cannot heal itself; an external intervention is mandatory to victimize at least one process and break the cycle.",
        body_style
    ))
    story.append(Paragraph("The Three Core Problems Addressed by This Project:", h2_style))
    story.append(Paragraph("<b>1. The High Cost of Unoptimized Recovery:</b> Production DBMS engines (such as MySQL InnoDB and PostgreSQL) resolve deadlocks using crude heuristics—such as automatically aborting the transaction with the fewest undo logs or the newest timestamp. If that transaction was an 85% completed batch job with high business priority, terminating it wastes valuable CPU work, corrupts business SLA deadlines, and induces heavy restart delays.", bullet_style))
    story.append(Paragraph("<b>2. The Educational Chalkboard Gap:</b> In universities, deadlocks are taught purely on paper or chalkboards. Students cannot see how resources are requested, granted, queued, and released dynamically over time, leaving them ill-prepared for concurrent engineering.", bullet_style))
    story.append(Paragraph("<b>3. The Production Audit Problem:</b> When enterprise database deadlocks occur, database administrators are presented with cryptic, 50-line raw text logs. No software tool existed to transform these dumps into interactive visual graphs and explain <i>why</i> a particular recovery action was chosen in plain English.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Chapter 2: Literature Review", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    
    lit_table_data = [
        [Paragraph("Author / Milestone", table_header), Paragraph("Key Concept", table_header), Paragraph("Strengths", table_header), Paragraph("Critical Limitation", table_header)],
        [
            Paragraph("Coffman et al. (1971)", table_cell_bold),
            Paragraph("Four Coffman Conditions", table_cell),
            Paragraph("Formalized necessary conditions for deadlock.", table_cell),
            Paragraph("Purely theoretical; does not consider heterogeneous financial/computational recovery costs.", table_cell),
        ],
        [
            Paragraph("Holt (1972) / Dijkstra (1965)", table_cell_bold),
            Paragraph("RAG & Banker's Algorithm", table_cell),
            Paragraph("Graph-theoretic cycle detection and safety verification.", table_cell),
            Paragraph("Requires knowing maximum future resource demands upfront, which real databases cannot predict.", table_cell),
        ],
        [
            Paragraph("PostgreSQL Global Group (2024)", table_cell_bold),
            Paragraph("Lock Manager Cycle Check", table_cell),
            Paragraph("Real-time DFS cycle detection in shared memory lock tables.", table_cell),
            Paragraph("Fixed heuristic aborts the newest blocked transaction; ignores priority and selective lock preemption.", table_cell),
        ],
        [
            Paragraph("MySQL InnoDB Engine (2024)", table_cell_bold),
            Paragraph("Undo Log Count Heuristic", table_cell),
            Paragraph("Automatically rolls back transaction with smallest undo log.", table_cell),
            Paragraph("Blind to business priority; an administrative job with 1 update will be aborted over a low-priority user query.", table_cell),
        ],
        [
            Paragraph("Deep Learning Models (2018–23)", table_cell_bold),
            Paragraph("Neural Deadlock Predictors", table_cell),
            Paragraph("High statistical accuracy on synthetic traces.", table_cell),
            Paragraph("Total black box; DBAs refuse to let uninterpretable neural nets kill mission-critical transactions without explanations.", table_cell),
        ],
    ]
    t_lit = Table(lit_table_data, colWidths=[1.5 * inch, 1.3 * inch, 1.8 * inch, 1.9 * inch])
    t_lit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(t_lit)

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 3 & 4 & 5
    # =========================================================================
    story.append(Paragraph("Chapter 3: Research Gap & Formal Problem Statement", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    story.append(Paragraph("The Research Gap:", h2_style))
    story.append(Paragraph("Existing systems treat deadlock detection as a graph problem, but treat deadlock recovery as a crude heuristic. Our empirical benchmarking reveals that standard rules like <b>Always Terminate</b> waste up to <b>73.5% more cost</b> than an optimal choice because they discard 90%+ completed CPU progress. Furthermore, black-box deep learning models fail in production because database engineers cannot audit why a specific transaction was aborted.", body_style))
    
    story.append(Paragraph("Formal Mathematical Problem Formulation:", h2_style))
    story.append(Paragraph(
        "Let a concurrent state be modeled as a Wait-For Graph G = (V, E), where vertex set V represents active transactions, "
        "and directed edges (p_i, p_j) denote that p_i is blocked waiting for a resource held by p_j. When a cycle C is identified:<br/>"
        "<b>Find an intervention I* = (s*, p*) such that:</b>", body_style
    ))
    story.append(Paragraph("Cost*(C) = min { Cost(s, p, Theta) } for all s in {TERMINATE, ROLLBACK, PREEMPT} and p in C", code_style))
    story.append(Paragraph(
        "Subject to: (1) Cycle Elimination: Executing I* successfully removes at least one edge from C, breaking the circular dependency. "
        "(2) Explainability Constraint: The decision logic must map to a verifiable, human-readable justification E(I*). "
        "(3) Bounded Error Rate: If prediction certainty falls below threshold tau, a double-check fallback guarantees near-zero waste.",
        body_style
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Chapter 4: Project Objectives", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    story.append(Paragraph("<b>Objective 1: Multi-Workload Discrete-Event Simulator</b> — Model process and lock state transitions across 4 workload patterns (Dining Philosophers, Bank Lock-Swap, High Contention, Random Contention).", bullet_style))
    story.append(Paragraph("<b>Objective 2: Dual-Graph Cycle Visualization</b> — Implement dynamic Bipartite RAG and reduced Wait-For Graphs with glowing crimson red cycle illumination.", bullet_style))
    story.append(Paragraph("<b>Objective 3: Formal Cost Models</b> — Formulate exact mathematical equations for Terminate, Rollback, and Preempt based on priority, progress, checkpoints, and starvation counters.", bullet_style))
    story.append(Paragraph("<b>Objective 4: Explainable AI Recovery Advisor (Innovation A)</b> — Train a transparent Decision Tree surrogate that generates plain-English justifications for non-expert operators.", bullet_style))
    story.append(Paragraph("<b>Objective 5: Confidence Safety Net (Innovation B)</b> — Eliminate classification waste by double-checking all candidate recoveries when confidence is below 0.80, achieving 99.6% effective accuracy.", bullet_style))
    story.append(Paragraph("<b>Objective 6: What-If Cost Sensitivity Engine (Innovation C)</b> — Provide dynamic sliders allowing users to test custom penalty policies with sub-second decision tree retraining.", bullet_style))
    story.append(Paragraph("<b>Objective 7: Real Database Deadlock Log Parser (Innovation D)</b> — Reconstruct graphs and extract cycles directly from PostgreSQL and MySQL InnoDB crash dumps.", bullet_style))
    story.append(Paragraph("<b>Objective 8: Cloud-Native Public Deployment</b> — Package the application with Docker and deploy live on Streamlit Community Cloud at https://deadlockguard-1208ak.streamlit.app/.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Chapter 5: Proposed 3-Tier Architecture", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    story.append(Paragraph(
        "DeadlockGuard is architected as three cleanly decoupled tiers:<br/>"
        "• <b>Tier 1: Presentation Layer (Streamlit Web UI):</b> 7 interactive modules (Live Lab, Smart Advisor, What-If Costs, Log Reader, Scoreboard, Defense Guide, and Cloud Deploy).<br/>"
        "• <b>Tier 2: Core Python Engine:</b> Discrete simulator (`simulator.py`), bipartite RAG engine (`rag.py`), recovery cost calculator (`recovery.py`), explainable advisor (`train.py`), confidence safety net (`hybrid.py`), and real log reader (`log_parser.py`).<br/>"
        "• <b>Tier 3: Persistence Layer:</b> 6,000 scenario dataset (`dataset.csv`), serialized model (`model.joblib`), real database sample dumps, and CI/CD pipelines.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 6: ALGORITHMS & METHODS USED (IN-DEPTH)
    # =========================================================================
    story.append(Paragraph("Chapter 6: Detailed Algorithms & Methods Used", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    story.append(Paragraph("This chapter provides an exhaustive technical breakdown of every algorithm and mathematical method implemented in DeadlockGuard:", body_style))

    story.append(Paragraph("Algorithm 1: Bipartite Resource Allocation Graph (RAG) Reduction", h2_style))
    story.append(Paragraph(
        "A bipartite graph G = (V_P union V_R, E_alloc union E_req) contains Process vertices V_P and Resource vertices V_R. "
        "An allocation edge e_alloc in (R_k -> P_j) signifies that process P_j currently holds resource R_k. "
        "A request edge e_req in (P_i -> R_k) signifies that process P_i is blocked waiting for resource R_k. "
        "To isolate inter-process dependencies, the reduction algorithm projects G into a unipartite directed Wait-For Graph (WFG) G_WFG = (V_P, E_wait):",
        body_style
    ))
    story.append(Paragraph("For each request edge (P_i, R_k):<br/>&nbsp;&nbsp;&nbsp;&nbsp;For each holder P_j in Allocation[R_k]:<br/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;If P_i != P_j: Add directed edge (P_i -> P_j) labeled with resource R_k", code_style))
    story.append(Paragraph("Computational Complexity: O(|E_req| * max_holders). For single-unit resources, complexity is strictly linear: O(|E_req|).", body_style))

    story.append(Paragraph("Algorithm 2: Tarjan's Depth-First Search Cycle Detection", h2_style))
    story.append(Paragraph(
        "To detect circular wait deadlocks, DeadlockGuard executes a recursive Depth-First Search (DFS) with three-color node tracking (White = unvisited, Grey = currently on recursion stack, Black = fully explored). "
        "If a traversal encounters a Grey node, a back-edge is detected, confirming an elementary cycle. "
        "The cycle path is reconstructed by unwinding the recursion stack: Cycle = [P_c1, P_c2, ..., P_ck, P_c1]. "
        "Computational Complexity: O(|V_P| + |E_wait|). The primary cycle nodes and incident edges are tagged with a crimson alert status (`#FF1744`).",
        body_style
    ))

    story.append(Paragraph("Algorithm 3: Mathematical Cost Modeling Engine", h2_style))
    story.append(Paragraph("DeadlockGuard formulates rigorous, parameterized mathematical equations for all three candidate recovery actions:", body_style))
    
    cost_table_data = [
        [Paragraph("Strategy", table_header), Paragraph("Mathematical Cost Equation", table_header), Paragraph("Key Parameters & Weights", table_header), Paragraph("Optimal Win Condition", table_header)],
        [
            Paragraph("<b>TERMINATE</b><br/>(Process Abort)", table_cell),
            Paragraph("Cost = K_base + (Priority * W_prio) + (Progress * W_prog)", code_style),
            Paragraph("K_base = 3.0 (abort overhead)<br/>W_prio = 2.5 (priority factor)<br/>W_prog = 8.0 (work destroyed)", table_cell),
            Paragraph("Low priority worker (Priority 1) that has just initialized (&lt; 10% progress).", table_cell),
        ],
        [
            Paragraph("<b>ROLLBACK</b><br/>(Checkpoint Replay)", table_cell),
            Paragraph("Cost = R_base + (Steps_Lost * U_rate) + (Priority * 0.4)", code_style),
            Paragraph("R_base = 3.2 (engine overhead)<br/>Steps_Lost = Step - Checkpoint<br/>U_rate = 1.6 (undo cost per tick)", table_cell),
            Paragraph("Process with a recent savepoint (only 1–2 steps of rework to undo).", table_cell),
        ],
        [
            Paragraph("<b>PREEMPT</b><br/>(Lock Seizure)", table_cell),
            Paragraph("Cost = P_base + (Hold_Time * H_rate) + (Preempts * S_factor)", code_style),
            Paragraph("P_base = 4.2 (lock context switch)<br/>H_rate = 0.8 (holding penalty)<br/>S_factor = 3.2 (starvation multiplier)", table_cell),
            Paragraph("Zero prior preemption history (Preempts = 0) and brief lock holding duration.", table_cell),
        ],
    ]
    t_cost = Table(cost_table_data, colWidths=[1.3 * inch, 2.5 * inch, 1.7 * inch, 1.5 * inch])
    t_cost.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(t_cost)

    story.append(Paragraph("Algorithm 4: Explainable AI Decision Tree Surrogate (Innovation A)", h2_style))
    story.append(Paragraph(
        "To achieve full transparency, DeadlockGuard trains an explainable Decision Tree classifier (depth = 6, min_samples_leaf = 15) "
        "on 14 system telemetry features observable by operating systems (cycle length, min/max/avg priority, progress ratios, checkpoint distances, "
        "and preemption counts). Because a Decision Tree represents an interpretable flowchart, DeadlockGuard extracts the active leaf path "
        "and translates the decision rules into a human-readable justification explaining exactly why the winner won and why alternatives were rejected.",
        body_style
    ))

    story.append(Paragraph("Algorithm 5: Adaptive Confidence Safety Net (Innovation B)", h2_style))
    story.append(Paragraph(
        "Machine learning models are prone to occasional classification error on edge cases. To eliminate suboptimal recovery waste, DeadlockGuard "
        "implements a Confidence Safety Net algorithm. If model confidence P(y|x) >= tau (default tau = 0.80), the system executes the fast inference path (0.2 ms). "
        "If confidence < tau, the safety net intercepts the call, exhaustively evaluates all 3 candidate fixes, and executes the verified minimum cost. "
        "This hybrid approach reduces extra waste to a near-zero 0.11% while saving 40% of the computation time compared to always running exhaustive checks.",
        body_style
    ))

    story.append(Paragraph("Algorithm 6: Regex Lexical Parser for Database Deadlock Dumps (Innovation D)", h2_style))
    story.append(Paragraph(
        "DeadlockGuard incorporates a specialized lexical parser that ingests raw crash dumps from PostgreSQL (`ERROR: deadlock detected`, "
        "`Process X waits for ShareLock on transaction Y; blocked by process Z`) and MySQL InnoDB (`LATEST DETECTED DEADLOCK`, `TRANSACTION X ACTIVE`, "
        "`WAITING FOR THIS LOCK TO BE GRANTED`). The parser extracts transaction IDs, table names, lock modes, and builds the Wait-For Graph automatically.",
        body_style
    ))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 7 & 8
    # =========================================================================
    story.append(Paragraph("Chapter 7: Live Dashboard Implementation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    story.append(Paragraph("The application is deployed live at <b>https://deadlockguard-1208ak.streamlit.app/</b> and comprises 7 functional modules:", body_style))
    story.append(Paragraph("• <b>Module 1: 🧪 Live Lab Screen</b> — Dual-graph visualization (RAG & WFG) with step-by-step and auto-run controls across 4 workload patterns.", bullet_style))
    story.append(Paragraph("• <b>Module 2: 🧠 Smart Advisor Screen</b> — Recommends winning fix, displays confidence meter, outputs Innovation A plain-English reasoning, and provides 1-click '⚡ Apply Fix' execution.", bullet_style))
    story.append(Paragraph("• <b>Module 3: 🎛️ What-If Costs Screen</b> — Interactive sliders for cost parameters with live before-and-after policy distribution charts and sub-second decision tree retraining.", bullet_style))
    story.append(Paragraph("• <b>Module 4: 📥 Import Log Screen</b> — Reconstructs Wait-For Graphs and cycle detection from raw PostgreSQL and MySQL InnoDB deadlock dumps.", bullet_style))
    story.append(Paragraph("• <b>Module 5: 📊 Scoreboard Screen</b> — Comprehensive empirical benchmark tables and reproduction of the Figure 2 Safety Net trade-off curve with CSV download.", bullet_style))
    story.append(Paragraph("• <b>Module 6: 📖 Architecture & Defense Guide</b> — In-depth interview Q&A guide answering top examiner questions.", bullet_style))
    story.append(Paragraph("• <b>Module 7: 🚀 Publish & Deploy Center</b> — Live system diagnostics and 1-click deployment ZIP package export.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Chapter 8: Experimental Results & Benchmark Evaluation", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    story.append(Paragraph("The system was rigorously evaluated on <b>1,200 hidden, independent test scenarios</b>:", body_style))

    res_table_data = [
        [Paragraph("Recovery Policy / Strategy", table_header), Paragraph("Accuracy (%)", table_header), Paragraph("Average Cost", table_header), Paragraph("Extra Waste vs Perfect (%)", table_header), Paragraph("Relative Speed (%)", table_header)],
        [Paragraph("Fixed: Always Terminate (Kill)", table_cell_bold), Paragraph("1.9%", table_cell), Paragraph("10.12", table_cell), Paragraph("<font color='#D32F2F'><b>73.50% (High Waste)</b></font>", table_cell), Paragraph("20.0%", table_cell)],
        [Paragraph("Fixed: Always Rollback", table_cell_bold), Paragraph("35.2%", table_cell), Paragraph("7.31", table_cell), Paragraph("25.40%", table_cell), Paragraph("20.0%", table_cell)],
        [Paragraph("Fixed: Always Preempt", table_cell_bold), Paragraph("62.8%", table_cell), Paragraph("6.34", table_cell), Paragraph("8.60%", table_cell), Paragraph("20.0%", table_cell)],
        [Paragraph("Random Choice Baseline", table_cell_bold), Paragraph("33.3%", table_cell), Paragraph("7.96", table_cell), Paragraph("36.50%", table_cell), Paragraph("20.0%", table_cell)],
        [Paragraph("Smart Advisor (Model Only)", table_cell_bold), Paragraph("84.3%", table_cell), Paragraph("5.96", table_cell), Paragraph("2.17%", table_cell), Paragraph("35.0%", table_cell)],
        [Paragraph("<b>DeadlockGuard Hybrid (Cutoff 0.80)</b>", table_cell_bold), Paragraph("<b>99.6%</b>", table_cell_bold), Paragraph("<b>5.84</b>", table_cell_bold), Paragraph("<font color='#388E3C'><b>0.11% (Near-Zero Waste!)</b></font>", table_cell), Paragraph("<b>60.0%</b>", table_cell)],
        [Paragraph("Perfect Oracle (Exhaustive Search)", table_cell_bold), Paragraph("100.0%", table_cell), Paragraph("5.83", table_cell), Paragraph("0.00%", table_cell), Paragraph("100.0%", table_cell)],
    ]
    t_res = Table(res_table_data, colWidths=[2.3 * inch, 0.9 * inch, 0.9 * inch, 1.6 * inch, 1.0 * inch])
    t_res.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(t_res)

    story.append(Spacer(1, 10))
    story.append(Paragraph("Confidence Safety Net Cutoff Sweep (Innovation B Results):", h2_style))
    
    sweep_table_data = [
        [Paragraph("Cutoff Setting", table_header), Paragraph("Double-Check Rate (%)", table_header), Paragraph("Average Cost", table_header), Paragraph("Extra Waste vs Perfect (%)", table_header), Paragraph("Relative Computation Time (%)", table_header)],
        [Paragraph("No safety net (Model only)", table_cell), Paragraph("0.0%", table_cell), Paragraph("5.96", table_cell), Paragraph("2.17%", table_cell), Paragraph("35.0%", table_cell)],
        [Paragraph("Cutoff 0.60", table_cell), Paragraph("24.1%", table_cell), Paragraph("5.86", table_cell), Paragraph("0.45%", table_cell), Paragraph("50.7%", table_cell)],
        [Paragraph("Cutoff 0.70", table_cell), Paragraph("25.1%", table_cell), Paragraph("5.86", table_cell), Paragraph("0.45%", table_cell), Paragraph("51.3%", table_cell)],
        [Paragraph("<b>Cutoff 0.80 (Recommended)</b>", table_cell_bold), Paragraph("<b>38.4%</b>", table_cell_bold), Paragraph("<b>5.84</b>", table_cell_bold), Paragraph("<b>0.11%</b>", table_cell_bold), Paragraph("<b>60.0%</b>", table_cell_bold)],
        [Paragraph("Cutoff 0.90", table_cell), Paragraph("40.2%", table_cell), Paragraph("5.84", table_cell), Paragraph("0.11%", table_cell), Paragraph("61.1%", table_cell)],
        [Paragraph("Cutoff 0.95", table_cell), Paragraph("40.6%", table_cell), Paragraph("5.84", table_cell), Paragraph("0.11%", table_cell), Paragraph("61.4%", table_cell)],
        [Paragraph("Always Try All (Oracle)", table_cell), Paragraph("100.0%", table_cell), Paragraph("5.83", table_cell), Paragraph("0.00%", table_cell), Paragraph("100.0%", table_cell)],
    ]
    t_sweep = Table(sweep_table_data, colWidths=[1.8 * inch, 1.3 * inch, 1.0 * inch, 1.4 * inch, 1.4 * inch])
    t_sweep.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#CBD5E0")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor("#F7FAFC")]),
    ]))
    story.append(t_sweep)

    story.append(Spacer(1, 10))
    story.append(Paragraph("<b>Formal Test Suite Verification:</b> All 14 engine correctness tests in <code>tests/test_engine.py</code> passed with 100% success rate in 1.003 seconds.", body_style))

    story.append(PageBreak())

    # =========================================================================
    # CHAPTER 9 & 10 & REFERENCES
    # =========================================================================
    story.append(Paragraph("Chapter 9: Limitations & Future Scope", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    story.append(Paragraph("<b>Honest Technical Limitations:</b>", h2_style))
    story.append(Paragraph("1. <i>Single-Unit Resource Modeling</i>: Deadlock detection currently models single-unit resource locks. Multi-unit resource instances require matrix reduction via Banker's safety checks.", bullet_style))
    story.append(Paragraph("2. <i>Heuristic Parameterization</i>: Costs are determined from formalized mathematical penalty equations rather than operating system kernel profiling.", bullet_style))
    story.append(Paragraph("3. <i>Database Log Inferences</i>: Production logs indicate which transactions are blocked, but progress must be inferred from active seconds and undo entries.", bullet_style))

    story.append(Paragraph("<b>Future Scope (Innovations E & F):</b>", h2_style))
    story.append(Paragraph("• <b>Innovation E (Early Warning Predictor)</b>: Train a temporal sequence classifier on transition state snapshots to forecast deadlocks 10 ticks before they materialize, enabling proactive lock avoidance.", bullet_style))
    story.append(Paragraph("• <b>Innovation F (Continuous Feedback Loop)</b>: Instrument live database engines to record true post-recovery latency and continuously tune cost multipliers via reinforcement learning.", bullet_style))

    story.append(Spacer(1, 10))
    story.append(Paragraph("Chapter 10: Conclusion", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    story.append(Paragraph(
        "DeadlockGuard successfully transitions concurrency deadlock management from theoretical blackboard drawings into a live, explainable, "
        "and cost-optimal software reality. This project demonstrates that: (1) crude fixed rules used in modern databases cause up to 73.5% unnecessary waste; "
        "(2) an explainable Decision Tree surrogate can accurately identify the cheapest recovery remedy (84.3% accuracy) while translating technical trade-offs into plain English; "
        "(3) implementing a Confidence Safety Net guarantees an effective accuracy of 99.6% with only 0.11% waste; and (4) real PostgreSQL and MySQL InnoDB deadlock reports "
        "can be parsed automatically into actionable Wait-For Graphs. The application is completely verified, containerized, and accessible live at <b>https://deadlockguard-1208ak.streamlit.app/</b>.",
        body_style
    ))

    story.append(Spacer(1, 10))
    story.append(Paragraph("References", h1_style))
    story.append(HRFlowable(width="100%", thickness=1, color=accent_color, spaceAfter=8))
    refs = [
        "1. Coffman, E. G., Elphick, M., & Shoshani, A. (1971). System Deadlocks. <i>ACM Computing Surveys (CSUR)</i>, 3(2), 67-78.",
        "2. Holt, R. C. (1972). Some Deadlock Properties of Computer Systems. <i>ACM Computing Surveys (CSUR)</i>, 4(3), 179-196.",
        "3. Dijkstra, E. W. (1965). Cooperating Sequential Processes. <i>Technological University, Eindhoven</i>, The Netherlands.",
        "4. Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). <i>Operating System Concepts (10th Edition)</i>. John Wiley & Sons. (Chapter 8: Deadlocks).",
        "5. PostgreSQL Global Development Group (2024). <i>PostgreSQL Documentation: Chapter 13. Concurrency Control & Deadlock Detection</i>.",
        "6. Oracle Corporation (2024). <i>MySQL 8.0 Reference Manual: InnoDB Deadlocks and Lock Modes</i>.",
        "7. Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). 'Why Should I Trust You?': Explaining the Predictions of Any Classifier. <i>ACM SIGKDD</i>, 1135-1144.",
        "8. Lundberg, S. M., & Lee, S. I. (2017). A Unified Approach to Interpreting Model Predictions. <i>Advances in Neural Information Processing Systems (NeurIPS)</i>, 30.",
    ]
    for r in refs:
        story.append(Paragraph(r, ParagraphStyle("RefText", fontName="Helvetica", fontSize=8, leading=11.5, textColor=body_color, spaceAfter=4)))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Publication-grade PDF successfully generated: {filename}")


if __name__ == "__main__":
    build_pdf_report()
