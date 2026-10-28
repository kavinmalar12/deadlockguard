"""
PowerPoint Generator for DeadlockGuard Presentation.
Builds a professional, clean, dark-themed 16:9 presentation slide deck
with minimum text, simple English phrases, and high readability.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE


def create_deck(output_file: str = "DeadlockGuard_Presentation.pptx"):
    prs = Presentation()
    # Set 16:9 widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # Theme colors
    COLOR_BG = RGBColor(14, 19, 31)        # #0E131F Dark Navy
    COLOR_CARD = RGBColor(24, 32, 50)      # #182032 Slate Navy
    COLOR_CYAN = RGBColor(0, 229, 255)     # #00E5FF Cyan Accent
    COLOR_WHITE = RGBColor(240, 244, 248)  # #F0F4F8 Off-white
    COLOR_MUTED = RGBColor(160, 174, 192)  # #A0AEC0 Muted Grey
    COLOR_GREEN = RGBColor(0, 230, 118)    # #00E676 Mint Green
    COLOR_RED = RGBColor(255, 23, 68)      # #FF1744 Crimson Red

    blank_slide_layout = prs.slide_layouts[6]

    def add_slide_bg(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = COLOR_BG
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="DEADLOCKGUARD"):
        # Category tag
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.5), Inches(0.4))
        tf_cat = cat_box.text_frame
        tf_cat.word_wrap = True
        p_cat = tf_cat.paragraphs[0]
        p_cat.text = category_text.upper()
        p_cat.font.size = Pt(11)
        p_cat.font.bold = True
        p_cat.font.color.rgb = COLOR_CYAN

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.5), Inches(0.8))
        tf_title = title_box.text_frame
        tf_title.word_wrap = True
        p_title = tf_title.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(26)
        p_title.font.bold = True
        p_title.font.color.rgb = COLOR_WHITE

    def add_card(slide, left, top, width, height, title, points, accent_color=COLOR_CYAN):
        # Card background
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = COLOR_CARD
        card.line.color.rgb = accent_color
        card.line.width = Pt(1.5)

        tb = slide.shapes.add_textbox(left + Inches(0.25), top + Inches(0.2), width - Inches(0.5), height - Inches(0.4))
        tf = tb.text_frame
        tf.word_wrap = True

        if title:
            p_t = tf.paragraphs[0]
            p_t.text = title
            p_t.font.size = Pt(16)
            p_t.font.bold = True
            p_t.font.color.rgb = accent_color
            p_t.space_after = Pt(10)

        first = True if not title else False
        for pt in points:
            p = tf.add_paragraph() if not first else tf.paragraphs[0]
            first = False
            p.text = f"• {pt}"
            p.font.size = Pt(13)
            p.font.color.rgb = COLOR_WHITE
            p.space_after = Pt(6)

    # -------------------------------------------------------------
    # SLIDE 1: TITLE SLIDE
    # -------------------------------------------------------------
    slide1 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide1)

    t_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.8), Inches(11.3), Inches(3.5))
    tf1 = t_box.text_frame
    tf1.word_wrap = True

    p_badge = tf1.paragraphs[0]
    p_badge.text = "🛡️ REAL-TIME APPLICATION PROJECT | VIVA PRESENTATION"
    p_badge.font.size = Pt(13)
    p_badge.font.bold = True
    p_badge.font.color.rgb = COLOR_CYAN
    p_badge.space_after = Pt(14)

    p_main = tf1.add_paragraph()
    p_main.text = "DeadlockGuard"
    p_main.font.size = Pt(44)
    p_main.font.bold = True
    p_main.font.color.rgb = COLOR_WHITE
    p_main.space_after = Pt(10)

    p_sub = tf1.add_paragraph()
    p_sub.text = "An Explainable Web Application for Detecting Deadlocks and Recommending the Cheapest Recovery"
    p_sub.font.size = Pt(18)
    p_sub.font.color.rgb = COLOR_MUTED
    p_sub.space_after = Pt(24)

    p_url = tf1.add_paragraph()
    p_url.text = "🌐 Live Public URL: https://deadlockguard-1208ak.streamlit.app/"
    p_url.font.size = Pt(15)
    p_url.font.bold = True
    p_url.font.color.rgb = COLOR_GREEN

    # -------------------------------------------------------------
    # SLIDE 2: INTRODUCTION & MOTIVATION
    # -------------------------------------------------------------
    slide2 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide2)
    add_header(slide2, "Introduction & Real-World Motivation", "1. CONTEXT & PROBLEM")

    add_card(slide2, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.0), "The Real-World Deadlock Crisis", [
        "Concurrent systems (Banking, E-Commerce, Cloud Databases) lock rows to guarantee consistency.",
        "When Process A waits for Process B, and Process B waits for Process A, the entire system hangs.",
        "Transactions freeze indefinitely; customers face payment timeouts, and servers crash.",
        "Deadlocks cannot be ignored — an intervention is mandatory.",
    ], COLOR_RED)

    add_card(slide2, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.0), "Why Existing Systems Fail", [
        "Textbook Theory: Deadlocks are drawn on chalkboards; students never see live lock contention.",
        "Crude Recovery Rules: Standard databases automatically kill transactions, wasting completed work.",
        "Zero Explainability: Administrators receive 50-line cryptic logs without a plain-English explanation.",
        "DeadlockGuard Solution: An explainable interactive lab and recovery advisor built for real humans.",
    ], COLOR_CYAN)

    # -------------------------------------------------------------
    # SLIDE 3: LITERATURE REVIEW
    # -------------------------------------------------------------
    slide3 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide3)
    add_header(slide3, "Literature Review (Evolution of Concurrency)", "2. PRIOR WORK")

    add_card(slide3, Inches(0.8), Inches(1.7), Inches(3.7), Inches(5.0), "Coffman & Holt (1971-72)", [
        "Formalized the 4 Coffman conditions for deadlock.",
        "Introduced Resource Allocation Graphs (RAG) and Wait-For Graphs (WFG).",
        "Limitation: Purely theoretical; did not calculate recovery dollar costs.",
    ], COLOR_CYAN)

    add_card(slide3, Inches(4.8), Inches(1.7), Inches(3.7), Inches(5.0), "Modern DBMS (Postgres/InnoDB)", [
        "Standard heuristic: Kill the transaction with the fewest undo entries.",
        "Fast detection, but blind to transaction business priority.",
        "Limitation: Wastes up to 73.5% extra cost by aborting near-complete work.",
    ], COLOR_MUTED)

    add_card(slide3, Inches(8.8), Inches(1.7), Inches(3.7), Inches(5.0), "Deep Learning Models", [
        "Recent AI studies predict deadlocks with neural networks.",
        "High accuracy, but total 'black box'.",
        "Limitation: DBAs refuse to trust AI that kills transactions without giving a reason.",
    ], COLOR_GREEN)

    # -------------------------------------------------------------
    # SLIDE 4: RESEARCH GAP
    # -------------------------------------------------------------
    slide4 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide4)
    add_header(slide4, "The Research Gap: Theory vs Reality", "3. GAP ANALYSIS")

    add_card(slide4, Inches(0.8), Inches(1.7), Inches(5.6), Inches(2.4), "1. The Visualization Gap", [
        "Theory: Drawn on static paper.",
        "Reality: Concurrency is dynamic; students need an interactive simulator to watch locks move.",
    ], COLOR_CYAN)

    add_card(slide4, Inches(6.8), Inches(1.7), Inches(5.7), Inches(2.4), "2. The Fixed-Rule Waste Gap", [
        "Databases use 'Always Terminate' or 'Always Preempt'.",
        "Empirical measurement: Fixed rules waste up to 73.5% more than the optimal choice.",
    ], COLOR_RED)

    add_card(slide4, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.4), "3. The Log Parsing Gap", [
        "Database dumps (PostgreSQL / MySQL) are walls of cryptic text.",
        "DBAs spend minutes manually piecing together who blocks whom.",
    ], COLOR_MUTED)

    add_card(slide4, Inches(6.8), Inches(4.3), Inches(5.7), Inches(2.4), "4. The Explainability (XAI) Gap", [
        "No existing system explains WHY a fix was chosen in plain English.",
        "Need human-understandable justification before executing recovery.",
    ], COLOR_GREEN)

    # -------------------------------------------------------------
    # SLIDE 5: PROBLEM STATEMENT & OBJECTIVES
    # -------------------------------------------------------------
    slide5 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide5)
    add_header(slide5, "Problem Statement & Project Objectives", "4. SCOPE & GOALS")

    add_card(slide5, Inches(0.8), Inches(1.7), Inches(11.7), Inches(2.0), "Problem Statement", [
        "To build an application-based web platform that dynamically detects deadlock cycles in real-time, "
        "evaluates the cost of three classic fixes (Terminate, Rollback, Preempt), and recommends the cheapest "
        "recovery backed by plain-English reasoning and confidence safety-net guarantees.",
    ], COLOR_CYAN)

    add_card(slide5, Inches(0.8), Inches(3.9), Inches(5.6), Inches(2.8), "Primary Objectives", [
        "1. Real-Time Concurrency Simulator (RAG & WFG).",
        "2. Multi-Objective Cost Engine (Kill vs Rollback vs Preempt).",
        "3. Explainable AI Advisor (Plain-English XAI).",
    ], COLOR_GREEN)

    add_card(slide5, Inches(6.8), Inches(3.9), Inches(5.7), Inches(2.8), "Practical Objectives", [
        "4. Confidence Safety Net (Double-check when unsure).",
        "5. Real Database Log Importer (PostgreSQL / MySQL).",
        "6. Live Public Web App (Streamlit Community Cloud).",
    ], COLOR_GREEN)

    # -------------------------------------------------------------
    # SLIDE 6: METHODOLOGY & SYSTEM ARCHITECTURE
    # -------------------------------------------------------------
    slide6 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide6)
    add_header(slide6, "Proposed Methodology: 3-Layer Architecture", "5. ARCHITECTURE")

    add_card(slide6, Inches(0.8), Inches(1.7), Inches(3.7), Inches(5.0), "Layer 1: What User Sees", [
        "🧪 Live Lab: Interactive graph.",
        "🧠 Smart Advisor: Recommended fix + confidence + explanation.",
        "🎛️ What-If Costs: Slider lab.",
        "📥 Import Log: Real DBA dumps.",
        "📊 Scoreboard: Empirical charts.",
        "🚀 Publish Center: Cloud exports.",
    ], COLOR_CYAN)

    add_card(slide6, Inches(4.8), Inches(1.7), Inches(3.7), Inches(5.0), "Layer 2: Python Engine", [
        "Simulator: Multi-workload state machine.",
        "Detector: Bipartite RAG to WFG graph reduction + Tarjan DFS cycle finding.",
        "Recovery Engine: Computes exact costs.",
        "Smart Advisor: Decision Tree + Safety Net.",
        "Log Parser: Regex dump extractor.",
    ], COLOR_GREEN)

    add_card(slide6, Inches(8.8), Inches(1.7), Inches(3.7), Inches(5.0), "Layer 3: Stored Data", [
        "dataset.csv: 6,000 deadlock cases.",
        "model.joblib: Trained explainable Decision Tree surrogate.",
        "sample_logs: Real database traces (Postgres, MySQL, Microservices).",
        "Cloud Artifacts: Dockerfile & CI workflows.",
    ], COLOR_MUTED)

    # -------------------------------------------------------------
    # SLIDE 7: DASHBOARD WORKING & LIVE MODULES
    # -------------------------------------------------------------
    slide7 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide7)
    add_header(slide7, "Working of the Live Dashboard (7 Modules)", "6. HOW IT WORKS")

    add_card(slide7, Inches(0.8), Inches(1.7), Inches(5.6), Inches(2.4), "1. 🧪 Live Lab Screen", [
        "Select workload: 'Dining Philosophers' or 'Bank Lock-Swap'.",
        "Click ▶️ Step or ⏩ Auto-Run to advance time.",
        "When stuck, the cycle illuminates in bright crimson red (#FF1744).",
    ], COLOR_CYAN)

    add_card(slide7, Inches(6.8), Inches(1.7), Inches(5.7), Inches(2.4), "2. 🧠 Smart Advisor Screen", [
        "Card shows winning fix: TERMINATE, ROLLBACK, or PREEMPT.",
        "Gives confidence score and plain-English why/why-not explanation.",
        "Click '⚡ Apply Recommended Fix' to break cycle and resume!",
    ], COLOR_GREEN)

    add_card(slide7, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.4), "3. 🎛️ What-If Costs & 4. 📥 Log Reader", [
        "Move penalty sliders (priority weight, rollback unit cost).",
        "Watch strategy share shift; retrain decision tree in < 1 second.",
        "Upload raw PostgreSQL/MySQL log; app draws the stuck circle.",
    ], COLOR_MUTED)

    add_card(slide7, Inches(6.8), Inches(4.3), Inches(5.7), Inches(2.4), "5. 📊 Scoreboard & 7. 🚀 Cloud Deploy", [
        "Visualizes Figure 2 Safety Net curve (waste vs double-check work).",
        "Export benchmark results as CSV.",
        "Cloud-native deployable on Streamlit Cloud, Docker, and Render.",
    ], COLOR_CYAN)

    # -------------------------------------------------------------
    # SLIDE 8: THREE RECOVERY FIXES & MATHEMATICAL COST MODELS
    # -------------------------------------------------------------
    slide8 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide8)
    add_header(slide8, "Three Recovery Fixes: Mathematical Cost Models", "7. COST FORMULATION")

    add_card(slide8, Inches(0.8), Inches(1.7), Inches(3.7), Inches(5.0), "1. TERMINATE (Kill)", [
        "Abort process and restart transaction.",
        "Cost Equation:",
        "Cost = Base + (Priority × W_prio) + (Progress × W_work)",
        "When it wins: Low priority job that just started (0-10% progress).",
    ], COLOR_RED)

    add_card(slide8, Inches(4.8), Inches(1.7), Inches(3.7), Inches(5.0), "2. ROLLBACK", [
        "Rewind process to nearest checkpoint.",
        "Cost Equation:",
        "Cost = Base + (Steps_Lost × Rate) + (Priority × 0.4)",
        "When it wins: Process has a recent checkpoint (1-2 steps of undo).",
    ], COLOR_CYAN)

    add_card(slide8, Inches(8.8), Inches(1.7), Inches(3.7), Inches(5.0), "3. PREEMPT", [
        "Revoke resource; assign to waiting process.",
        "Cost Equation:",
        "Cost = Base + (Hold_Time × Rate) + (Preempts × Starvation)",
        "When it wins: Zero prior preemption history and holding time is short.",
    ], COLOR_GREEN)

    # -------------------------------------------------------------
    # SLIDE 9: KEY INNOVATIONS (A, B, C, D)
    # -------------------------------------------------------------
    slide9 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide9)
    add_header(slide9, "Four Key Innovations Delivered", "8. INNOVATIONS")

    add_card(slide9, Inches(0.8), Inches(1.7), Inches(5.6), Inches(2.4), "Innovation A: Explain the Advice (XAI)", [
        "Generates human sentences instead of raw numbers.",
        "Example: 'Preempt P2 (Cost: 5.8) because Rollback costs 11.2 and Terminating costs 18.5 destroying 85% work.'",
    ], COLOR_CYAN)

    add_card(slide9, Inches(6.8), Inches(1.7), Inches(5.7), Inches(2.4), "Innovation B: Confidence Safety Net", [
        "If model confidence < cutoff (0.80), double-check all 3 fixes.",
        "Eliminates 98% of waste; achieves 99.6% effective accuracy.",
    ], COLOR_GREEN)

    add_card(slide9, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.4), "Innovation C: What-If Cost Sensitivity", [
        "Interactive sliders allow users to input company-specific costs.",
        "Re-fits the explainable Decision Tree in under 1 second.",
    ], COLOR_MUTED)

    add_card(slide9, Inches(6.8), Inches(4.3), Inches(5.7), Inches(2.4), "Innovation D: Real Database Log Reader", [
        "Reads PostgreSQL 'deadlock detected' and MySQL InnoDB status.",
        "Extracts transaction IDs, builds WFG, and isolates the circle.",
    ], COLOR_CYAN)

    # -------------------------------------------------------------
    # SLIDE 10: RESULTS & EMPIRICAL BENCHMARKS
    # -------------------------------------------------------------
    slide10 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide10)
    add_header(slide10, "Empirical Results: 1,200 Hidden Test Cases", "9. RESULTS")

    add_card(slide10, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.0), "Benchmark Comparison Table", [
        "Fixed: Always Terminate -> 1.9% Acc | 73.5% Extra Waste",
        "Fixed: Always Rollback -> 35.2% Acc | 25.4% Extra Waste",
        "Fixed: Always Preempt -> 62.8% Acc | 8.6% Extra Waste",
        "Smart Advisor (Model Only) -> 84.3% Acc | 2.17% Extra Waste",
        "DeadlockGuard Hybrid (Cutoff 0.80) -> 99.6% Acc | 0.11% Waste!",
        "Perfect Oracle (Cheapest Fix) -> 100% Acc | 0.00% Waste",
    ], COLOR_GREEN)

    add_card(slide10, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.0), "Key Empirical Takeaways", [
        "Fixed rules in modern databases cause severe waste (up to 73.5%).",
        "Explainable Decision Tree achieves 84.3% accuracy alone.",
        "Innovation B Safety Net brings extra waste down to just 0.11%!",
        "Double-checks only 38.4% of cases; cuts compute time by 40% vs exhaustive search.",
        "Formal Engine Verification: All 14 test checks pass 100%.",
    ], COLOR_CYAN)

    # -------------------------------------------------------------
    # SLIDE 11: CONCLUSION & FUTURE WORK
    # -------------------------------------------------------------
    slide11 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide11)
    add_header(slide11, "Conclusion & Future Work", "10. FUTURE SCOPE")

    add_card(slide11, Inches(0.8), Inches(1.7), Inches(5.6), Inches(5.0), "Summary of Achievements", [
        "Built a working, publishable, production-ready web application.",
        "Demonstrated that explainable AI can recommend the cheapest fix reliably.",
        "Provided transparent plain-English reasons for non-expert operators.",
        "Bridged theory with real PostgreSQL and MySQL InnoDB deadlock dumps.",
        "Deploys live in 1 click at https://deadlockguard-1208ak.streamlit.app/",
    ], COLOR_CYAN)

    add_card(slide11, Inches(6.8), Inches(1.7), Inches(5.7), Inches(5.0), "Future Work (Innovations E & F)", [
        "Innovation E (Early Warning Predictor): Train a temporal model to forecast deadlocks 10 ticks before they occur.",
        "Innovation F (Continuous Feedback): Record true post-recovery latency in production to update cost weights via reinforcement learning.",
        "Multi-Unit Resources: Generalize graph reduction to multi-instance resource matrices.",
    ], COLOR_GREEN)

    # -------------------------------------------------------------
    # SLIDE 12: REFERENCES
    # -------------------------------------------------------------
    slide12 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide12)
    add_header(slide12, "References", "11. BIBLIOGRAPHY")

    add_card(slide12, Inches(0.8), Inches(1.7), Inches(11.7), Inches(5.0), "Academic & Technical Citations", [
        "1. Coffman, E. G., Elphick, M., & Shoshani, A. (1971). 'System Deadlocks.' ACM Computing Surveys, 3(2), 67-78.",
        "2. Holt, R. C. (1972). 'Some Deadlock Properties of Computer Systems.' ACM Computing Surveys, 4(3), 179-196.",
        "3. Dijkstra, E. W. (1965). 'Cooperating Sequential Processes.' Technological University, Eindhoven.",
        "4. Silberschatz, A., Galvin, P. B., & Gagne, G. (2018). 'Operating System Concepts (10th Ed).' John Wiley & Sons.",
        "5. PostgreSQL Global Development Group (2024). 'PostgreSQL Documentation: Chapter 13. Concurrency Control.'",
        "6. Oracle Corporation (2024). 'MySQL 8.0 Reference Manual: InnoDB Deadlocks and Lock Modes.'",
        "7. Ribeiro, M. T., Singh, S., & Guestrin, C. (2016). 'Why Should I Trust You?: Explaining Predictions of Any Classifier.' ACM SIGKDD.",
    ], COLOR_WHITE)

    # -------------------------------------------------------------
    # SLIDE 13: VIVA CHEAT SHEET (TOP QUESTIONS & SHORT ANSWERS)
    # -------------------------------------------------------------
    slide13 = prs.slides.add_slide(blank_slide_layout)
    add_slide_bg(slide13)
    add_header(slide13, "Viva Examination Cheat Sheet", "12. ORAL DEFENSE")

    add_card(slide13, Inches(0.8), Inches(1.7), Inches(5.6), Inches(2.4), "Q1: Is this just detection or recovery?", [
        "It does both! Detection is classical (Wait-For Graph cycle finding).",
        "The NOVELTY is dynamically comparing Terminate vs Rollback vs Preempt and picking the cheapest fix.",
    ], COLOR_CYAN)

    add_card(slide13, Inches(6.8), Inches(1.7), Inches(5.7), Inches(2.4), "Q2: Why not always Preempt?", [
        "Always preempting only wins 62.8% of the time and causes starvation.",
        "Our Safety Net brings extra waste down from 8.6% to 0.11%.",
    ], COLOR_GREEN)

    add_card(slide13, Inches(0.8), Inches(4.3), Inches(5.6), Inches(2.4), "Q3: Why a Decision Tree?", [
        "For EXPLAINABILITY (XAI). A neural net is an uninterpretable black box.",
        "A Decision Tree is a transparent flowchart; we can explain the path in plain English.",
    ], COLOR_MUTED)

    add_card(slide13, Inches(6.8), Inches(4.3), Inches(5.7), Inches(2.4), "Q4: Does it work on real databases?", [
        "YES! Module 4 reads real text dumps from PostgreSQL and MySQL InnoDB,",
        "parses transaction locks, builds the graph, and isolates the cycle.",
    ], COLOR_CYAN)

    prs.save(output_file)
    print(f"Presentation saved successfully as: {output_file}")


if __name__ == "__main__":
    create_deck()
