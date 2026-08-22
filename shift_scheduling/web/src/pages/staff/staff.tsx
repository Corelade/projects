import { useMemo, useState } from 'react'
import { useNavigate, useParams, useMatch } from 'react-router'

import Avatar from '@/components/avatar/avatar'
import Badge from '@/components/badge/badge'
import Button from '@/components/button/button'
import ConfirmDialog from '@/components/confirm-dialog/confirm-dialog'
import Drawer from '@/components/drawer/drawer'
import EmptyState from '@/components/empty-state/empty-state'
import ErrorPanel from '@/components/error-panel/error-panel'
import Icon from '@/components/icon/icon'
import Layout from '@/components/layout/layout'
import SearchInput from '@/components/search-input/search-input'
import Skeleton from '@/components/skeleton/skeleton'
import {
  RowActions,
  Table,
  TableFooter,
  TD,
  TH,
  TR,
} from '@/components/table/table'
import { fullName, initials, summariseExclusions } from '@/lib/format'
import type { Errors } from '@/lib/validation'
import { useAppDispatch, useAppSelector } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import {
  useCreateStaffMutation,
  useDeleteStaffMutation,
  useGetStaffQuery,
  useUpdateStaffMutation,
} from '@/store/api/staff-api'
import { pushToast, setStaffSearch, setStaffSort } from '@/store/slices/ui-slice'
import { POSITION_LABELS, type Staff, type StaffInput } from '@/types'
import StaffForm, { STAFF_FORM_ID } from './staff-form'
import './staff.css'

