#!/usr/bin/env python3
"""
Equity Research PDF Report Template
====================================
Generates a professional equity research snapshot PDF using fpdf2.

Usage:
    python3 equity_research_pdf.py

Customize the DATA dictionaries below with your research data.
All measurements are in points (1/72 inch). Letter size = 612 x 792 pts.
With 0.75" margins, printable width = 504 pts = 7.0 * 72.

Requires: fpdf2 (pip install fpdf2)
"""
from fpdf import FPDF
from datetime import datetime
import os

# ─── CUSTOMIZE THIS DATA ──────────────────────────────────────────

TICKER = "UI"
COMPANY_NAME = "Ubiquiti Inc."
REPORT_DATE = datetime.now().strftime("%B %d, %Y")
OUTPUT_PATH = os.path.expanduser(f "~/{TICKER}_Equity_Research.pdf")

# Current quote data
QUOTE_DATA = [
    ("Price", "$542.26"),
    ("Change", "-$8.73 (-1.58%)"),
    ("Previous Close", "$550.99"),
    ("Day Range", "$539.00 - $553.72"),
    ("52-Week Range", "$380.00 - $1,099.99"),
    ("Volume", "31,404 (avg: 128,718)"),
    ("Market Cap", "$32.8B"),
    ("P/E (TTM)", "34.89"),
    ("EPS (TTM)", "$15.54"),
    ("Beta", "1.31"),
]

# Price performance stats
PERF_DATA = [
    ("1Y Total Return", "+31.47%"),
    ("1Y Low", "$388.83 (Aug 2025)"),
    ("1Y High", "$1,084.50 (Apr 17, 2026)"),
    ("1Y Average", "$643.99"),
    ("Current vs 52W High", "-50.7%"),
    ("Current vs 52W Low", "+42.7%"),
]

# Monthly price trajectory
MONTHLY_DATA = [
    ("Jul 2025", "~$412", "Starting base"),
    ("Aug 2025", "$390 -> $510+", "Big earnings gap-up"),
    ("Oct 2025", "$687 -> $787", "Strong uptrend"),
    ("Nov 2025", "~$515", "Sharp pullback"),
    ("Feb 2026", "~$767", "Recovery rally"),
    ("Apr 2026", "~$1,084", "PEAK"),
    ("May 2026", "~$584", "Crashing"),
    ("Jun 2026", "~$534", "Continued decline"),
    ("Jul 2026", "~$542", "Stabilizing?"),
]

# Company overview paragraph
COMPANY_OVERVIEW = (
    "Ubiquiti Inc. designs and manufactures wireless networking and communications "
    "products under brands including UniFi (enterprise networking), UISP (service "
    "provider gear), and airMAX. Founded by Robert Pera. Known for a unique "
    "go-to-market model - community-driven marketing, minimal salesforce, and "
    "direct-to-consumer distribution."
)

# Bull case bullet points
BULL_CASE = [
    "Strong brand loyalty and ecosystem lock-in",
    "High-margin, asset-light business model with minimal SG&A",
    "The 50% pullback from peak could be a significant reset and entry point",
    "Growing product portfolio (cameras, access points, switching, UniFi OS)",
]

# Bear case bullet points
BEAR_CASE = [
    "35x trailing P/E is still expensive if growth is decelerating",
    "~50% drop from April peak suggests something fundamental changed",
    "Low float / thin volume makes stock volatile and prone to sharp swings",
    "Founder-controlled with concentrated ownership - governance concerns",
    "Competition from Aruba/HPE, Meraki/Cisco and cheap Asian alternatives",
]

# Key risk callout
KEY_RISK = (
    "KEY RISK: The sharp sell-off from $1,084 to $542 in ~3 months is a major "
    "red flag. Either earnings disappointment or technical de-rating. Check "
    "most recent quarterly earnings to understand the catalyst."
)

# ─── PDF GENERATION (do not edit below unless changing layout) ─────

PAGE_WIDTH = 612  # Letter width in points
MARGIN = 0.75 * 72  # 54 points
PRINTABLE_WIDTH = PAGE_WIDTH - 2 * MARGIN  # 504 points = 7.0 * 72

pdf = FPDF(format="Letter")
pdf.set_auto_page_break(auto=True, margin=MARGIN)
pdf.add_page()
pdf.set_left_margin(MARGIN)
pdf.set_right_margin(MARGIN)
pdf.set_top_margin(MARGIN)


