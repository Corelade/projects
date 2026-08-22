# 06 — Print & PDF

Two independent paths to paper, because they fail differently:

| Path | Mechanism | When |
|---|---|---|
| **Print** | `styles/print.css`, triggered by ⌘P | Quick, whatever's on screen |
| **PDF** | `jspdf` + `jspdf-autotable`, the *Download PDF* button | A file to send or archive |

Both must produce the same rota. If they diverge, that's drift.

---

## Print stylesheet

`web/src/styles/print.css`, imported once globally.

### Page setup

```css
@page {
  size: A4 landscape;
  margin: 12mm;
}
```

Landscape is mandatory — seven day columns plus a label column will not fit
portrait at a legible size.

### What disappears

`.no-print` on: sidebar, topbar, week-picker controls, Generate button, Download
button, search inputs, row action buttons, toasts, drawers.

What appears instead — `.print-only`:
- **Header**: "Rota · 17 – 23 Aug 2026" and "Generated 21 Aug 2026".
- **Footer**: page `n` of `m` via `@page` counters.
- The **shift legend**, always. A printed rota with no legend is undecodable.

### Ink and contrast

Screen tints do not survive photocopying, so print rewrites them:

| Screen | Print |
|---|---|
| Shift tint fills | White fill; shift named in the row label |
| Coverage rose tint | White fill + bold `⚠` + bold headcount |
| Zebra rows | Removed |
| Borders slate-200 | `#000` at 0.5pt |
| Body text | `#000` |

```css
@media print {
  * { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
}
```

is deliberately **not** used for the grid — we want it to print as line art, not
as washed-out colour blocks.

### Pagination

```css
thead { display: table-header-group; }   /* repeat header on every page */
tr, .rota-dept-group { break-inside: avoid; }
.rota-dept-group { break-after: auto; }
```

A department's three shift rows never split across a page break. If a whole
department group can't fit, it moves to the next page intact.

### Typography in print

Body drops to 10pt, caption to 8pt — a full week at 14pt does not fit. Staff
names wrap rather than truncate: an ellipsis on paper is useless, since nobody
can hover it.

---

## PDF export

**Library:** `jspdf` + `jspdf-autotable`.

Chosen over html2canvas-based approaches (`html2pdf.js`, `react-to-pdf`) because
those rasterise the DOM — producing a screenshot that is blurry when zoomed,
unsearchable, unselectable, and heavy. A rota *is* a table; `autotable` emits
real vector text with genuine pagination and repeating headers.

### Output

| Property | Value |
|---|---|
| Orientation | landscape |
| Format | A4 |
| Filename | `rota-2026-08-17_2026-08-23.pdf` |
| Header | "Rota · 17 – 23 Aug 2026" left, "Generated 21 Aug 2026" right |
| Footer | "Page n of m", centred |
| Font | Helvetica (jsPDF built-in) — Inter would need embedding for marginal gain |

### Structure

Built from the **same normalised week data the grid renders**, not by scraping
the DOM. One source of truth means the PDF can't drift from the screen.

```
columns: ['', 'Mon 17', 'Tue 18', … 'Sun 23']
body:    per department → three shift rows
         first cell: 'Morning  1/1'
         other cells: staff names, newline-separated
```

Department group headers use `autotable`'s row styling; understaffed cells get
a bold `⚠` prefix, not a fill.

`didDrawPage` writes the header and footer on each page. `rowPageBreak: 'avoid'`
keeps a department's rows together.

### Empty week

The button is disabled when there is no rota. It never exports a blank grid.

---

## Testing both

Part of the drift audit:

1. ⌘P on a full week → landscape, one page for ~4 departments, header repeated,
   no department split.
2. Print to greyscale → every shift and every warning still identifiable.
3. Export PDF → select text in the viewer (proves it's vector, not an image).
4. Compare the PDF against the screen — same staff, same order, same warnings.
5. A week with 8+ departments → paginates cleanly, no orphaned rows.

---
*Changelog: 2026-08-21 — initial.*
