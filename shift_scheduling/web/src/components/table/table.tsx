import type { ReactNode, ThHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'
import Icon from '@/components/icon/icon'
import './table.css'

export interface TableProps {
  children: ReactNode
  className?: string
  'aria-label': string
}

export function Table({ children, className, ...aria }: TableProps) {
  return (
    <div className="flex-1 overflow-auto">
      <table {...aria} className={cn('data-table', className)}>
        {children}
      </table>
    </div>
  )
}

export interface SortableHeaderProps
  extends ThHTMLAttributes<HTMLTableCellElement> {
  children: ReactNode
  /** Omit to render a non-sortable header. */
  onSort?: () => void
  active?: boolean
  dir?: 'asc' | 'desc'
  align?: 'left' | 'right'
}

export function TH({
  children,
  onSort,
  active,
  dir,
  align = 'left',
  className,
  ...rest
}: SortableHeaderProps) {
  const content = (
    <>
      {children}
      {onSort && (
        <Icon
          name={
            active ? (dir === 'asc' ? 'chevron-up' : 'chevron-down') : 'chevron-up-down'
          }
          size={16}
          className={cn(
            'shrink-0',
            active
              ? 'text-fg'
              : 'text-fg-subtle opacity-0 group-hover/th:opacity-100',
          )}
        />
      )}
    </>
  )

  return (
    <th
      {...rest}
      scope="col"
      aria-sort={active ? (dir === 'asc' ? 'ascending' : 'descending') : undefined}
      className={cn(
        'caption h-(--size-row-header) px-4 whitespace-nowrap',
        align === 'right' ? 'text-right' : 'text-left',
        active && 'text-fg',
        className,
      )}
    >
      {onSort ? (
        <button
          type="button"
          onClick={onSort}
          /* Browsers reset text-transform on <button>, which would drop the
             caption styling inherited from the <th>. */
          className={cn(
            'caption focus-ring group/th inline-flex items-center gap-1 rounded-sm hover:text-fg',
            active && 'text-fg',
          )}
        >
          {content}
        </button>
      ) : (
        <span className="inline-flex items-center gap-1">{content}</span>
      )}
    </th>
  )
}

export interface TRProps {
  children: ReactNode
  onClick?: () => void
  zebra?: boolean
  className?: string
}

export function TR({ children, onClick, zebra, className }: TRProps) {
  return (
    <tr
      onClick={onClick}
      className={cn(
        'group/row h-(--size-row)',
        zebra && 'bg-surface-subtle/60',
        onClick && 'cursor-pointer',
        'hover:bg-surface-subtle',
        className,
      )}
    >
      {children}
    </tr>
  )
}

export interface TDProps {
  children: ReactNode
  align?: 'left' | 'right'
  className?: string
  colSpan?: number
}

export function TD({ children, align = 'left', className, colSpan }: TDProps) {
  return (
    <td
      colSpan={colSpan}
      className={cn(
        'px-4 py-3 text-body text-fg',
        align === 'right' && 'text-right tabular',
        className,
      )}
    >
      {children}
    </td>
  )
}

/** Row-action cell: buttons stay in the DOM and keyboard-reachable always. */
export function RowActions({ children }: { children: ReactNode }) {
  return (
    <div className="flex items-center justify-end gap-1 opacity-0 transition-opacity duration-(--duration-fast) group-hover/row:opacity-100 focus-within:opacity-100">
      {children}
    </div>
  )
}

export function TableFooter({ children }: { children: ReactNode }) {
  return (
    <div className="shrink-0 border-t border-border px-4 py-3 text-small text-fg-muted">
      {children}
    </div>
  )
}