def section_header(text):
    """Add a bold section header."""
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 0.3 * 72, text, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(0.05 * 72)


def key_value_table(data, label_width=2.0 * 72, value_width=3.0 * 72):
    """Render a list of (label, value) tuples as a simple two-column layout."""
    for label, value in data:
        pdf.set_font("Helvetica", "", 10)
        pdf.cell(label_width, 0.2 * 72, label)
        pdf.set_font("Helvetica", "B", 10)
        pdf.cell(value_width, 0.2 * 72, value)
        pdf.ln(0.2 * 72)


def bordered_table(headers, rows, col_widths):
    """Render a bordered table with a shaded header row."""
    # Header
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Helvetica", "B", 9)
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 0.22 * 72, header, border=1, fill=True)
    pdf.ln(0.22 * 72)
    # Rows
    pdf.set_font("Helvetica", "", 9)
    for row in rows:
        for i, cell in enumerate(row):
            pdf.cell(col_widths[i], 0.22 * 72, cell, border=1)
        pdf.ln(0.22 * 72)


# ── Title ──
pdf.set_font("Helvetica", "B", 22)
pdf.ln(0.2 * 72)
pdf.cell(0, 0.4 * 72, f"{COMPANY_NAME} ({TICKER})", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 12)
pdf.set_text_color(90, 90, 90)
pdf.cell(0, 0.2 * 72, f"Equity Research Snapshot  |  {REPORT_DATE}", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.ln(0.1 * 72)
pdf.set_draw_color(60, 60, 60)
pdf.set_line_width(0.5)
pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + PRINTABLE_WIDTH, pdf.get_y())
pdf.ln(0.15 * 72)

# ── Current Quote ──
section_header(f"Current Quote ({REPORT_DATE})")
key_value_table(QUOTE_DATA)
pdf.ln(0.1 * 72)

# ── Price Performance ──
section_header("Price Performance (1-Year)")
key_value_table(PERF_DATA)
pdf.ln(0.1 * 72)

# ── Monthly Trajectory ──
section_header("Price Trajectory (Monthly Summary)")
bordered_table(
    ["Period", "Price", "Trend"],
    MONTHLY_DATA,
    [1.5 * 72, 1.5 * 72, 4.0 * 72],
)
pdf.ln(0.15 * 72)

# ── Company Overview ──
section_header("Company Overview")
pdf.multi_cell(PRINTABLE_WIDTH, 0.18 * 72, COMPANY_OVERVIEW)
pdf.ln(0.1 * 72)

# ── Investment Considerations ──
section_header("Investment Considerations")

# Bull case
pdf.set_text_color(0, 120, 0)
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 0.25 * 72, "Bull Case", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.set_font("Helvetica", "", 10)
for item in BULL_CASE:
    pdf.multi_cell(PRINTABLE_WIDTH, 0.18 * 72, f"  -  {item}")
pdf.ln(0.05 * 72)

# Bear case
pdf.set_text_color(180, 0, 0)
pdf.set_font("Helvetica", "B", 11)
pdf.cell(0, 0.25 * 72, "Bear Case", new_x="LMARGIN", new_y="NEXT")
pdf.set_text_color(0, 0, 0)
pdf.set_font("Helvetica", "", 10)
for item in BEAR_CASE:
    pdf.multi_cell(PRINTABLE_WIDTH, 0.18 * 72, f"  -  {item}")
pdf.ln(0.1 * 72)

# ── Key Risk Callout ──
pdf.set_fill_color(255, 245, 230)
pdf.set_draw_color(200, 150, 0)
pdf.set_font("Helvetica", "B", 10)
pdf.multi_cell(PRINTABLE_WIDTH, 0.2 * 72, KEY_RISK, border=1, fill=True)
pdf.ln(0.1 * 72)

# ── Footer ──
pdf.set_font("Helvetica", "", 9)
pdf.set_text_color(120, 120, 120)
pdf.multi_cell(
    PRINTABLE_WIDTH,
    0.16 * 72,
    f"Data sources: Yahoo Finance. Prices as of {REPORT_DATE}. "
    "This report is for informational purposes only and is not investment advice.",
)

# ── Save ──
pdf.output(OUTPUT_PATH)
print(f"Saved: {OUTPUT_PATH}")
print(f"Size: {os.path.getsize(OUTPUT_PATH)} bytes")