export default function StaffPage() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { id } = useParams()
  const isNew = Boolean(useMatch('/staff/new'))
  const isEdit = Boolean(useMatch('/staff/:id/edit'))

  const search = useAppSelector((s) => s.ui.staffSearch)
  const sort = useAppSelector((s) => s.ui.staffSort)

  const { data, isLoading, isError, error, refetch, isFetching } =
    useGetStaffQuery()
  const [createStaff, createState] = useCreateStaffMutation()
  const [updateStaff, updateState] = useUpdateStaffMutation()
  const [deleteStaff, deleteState] = useDeleteStaffMutation()

  const [serverErrors, setServerErrors] = useState<Errors<StaffInput>>({})
  const [dirty, setDirty] = useState(false)
  const [confirmDiscard, setConfirmDiscard] = useState(false)
  const [pendingDelete, setPendingDelete] = useState<Staff | null>(null)

  const editing = isEdit ? data?.find((s) => s.id === Number(id)) : undefined
  const drawerOpen = isNew || (isEdit && Boolean(editing))
  const submitting = createState.isLoading || updateState.isLoading

  const visible = useMemo(() => {
    if (!data) return []
    const q = search.trim().toLowerCase()
    const filtered = q
      ? data.filter(
          (s) =>
            fullName(s).toLowerCase().includes(q) ||
            s.email.toLowerCase().includes(q) ||
            POSITION_LABELS[s.position].toLowerCase().includes(q),
        )
      : data

    const dir = sort.dir === 'asc' ? 1 : -1
    return [...filtered].sort((a, b) => {
      if (sort.key === 'name') return fullName(a).localeCompare(fullName(b)) * dir
      const av = a[sort.key as keyof Staff]
      const bv = b[sort.key as keyof Staff]
      if (typeof av === 'number' && typeof bv === 'number') return (av - bv) * dir
      return String(av).localeCompare(String(bv)) * dir
    })
  }, [data, search, sort])

  function toggleSort(key: typeof sort.key) {
    dispatch(
      setStaffSort({
        key,
        dir: sort.key === key && sort.dir === 'asc' ? 'desc' : 'asc',
      }),
    )
  }

  function closeDrawer(force = false) {
    if (dirty && !force) return setConfirmDiscard(true)
    setDirty(false)
    setServerErrors({})
    setConfirmDiscard(false)
    navigate('/staff')
  }

  async function handleSubmit(value: StaffInput) {
    setServerErrors({})
    try {
      if (editing) {
        await updateStaff({ ...value, id: editing.id }).unwrap()
        dispatch(pushToast('success', `${fullName(value)} updated.`))
      } else {
        await createStaff(value).unwrap()
        dispatch(pushToast('success', `${fullName(value)} added to the roster.`))
      }
      setDirty(false)
      closeDrawer(true)
    } catch (err) {
      const message = errorMessage(err, "Couldn't save this staff member.")
      // Map what we can onto the field it belongs to.
      if (message.toLowerCase().includes('email')) {
        setServerErrors({ email: message })
      }
      dispatch(pushToast('error', message))
    }
  }

  async function handleDelete() {
    if (!pendingDelete) return
    try {
      await deleteStaff(pendingDelete.id).unwrap()
      dispatch(pushToast('success', `${fullName(pendingDelete)} removed.`))
      setPendingDelete(null)
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't delete that staff member.")))
    }
  }

  return (
    <Layout
      title="Staff"
      description="Everyone the scheduler can assign, and when they can't work."
      actions={
        <Button
          variant="primary"
          iconLeft={<Icon name="plus" size={16} />}
          onClick={() => navigate('/staff/new')}
        >
          Add staff
        </Button>
      }
    >
      <div className="flex h-full flex-col gap-4">
        <SearchInput
          aria-label="Search staff"
          placeholder="Search by name, email or position"
          value={search}
          onChange={(v) => dispatch(setStaffSearch(v))}
        />

        {isError ? (
          <ErrorPanel
            title="Couldn't load the roster"
            message={errorMessage(error)}
            onRetry={refetch}
            retrying={isFetching}
          />
        ) : (
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-md border border-border bg-surface">
            {isLoading ? (
              <StaffTableSkeleton />
            ) : visible.length === 0 ? (
              <EmptyState
                icon="users"
                title={search ? 'No matching staff' : 'No staff yet'}
                description={
                  search
                    ? 'Try a different name, email or position.'
                    : 'Add the people the scheduler can assign to shifts.'
                }
                action={
                  search ? undefined : (
                    <Button
                      variant="primary"
                      iconLeft={<Icon name="plus" size={16} />}
                      onClick={() => navigate('/staff/new')}
                    >
                      Add staff
                    </Button>
                  )
                }
              />
            ) : (
              <>
                <Table aria-label="Staff roster" className="staff-table">
                  <thead>
                    <tr>
                      <TH
                        className="col-name"
                        onSort={() => toggleSort('name')}
                        active={sort.key === 'name'}
                        dir={sort.dir}
                      >
                        Name
                      </TH>
                      <TH
                        className="col-position"
                        onSort={() => toggleSort('position')}
                        active={sort.key === 'position'}
                        dir={sort.dir}
                      >
                        Position
                      </TH>
                      <TH
                        className="col-contract"
                        align="right"
                        onSort={() => toggleSort('contract_hours')}
                        active={sort.key === 'contract_hours'}
                        dir={sort.dir}
                      >
                        Contract
                      </TH>
                      <TH className="col-min" align="right">
                        Minimum
                      </TH>
                      <TH className="col-unavailable">Unavailable</TH>
                      <TH className="col-actions">
                        <span className="sr-only">Actions</span>
                      </TH>
                    </tr>
                  </thead>
                  <tbody>
                    {visible.map((s, i) => (
                      <TR
                        key={s.id}
                        zebra={i % 2 === 1}
                        onClick={() => navigate(`/staff/${s.id}/edit`)}
                      >
                        <TD className="cell-name">
                          <span className="flex items-center gap-2.5">
                            <Avatar initials={initials(s)} />
                            <span className="flex flex-col">
                              <span className="font-medium">{fullName(s)}</span>
                              <span className="text-small text-fg-muted">
                                {s.email}
                              </span>
                            </span>
                          </span>
                        </TD>
                        <TD>
                          <Badge>{POSITION_LABELS[s.position]}</Badge>
                        </TD>
                        <TD align="right">{s.contract_hours} h</TD>
                        <TD align="right">{s.min_hours} h</TD>
                        <TD className="text-fg-muted">
                          {summariseExclusions(s.day_exclusions, s.shift_exclusions)}
                        </TD>
                        <TD>
                          <RowActions>
                            <Button
                              variant="ghost"
                              size="sm"
                              aria-label={`Edit ${fullName(s)}`}
                              onClick={(e) => {
                                e.stopPropagation()
                                navigate(`/staff/${s.id}/edit`)
                              }}
                            >
                              <Icon name="pencil" size={16} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              aria-label={`Delete ${fullName(s)}`}
                              onClick={(e) => {
                                e.stopPropagation()
                                setPendingDelete(s)
                              }}
                            >
                              <Icon name="trash" size={16} />
                            </Button>
                          </RowActions>
                        </TD>
                      </TR>
                    ))}
                  </tbody>
                </Table>
                <TableFooter>
                  Showing {visible.length} of {data?.length ?? 0} staff
                </TableFooter>
              </>
            )}
          </div>
        )}
      </div>

      {drawerOpen && (
        <Drawer
          title={editing ? 'Edit staff' : 'Add staff'}
          subtitle={
            editing
              ? 'Update their profile and availability'
              : 'Profile and exclusion logic'
          }
          onClose={() => closeDrawer()}
          footer={
            <div className="flex gap-2">
              <Button
                type="button"
                onClick={() => closeDrawer()}
                disabled={submitting}
                fullWidth
              >
                Cancel
              </Button>
              <Button
                type="submit"
                form={STAFF_FORM_ID}
                variant="primary"
                loading={submitting}
                fullWidth
              >
                {editing ? 'Save changes' : 'Add staff'}
              </Button>
            </div>
          }
        >
          <StaffForm
            initial={editing}
            submitting={submitting}
            serverErrors={serverErrors}
            onSubmit={handleSubmit}
            onDirtyChange={setDirty}
          />
        </Drawer>
      )}

      {confirmDiscard && (
        <ConfirmDialog
          title="Discard your changes?"
          description="This form has unsaved changes. Closing it will lose them."
          confirmLabel="Discard"
          cancelLabel="Keep editing"
          onConfirm={() => closeDrawer(true)}
          onCancel={() => setConfirmDiscard(false)}
        />
      )}

      {pendingDelete && (
        <ConfirmDialog
          title={`Delete ${fullName(pendingDelete)}?`}
          description="They'll be removed from all future rotas. This can't be undone."
          confirmLabel="Delete"
          loading={deleteState.isLoading}
          onConfirm={handleDelete}
          onCancel={() => setPendingDelete(null)}
        />
      )}
    </Layout>
  )
}

/** Mirrors the shape of the real table: right row height, right column widths. */
function StaffTableSkeleton() {
  return (
    <div className="flex flex-col">
      <div className="flex h-(--size-row-header) items-center gap-4 border-b border-border px-4">
        <Skeleton width="20%" />
        <Skeleton width="12%" />
        <Skeleton width="10%" />
      </div>
      {Array.from({ length: 6 }).map((_, i) => (
        <div
          key={i}
          className="flex h-(--size-row) items-center gap-3 border-b border-border px-4 last:border-b-0"
        >
          <Skeleton variant="circle" width={32} height={32} />
          <Skeleton width="22%" />
          <Skeleton width="12%" />
          <Skeleton width="8%" />
          <Skeleton width="16%" />
        </div>
      ))}
    </div>
  )
}
