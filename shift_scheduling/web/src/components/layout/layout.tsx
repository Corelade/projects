import { useEffect, useState, type ReactNode } from 'react'
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
 *
 * Below `lg` the sidebar leaves the flow and becomes a slide-over the topbar
 * opens; the shell itself is unchanged, so nothing downstream has to care.
 */
export default function Layout({
  title,
  description,
  actions,
  children,
  flush,
}: LayoutProps) {
  const [navOpen, setNavOpen] = useState(false)

  // The slide-over sits over the page, so the page must not scroll under it.
  useEffect(() => {
    if (!navOpen) return
    const previous = document.body.style.overflow
    document.body.style.overflow = 'hidden'
    return () => {
      document.body.style.overflow = previous
    }
  }, [navOpen])

  return (
    <div className="app-shell flex h-full w-full overflow-hidden">
      <Sidebar open={navOpen} onClose={() => setNavOpen(false)} />
      <div className="app-main flex min-w-0 flex-1 flex-col">
        <Navbar
          title={title}
          description={description}
          actions={actions}
          onOpenNav={() => setNavOpen(true)}
        />
        <main
          className={cn(
            'app-content min-h-0 flex-1 overflow-auto',
            !flush && 'p-4 sm:p-6',
          )}
        >
          {children}
        </main>
      </div>
    </div>
  )
}
