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

export default function Sidebar() {
  return (
    <aside className="no-print flex w-(--size-sidebar) shrink-0 flex-col border-r border-border bg-surface">
      <div className="flex h-(--size-topbar) shrink-0 items-center px-5">
        <NavLink
          to="/schedule"
          className="focus-ring flex items-center gap-2.5 rounded-sm text-h3 font-semibold text-fg"
        >
          <Logo size={24} className="text-brand-600" />
          ShiftPro
        </NavLink>
      </div>

      <nav className="flex-1 px-3 py-2" aria-label="Main">
        <ul className="flex flex-col gap-0.5">
          {NAV.map((item) => (
            <li key={item.to}>
              <NavLink
                to={item.to}
                className={({ isActive }) =>
                  cn(
                    'focus-ring relative flex items-center gap-2.5 rounded-md px-3 py-2 text-body transition-colors duration-(--duration-fast)',
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
                    {item.label}
                  </>
                )}
              </NavLink>
            </li>
          ))}
        </ul>
      </nav>

      <div className="shrink-0 border-t border-border px-3 py-3">
        <a
          href="mailto:support@shiftpro.test"
          className="focus-ring flex items-center gap-2.5 rounded-md px-3 py-2 text-body text-fg-muted hover:bg-surface-subtle hover:text-fg"
        >
          <Icon name="question" size={20} className="shrink-0" />
          Support
        </a>
      </div>
    </aside>
  )
}
