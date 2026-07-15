---
name: pdf-report-generation
description: Generate PDF reports from structured data using fpdf2. Covers the fpdf2 pitfalls (multi_cell width, venv mismatches), layout patterns for professional reports, and the workflow for delivering PDFs to the user. Use when the user asks for output as a PDF, to export a report as PDF, or to convert research/analysis output into a downloadable PDF file.
---

# PDF Report Generation

Generate professional PDF reports from structured data using the `fpdf2` library.

## When to Use

- User asks for research output, analysis, or a report "as a PDF"
- User wants a downloadable PDF version of any structured content
- Converting equity research, market analysis, or other briefing output to PDF

## Prerequisites

- `fpdf2` package: check with `python3 -c "import fpdf"`
- Install if needed: `pip install fpdf2`
- **Critical:** `execute_code` runs in the Hermes venv which may NOT have fpdf2 installed. If the import fails in `execute_code`:
  1. Write the generation script to a file using `write_file`
  2. Run it via `terminal` with the user's Python (e.g., `/Users/james/miniconda3/bin/python3`)
  3. Check available Pythons: `which python3`, `ls /Users/james/miniconda3/bin/python3`

## Workflow

1. **Check fpdf2 availability** — try importing in execute_code first; if that fails, find the user's Python that has it
2. **Write the script** to a file (e.g., `/Users/james/<NAME>_report.py`) using `write_file`
3. **Run the script** via `terminal` with the correct Python
4. **Verify the output** — check `file <output>.pdf` returns "PDF document" and `ls -lh` shows reasonable size
5. **Report the path** to the user — on iMessage/DM platforms, note that file attachments may not be deliverable directly; offer to email or AirDrop

## Layout Patterns

### Page Setup (US Letter, 0.75" margins)

```python
from fpdf import FPDF
pdf = FPDF(format="Letter")
pdf.set_auto_page_break(auto=True, margin=0.75 * 72)
pdf.add_page()
pdf.set_left_margin(0.75 * 72)
pdf.set_right_margin(0.75 * 72)
pdf.set_top_margin(0.75 * 72)
```

### Section Headers

```python
pdf.set_font("Helvetica", "B", 14)
pdf.cell(0, 0.3 * 72, "Section Title", new_x="LMARGIN", new_y="NEXT")
pdf.set_font("Helvetica", "", 10)
```

### Key-Value Tables

```python
for label, value in data:
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(2.0 * 72, 0.2 * 72, label)
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(3.0 * 72, 0.2 * 72, value)
    pdf.ln(0.2 * 72)
```

### Bordered Tables with Header Row

```python
pdf.set_fill_color(240, 240, 240)
pdf.set_font("Helvetica", "B", 9)
pdf.cell(1.5 * 72, 0.22 * 72, "Col1", border=1, fill=True)
pdf.cell(1.5 * 72, 0.22 * 72, "Col2", border=1, fill=True)
pdf.ln(0.22 * 72)

pdf.set_font("Helvetica", "", 9)
for row in rows:
    pdf.cell(1.5 * 72, 0.22 * 72, row[0], border=1)
    pdf.cell(1.5 * 72, 0.22 * 72, row[1], border=1)
    pdf.ln(0.22 * 72)
```

### Callout Box (Key Risk / Warning)

```python
pdf.set_fill_color(255, 245, 230)  # warm amber background
pdf.set_draw_color(200, 150, 0)   # amber border
pdf.set_font("Helvetica", "B", 10)
pdf.multi_cell(7.0 * 72, 0.2 * 72, "WARNING TEXT HERE", border=1, fill=True)
```

### Horizontal Rule

```python
pdf.set_draw_color(60, 60, 60)
pdf.set_line_width(0.5)
pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 7.0 * 72, pdf.get_y())
pdf.ln(0.15 * 72)
```

## Pitfalls

### 1. `multi_cell(0, h, text)` FAILS with custom margins

**The error:** `FPDFException: Not enough horizontal space to render a single character`

**The cause:** When margins are set via `set_left_margin`/`set_right_margin`, `multi_cell` with width `0` does not account for the reduced printable area and calculates negative available width.

**The fix:** Always pass an **explicit width** instead of `0`. For Letter (8.5") with 0.75" margins on both sides, the printable width is `7.0 * 72` points.

```python
# WRONG — crashes when margins are set
pdf.multi_cell(0, 0.18 * 72, text)

# RIGHT — explicit width
pdf.multi_cell(7.0 * 72, 0.18 * 72, text)
```

### 2. `ln=True` parameter deprecated in fpdf2 >= 2.5.2

Use `new_x="LMARGIN", new_y="NEXT"` instead. The old parameter still works but emits deprecation warnings to stderr.

### 3. All measurements are in points (1/72 inch)

- 1 inch = 72 points
- 0.75" margin = `0.75 * 72` = 54 points
- Letter width 8.5" = 612 points; height 11" = 792 points
- Printable width with 0.75" margins = `7.0 * 72` = 504 points

### 4. execute_code venv vs user Python

`execute_code` runs in `/Users/james/.hermes/hermes-agent/venv/bin/python` — packages installed in the user's conda/system Python are NOT available there. If fpdf2 (or any package) imports fine in `terminal` but fails in `execute_code`, write the script to a file and run it via `terminal` with the correct Python path.

## Templates

- `templates/equity_research_pdf.py` — Full example: equity research snapshot with quote table, price performance, monthly trajectory table, company overview, bull/bear case, and key risk callout. Adapt this for any structured report.

## Verification

After generating the PDF:

```bash
file /Users/james/<NAME>.pdf
# Should output: PDF document, version 1.3, N pages

ls -lh /Users/james/<NAME>.pdf
# Should show a reasonable file size (typically 3-15 KB for text-only reports)
```