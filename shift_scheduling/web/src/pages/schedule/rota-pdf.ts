/**
 * PDF export — jsPDF + autotable.
 *
 * Built from the SAME normalised week data the grid renders, never by scraping
 * the DOM, so the PDF can't drift from the screen (docs/ui/06-print.md).
 * autotable emits real vector text with genuine pagination, unlike the
 * html2canvas approaches which produce an unsearchable screenshot.
 */

import { jsPDF } from 'jspdf'
import autoTable, { type RowInput } from 'jspdf-autotable'

import { formatDayHeader, formatWeekRange, weekEnd } from '@/lib/dates'
import { capitalize } from '@/lib/format'
import type { Department, ScheduleCell, ScheduleWeek } from '@/types'
import { DAYS, SHIFTS } from '@/types'
import { cellKey, coverageOf } from './rota-model'

export function exportRotaPdf(week: ScheduleWeek, departments: Department[]) {
  const doc = new jsPDF({ orientation: 'landscape', format: 'a4', unit: 'mm' })

  const index = new Map<string, ScheduleCell>()
  for (const c of week.cells) index.set(cellKey(c.department_id, c.day, c.shift), c)

  const head: RowInput[] = [
    ['', ...DAYS.map((d) => formatDayHeader(week.week_start, d))],
  ]

  const body: RowInput[] = []
  const deptStartRows: number[] = []

  for (const department of departments) {
    SHIFTS.forEach((shift, shiftIndex) => {
      if (shiftIndex === 0) deptStartRows.push(body.length)

      const label =
        shiftIndex === 0
          ? `${department.name.toUpperCase()}\n${capitalize(shift)}`
          : capitalize(shift)

      const row: RowInput = [label]

      for (const day of DAYS) {
        const cell = index.get(cellKey(department.id, day, shift))
        const staff = cell?.staff ?? []
        const coverage = coverageOf(staff.length, department)
        const count = `${staff.length}/${department.max_staff}`

        // Understaffed carries a glyph and bold count, never a fill.
        const header = coverage === 'under' ? `! ${count}` : count
        const names = staff.length ? staff.map((s) => s.staff_name).join('\n') : '—'
        row.push(`${header}\n${names}`)
      }

      body.push(row)
    })
  }

  const generated = new Date().toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })

  autoTable(doc, {
    head,
    body,
    startY: 22,
    margin: { top: 22, right: 12, bottom: 16, left: 12 },
    theme: 'grid',
    styles: {
      font: 'helvetica',
      fontSize: 7,
      cellPadding: 1.5,
      lineColor: [0, 0, 0],
      lineWidth: 0.1,
      textColor: [0, 0, 0],
      valign: 'top',
    },
    headStyles: {
      fillColor: [255, 255, 255],
      textColor: [0, 0, 0],
      fontStyle: 'bold',
      fontSize: 7,
    },
    columnStyles: { 0: { cellWidth: 32, fontStyle: 'bold' } },
    // Keep a department's three shift rows together.
    rowPageBreak: 'avoid',
    didParseCell(data) {
      if (data.section === 'body' && deptStartRows.includes(data.row.index)) {
        data.cell.styles.lineWidth = { ...data.cell.styles.lineWidth as object, top: 0.5 } as never
      }
    },
    didDrawPage(data) {
      const pageWidth = doc.internal.pageSize.getWidth()
      const pageHeight = doc.internal.pageSize.getHeight()

      doc.setFont('helvetica', 'bold')
      doc.setFontSize(11)
      doc.text(`Rota · ${formatWeekRange(week.week_start)}`, data.settings.margin.left, 14)

      doc.setFont('helvetica', 'normal')
      doc.setFontSize(8)
      doc.text(`Generated ${generated}`, pageWidth - data.settings.margin.right, 14, {
        align: 'right',
      })

      doc.text(
        'Morning / Afternoon / Evening   ·   ! = below minimum staffing',
        data.settings.margin.left,
        19,
      )

      const page = doc.getNumberOfPages()
      doc.text(`Page ${data.pageNumber} of ${page}`, pageWidth / 2, pageHeight - 8, {
        align: 'center',
      })
    },
  })

  doc.save(`rota-${week.week_start}_${weekEnd(week.week_start)}.pdf`)
}
