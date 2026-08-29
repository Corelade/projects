import { useEffect, useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router'

import Button from '@/components/button/button'
import ConfirmDialog from '@/components/confirm-dialog/confirm-dialog'
import EmptyState from '@/components/empty-state/empty-state'
import ErrorPanel from '@/components/error-panel/error-panel'
import Icon from '@/components/icon/icon'
import Layout from '@/components/layout/layout'
import Skeleton from '@/components/skeleton/skeleton'
import WeekPicker from '@/components/week-picker/week-picker'
import { currentWeekStart, formatDateTime, formatWeekRange } from '@/lib/dates'
import { useAppDispatch, useAppSelector } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import { useGetDepartmentsQuery } from '@/store/api/departments-api'
import {
  useGenerateWeekMutation,
  useGetWeekQuery,
  useUpdateCellMutation,
} from '@/store/api/schedule-api'
import { useGetStaffQuery } from '@/store/api/staff-api'
import { pushToast, setWeek } from '@/store/slices/ui-slice'
import type { Day, Department, Shift } from '@/types'
import RotaGrid from './rota-grid'
import { cellKey, departmentByStaffDay, hoursByStaff, indexCells } from './rota-model'
import ShiftLegend from './shift-legend'
import StaffPicker from './staff-picker'
import './schedule.css'

interface CellTarget {
  department: Department
  day: Day
  shift: Shift
}

export default function SchedulePage() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const weekStart = useAppSelector((s) => s.ui.selectedWeekStart)

  // The week is linkable: ?week=2026-08-17 is the source of truth on load.
  useEffect(() => {
    const fromUrl = searchParams.get('week')
    if (fromUrl && fromUrl !== weekStart) {
      dispatch(setWeek(fromUrl))
    } else if (!fromUrl) {
      setSearchParams({ week: weekStart }, { replace: true })
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  function changeWeek(next: string) {
    dispatch(setWeek(next))
    setSearchParams({ week: next })
  }

  const week = useGetWeekQuery(weekStart)
  const departments = useGetDepartmentsQuery()
  const staff = useGetStaffQuery()

  const [generateWeek, generateState] = useGenerateWeekMutation()
  const [updateCell, updateState] = useUpdateCellMutation()

  const [target, setTarget] = useState<CellTarget | null>(null)
  const [confirmRegenerate, setConfirmRegenerate] = useState(false)
  const [exporting, setExporting] = useState(false)

  const cells = useMemo(() => indexCells(week.data), [week.data])
  const hours = useMemo(() => hoursByStaff(week.data), [week.data])
  const dayDepartment = useMemo(() => departmentByStaffDay(week.data), [week.data])

  const isLoading = week.isLoading || departments.isLoading || staff.isLoading
  const loadError = week.error ?? departments.error ?? staff.error
  const isError = week.isError || departments.isError || staff.isError

  const hasRota = Boolean(week.data?.cells.length)
  const orderedDepartments = useMemo(
    () =>
      [...(departments.data ?? [])].sort((a, b) =>
        a.name.localeCompare(b.name),
      ),
    [departments.data],
  )

  // Rotas are only generated for weeks that haven't started. The current week is
  // already in play, so it's edited cell by cell rather than regenerated wholesale.
  const isLockedWeek = weekStart <= currentWeekStart()

  async function runGenerate() {
    setConfirmRegenerate(false)
    try {
      await generateWeek(weekStart).unwrap()
      dispatch(pushToast('success', `Rota generated for ${formatWeekRange(weekStart)}.`))
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't generate a rota.")))
    }
  }

  /**
   * jspdf + autotable are ~380kB; loading them on demand keeps them out of the
   * initial bundle, since most visits never export.
   */
  async function downloadPdf() {
    if (!week.data) return
    setExporting(true)
    try {
      const { exportRotaPdf } = await import('./rota-pdf')
      exportRotaPdf(week.data, orderedDepartments)
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't build the PDF.")))
    } finally {
      setExporting(false)
    }
  }

  async function saveCell(staffIds: number[]) {
    if (!target) return
    try {
      await updateCell({
        week_start: weekStart,
        department_id: target.department.id,
        day: target.day,
        shift: target.shift,
        staff_ids: staffIds,
      }).unwrap()
      setTarget(null)
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't update that shift.")))
    }
  }

  const generatedAt = week.data?.generated_at

  return (
    <Layout
      title="Rota"
      description={
        generatedAt ? `Generated ${formatDateTime(generatedAt)}` : undefined
      }
      flush
      actions={
        <>
          <WeekPicker
            weekStart={weekStart}
            onChange={changeWeek}
            disabled={generateState.isLoading}
          />
          <Button
            variant="primary"
            iconLeft={<Icon name="sparkles" size={16} />}
            loading={generateState.isLoading}
            disabled={isLoading || isError || isLockedWeek}
            onClick={() => (hasRota ? setConfirmRegenerate(true) : runGenerate())}
          >
            {hasRota ? 'Regenerate' : 'Generate'}
          </Button>
          <Button
            iconLeft={<Icon name="download" size={16} />}
            disabled={!hasRota || !week.data}
            loading={exporting}
            onClick={downloadPdf}
          >
            Download PDF
          </Button>
        </>
      }
    >
      <div className="flex h-full flex-col gap-4 p-6">
        {/* Print-only header — the screen already shows this in the topbar. */}
        <div className="print-only">
          <h1 style={{ fontSize: '14pt', fontWeight: 700 }}>
            Rota · {formatWeekRange(weekStart)}
          </h1>
          {generatedAt && (
            <p style={{ fontSize: '9pt' }}>Generated {formatDateTime(generatedAt)}</p>
          )}
        </div>

        <ShiftLegend />

        {isError ? (
          <ErrorPanel
            title="Couldn't load the rota"
            message={errorMessage(loadError)}
            onRetry={() => {
              week.refetch()
              departments.refetch()
              staff.refetch()
            }}
            retrying={week.isFetching}
          />
        ) : isLoading ? (
          <RotaSkeleton />
        ) : orderedDepartments.length === 0 ? (
          <div className="rounded-md border border-border bg-surface">
            <EmptyState
              icon="building"
              title="No departments yet"
              description="A rota needs at least one department to schedule staff into."
              action={
                <Button
                  variant="primary"
                  onClick={() => navigate('/departments/new')}
                >
                  Add a department
                </Button>
              }
            />
          </div>
        ) : !hasRota ? (
          <div className="rounded-md border border-border bg-surface">
            <EmptyState
              icon="calendar"
              title={`No rota for ${formatWeekRange(weekStart)}`}
              description="Generate one from your current staff and departments, then adjust any cell by hand."
              action={
                <Button
                  variant="primary"
                  iconLeft={<Icon name="sparkles" size={16} />}
                  loading={generateState.isLoading}
                  disabled={isLockedWeek}
                  onClick={runGenerate}
                >
                  Generate rota
                </Button>
              }
            />
          </div>
        ) : (
          <RotaGrid
            weekStart={weekStart}
            departments={orderedDepartments}
            cells={cells}
            onSelectCell={(department, day, shift) =>
              setTarget({ department, day, shift })
            }
          />
        )}
      </div>

      {target && (
        <StaffPicker
          department={target.department}
          day={target.day}
          shift={target.shift}
          allStaff={staff.data ?? []}
          assignedIds={
            cells
              .get(cellKey(target.department.id, target.day, target.shift))
              ?.staff.map((a) => a.staff_id) ?? []
          }
          hours={hours}
          dayDepartment={dayDepartment}
          saving={updateState.isLoading}
          onSave={saveCell}
          onClose={() => setTarget(null)}
        />
      )}

      {confirmRegenerate && (
        <ConfirmDialog
          title={`Regenerate the rota for ${formatWeekRange(weekStart)}?`}
          description="The current assignments for this week will be replaced. The scheduler is non-deterministic, so you'll get a different valid rota."
          confirmLabel="Regenerate"
          loading={generateState.isLoading}
          onConfirm={runGenerate}
          onCancel={() => setConfirmRegenerate(false)}
        />
      )}
    </Layout>
  )
}

/** Mirrors the grid's shape: label column plus seven day columns. */
function RotaSkeleton() {
  return (
    <div className="min-h-0 flex-1 overflow-hidden rounded-md border border-border bg-surface">
      <div className="flex gap-px border-b border-border p-2">
        <Skeleton width="12rem" />
        {Array.from({ length: 7 }).map((_, i) => (
          <Skeleton key={i} width="100%" />
        ))}
      </div>
      {Array.from({ length: 9 }).map((_, i) => (
        <div key={i} className="flex gap-2 border-b border-border p-2">
          <Skeleton width="12rem" height="2.5rem" variant="rect" />
          {Array.from({ length: 7 }).map((_, j) => (
            <Skeleton key={j} width="100%" height="2.5rem" variant="rect" />
          ))}
        </div>
      ))}
    </div>
  )
}
