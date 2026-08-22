import type { ReactNode } from 'react'
import Navbar from '@/components/navbar/navbar'
import Sidebar from '@/components/sidebar/sidebar'
import { cn } from '@/lib/cn'

export interface LayoutProps {
  title: string
  description?: string
  actions?: ReactNode
  children: ReactNode
  /** Schedule page manages its own padding so the grid can go edge to edge. */
  flush?: boolean
}

/**
 * Flex shell: 260px sidebar, then 64px topbar + scrollable content.
 * Replaces the old grid-cols-20 / grid-rows-10 subgrid shell, which tied every
 * page's internals to a fixed 20x10 grid.
 */
export default function Layout({
  title,
  description,
  actions,
  children,
  flush,
}: LayoutProps) {
  return (
    <div className="app-shell flex h-full w-full overflow-hidden">
      <Sidebar />
      <div className="app-main flex min-w-0 flex-1 flex-col">
        <Navbar title={title} description={description} actions={actions} />
        <main className={cn('app-content min-h-0 flex-1 overflow-auto', !flush && 'p-6')}>
          {children}
        </main>
      </div>
    </div>
  )
}
