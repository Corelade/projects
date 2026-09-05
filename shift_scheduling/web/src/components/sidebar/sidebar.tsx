import { useEffect } from 'react'
import { NavLink } from 'react-router'
import { cn } from '@/lib/cn'
import Icon, { type IconName } from '@/components/icon/icon'
import Logo from '@/components/logo/logo'

interface NavItem {
  to: string
  label: string
  icon: IconName
}

const NAV: NavItem[] = [
  { to: '/schedule', label: 'Schedule', icon: 'calendar' },
  { to: '/staff', label: 'Staff', icon: 'users' },
  { to: '/departments', label: 'Departments', icon: 'building' },
]

export interface SidebarProps {
  /** Only meaningful below `lg`, where the sidebar is a slide-over. */
  open: boolean
  onClose: () => void
}

/**
 * Three shapes, per docs/ui/05-screens.md:
 *   >= xl   full 260px rail with labels
 *   lg-xl   72px icon rail — labels are dropped, not truncated
 *   < lg    off-canvas slide-over over a backdrop, opened from the topbar
 *
 * Below `lg` it is closed by default and `invisible`, which is what keeps its
 * links out of the tab order while they're off-screen. Every link closes it on
 * the way out — including a tap on the link that's already active, which
 * watching the route for a change would miss.
 */
export default function Sidebar({ open, onClose }: SidebarProps) {
  // Esc closes the slide-over. Harmless above `lg`, where `open` stays false.
  useEffect(() => {
    if (!open) return
    function onKeyDown(e: KeyboardEvent) {
      if (e.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [open, onClose])

  return (
    <>
      {open && (
        <div
          className="no-print fixed inset-0 bg-backdrop lg:hidden"
          style={{ zIndex: 'var(--z-backdrop)' }}
          onClick={onClose}
          aria-hidden="true"
        />
      )}

      <aside
        className={cn(
          'no-print flex shrink-0 flex-col border-r border-border bg-surface',
          // < lg: off-canvas
          'fixed inset-y-0 left-0 w-(--size-sidebar) shadow-md',
          'transition-[transform,visibility] duration-(--duration-slow) ease-(--ease-drawer)',
          open ? 'visible translate-x-0' : 'invisible -translate-x-full',
          // lg: icon rail, back in the page flow
          'lg:visible lg:static lg:w-(--size-sidebar-rail) lg:translate-x-0 lg:shadow-none',
          // xl: full width
          'xl:w-(--size-sidebar)',
        )}
        style={{ zIndex: 'var(--z-overlay)' }}
      >
        <div className="flex h-(--size-topbar) shrink-0 items-center gap-2 px-5 lg:justify-center lg:px-0 xl:justify-start xl:px-5">
          <NavLink
            to="/schedule"
            className="focus-ring flex min-w-0 items-center gap-2.5 rounded-sm text-h3 font-semibold text-fg"
          >
            <Logo size={24} className="shrink-0 text-brand-600" />
            <span className="lg:hidden xl:inline">ShiftPro</span>
          </NavLink>

          <button
            type="button"
            onClick={onClose}
            aria-label="Close menu"
            className="focus-ring ml-auto flex size-8 shrink-0 items-center justify-center rounded-md text-fg-muted hover:bg-surface-subtle hover:text-fg lg:hidden"
          >
            <Icon name="x" size={20} />
          </button>
        </div>

        <nav className="flex-1 px-3 py-2 lg:px-2 xl:px-3" aria-label="Main">
          <ul className="flex flex-col gap-0.5">
            {NAV.map((item) => (
              <li key={item.to}>
                <NavLink
                  to={item.to}
                  onClick={onClose}
                  /* The label is display:none in the rail, so the accessible
                     name has to come from the attribute at every width. */
                  aria-label={item.label}
                  title={item.label}
                  className={({ isActive }) =>
                    cn(
                      'focus-ring relative flex items-center gap-2.5 rounded-md px-3 py-2 text-body transition-colors duration-(--duration-fast)',
                      'lg:justify-center lg:px-0 xl:justify-start xl:px-3',
                      isActive
                        ? 'bg-brand-50 font-medium text-brand-700'
                        : 'text-fg-muted hover:bg-surface-subtle hover:text-fg',
                    )
                  }
                >
                  {({ isActive }) => (
                    <>
                      {isActive && (
                        <span className="absolute left-0 top-1/2 h-5 w-0.5 -translate-y-1/2 rounded-full bg-brand-600" />
                      )}
                      <Icon name={item.icon} size={20} className="shrink-0" />
                      <span className="lg:hidden xl:inline">{item.label}</span>
                    </>
                  )}
                </NavLink>
              </li>
            ))}
          </ul>
        </nav>

        <div className="shrink-0 border-t border-border px-3 py-3 lg:px-2 xl:px-3">
          <a
            href="mailto:support@shiftpro.test"
            onClick={onClose}
            aria-label="Support"
            title="Support"
            className="focus-ring flex items-center gap-2.5 rounded-md px-3 py-2 text-body text-fg-muted hover:bg-surface-subtle hover:text-fg lg:justify-center lg:px-0 xl:justify-start xl:px-3"
          >
            <Icon name="question" size={20} className="shrink-0" />
            <span className="lg:hidden xl:inline">Support</span>
          </a>
        </div>
      </aside>
    </>
  )
}
