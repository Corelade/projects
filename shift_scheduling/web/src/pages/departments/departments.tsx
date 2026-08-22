import { useMemo, useState } from 'react'
import { useMatch, useNavigate, useParams } from 'react-router'

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
import type { Errors } from '@/lib/validation'
import { useAppDispatch, useAppSelector } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import {
  useCreateDepartmentMutation,
  useDeleteDepartmentMutation,
  useGetDepartmentsQuery,
  useUpdateDepartmentMutation,
} from '@/store/api/departments-api'
import { pushToast, setDepartmentSearch } from '@/store/slices/ui-slice'
import type { Department, DepartmentInput } from '@/types'
import DepartmentForm, { DEPARTMENT_FORM_ID } from './department-form'
import './departments.css'

function capitalize(word: string) {
  let first_letter = word.slice(0, 1).toUpperCase();
  let rest = word.slice(1);

  return first_letter + rest
}

export default function DepartmentsPage() {
  const dispatch = useAppDispatch()
  const navigate = useNavigate()
  const { id } = useParams()
  const isNew = Boolean(useMatch('/departments/new'))
  const isEdit = Boolean(useMatch('/departments/:id/edit'))

  const search = useAppSelector((s) => s.ui.departmentSearch)

  const { data, isLoading, isError, error, refetch, isFetching } =
    useGetDepartmentsQuery()
  const [createDepartment, createState] = useCreateDepartmentMutation()
  const [updateDepartment, updateState] = useUpdateDepartmentMutation()
  const [deleteDepartment, deleteState] = useDeleteDepartmentMutation()

  const [serverErrors, setServerErrors] = useState<Errors<DepartmentInput>>({})
  const [dirty, setDirty] = useState(false)
  const [confirmDiscard, setConfirmDiscard] = useState(false)
  const [pendingDelete, setPendingDelete] = useState<Department | null>(null)

  const editing = isEdit ? data?.find((d) => d.id === Number(id)) : undefined
  const drawerOpen = isNew || (isEdit && Boolean(editing))
  const submitting = createState.isLoading || updateState.isLoading

  const visible = useMemo(() => {
    if (!data) return []
    const q = search.trim().toLowerCase()
    const filtered = q
      ? data.filter((d) => d.name.toLowerCase().includes(q))
      : data
    return [...filtered].sort((a, b) =>
      a.name.localeCompare(b.name),
    )
  }, [data, search])

  function closeDrawer(force = false) {
    if (dirty && !force) return setConfirmDiscard(true)
    setDirty(false)
    setServerErrors({})
    setConfirmDiscard(false)
    navigate('/departments')
  }

  async function handleSubmit(value: DepartmentInput) {
    setServerErrors({})
    try {
      if (editing) {
        await updateDepartment({ ...value, id: editing.id }).unwrap()
        dispatch(pushToast('success', `${value.name} updated.`))
      } else {
        await createDepartment(value).unwrap()
        dispatch(pushToast('success', `${value.name} added.`))
      }
      setDirty(false)
      closeDrawer(true)
    } catch (err) {
      const message = errorMessage(err, "Couldn't save this department.")
      if (message.toLowerCase().includes('exist')) {
        setServerErrors({ name: message })
      }
      dispatch(pushToast('error', message))
    }
  }

  async function handleDelete() {
    if (!pendingDelete) return
    try {
      await deleteDepartment(pendingDelete.id).unwrap()
      dispatch(pushToast('success', `${pendingDelete.name} removed.`))
      setPendingDelete(null)
    } catch (err) {
      dispatch(pushToast('error', errorMessage(err, "Couldn't delete that department.")))
    }
  }

  return (
    <Layout
      title="Departments"
      description="Where staff can be assigned, and how many each shift needs."
      actions={
        <Button
          variant="primary"
          iconLeft={<Icon name="plus" size={16} />}
          onClick={() => navigate('/departments/new')}
        >
          Add department
        </Button>
      }
    >
      <div className="flex h-full flex-col gap-4">
        <SearchInput
          aria-label="Search departments"
          placeholder="Search departments"
          value={search}
          onChange={(v) => dispatch(setDepartmentSearch(v))}
        />

        {isError ? (
          <ErrorPanel
            title="Couldn't load departments"
            message={errorMessage(error)}
            onRetry={refetch}
            retrying={isFetching}
          />
        ) : (
          <div className="flex min-h-0 flex-1 flex-col overflow-hidden rounded-md border border-border bg-surface">
            {isLoading ? (
              <DepartmentsTableSkeleton />
            ) : visible.length === 0 ? (
              <EmptyState
                icon="building"
                title={search ? 'No matching departments' : 'No departments yet'}
                description={
                  search
                    ? 'Try a different name.'
                    : 'Add the areas staff can be scheduled into.'
                }
                action={
                  search ? undefined : (
                    <Button
                      variant="primary"
                      iconLeft={<Icon name="plus" size={16} />}
                      onClick={() => navigate('/departments/new')}
                    >
                      Add department
                    </Button>
                  )
                }
              />
            ) : (
              <>
                <Table aria-label="Departments" className="departments-table">
                  <thead>
                    <tr>
                      <TH className="col-name">Department</TH>
                      <TH className="col-min" align="right">
                        Min staff
                      </TH>
                      <TH className="col-max" align="right">
                        Max staff
                      </TH>
                      <TH className="col-actions">
                        <span className="sr-only">Actions</span>
                      </TH>
                    </tr>
                  </thead>
                  <tbody>
                    {visible.map((d, i) => (
                      <TR
                        key={d.id}
                        zebra={i % 2 === 1}
                        onClick={() => navigate(`/departments/${d.id}/edit`)}
                      >
                        <TD className="font-medium">{capitalize(d.name)}</TD>
                        <TD align="right">{d.min_staff}</TD>
                        <TD align="right">{d.max_staff}</TD>
                        <TD>
                          <RowActions>
                            <Button
                              variant="ghost"
                              size="sm"
                              aria-label={`Edit ${d.name}`}
                              onClick={(e) => {
                                e.stopPropagation()
                                navigate(`/departments/${d.id}/edit`)
                              }}
                            >
                              <Icon name="pencil" size={16} />
                            </Button>
                            <Button
                              variant="ghost"
                              size="sm"
                              aria-label={`Delete ${d.name}`}
                              onClick={(e) => {
                                e.stopPropagation()
                                setPendingDelete(d)
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
                  Showing {visible.length} of {data?.length ?? 0} departments
                </TableFooter>
              </>
            )}
          </div>
        )}
      </div>

      {drawerOpen && (
        <Drawer
          title={editing ? 'Edit department' : 'Add department'}
          subtitle={
            editing ? 'Update its staffing range' : 'Name and staffing range'
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
                form={DEPARTMENT_FORM_ID}
                variant="primary"
                loading={submitting}
                fullWidth
              >
                {editing ? 'Save changes' : 'Add department'}
              </Button>
            </div>
          }
        >
          <DepartmentForm
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
          title={`Delete ${pendingDelete.name}?`}
          description="Its assignments disappear from every rota. This can't be undone."
          confirmLabel="Delete"
          loading={deleteState.isLoading}
          onConfirm={handleDelete}
          onCancel={() => setPendingDelete(null)}
        />
      )}
    </Layout>
  )
}

function DepartmentsTableSkeleton() {
  return (
    <div className="flex flex-col">
      <div className="flex h-(--size-row-header) items-center gap-4 border-b border-border px-4">
        <Skeleton width="30%" />
        <Skeleton width="12%" />
      </div>
      {Array.from({ length: 4 }).map((_, i) => (
        <div
          key={i}
          className="flex h-(--size-row) items-center gap-4 border-b border-border px-4 last:border-b-0"
        >
          <Skeleton width="34%" />
          <Skeleton width="8%" />
          <Skeleton width="8%" />
        </div>
      ))}
    </div>
  )
}
