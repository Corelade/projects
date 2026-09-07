import { Link, useNavigate } from 'react-router'

import Button from '@/components/button/button'
import Icon, { type IconName } from '@/components/icon/icon'
import Logo from '@/components/logo/logo'
import { useAppSelector } from '@/store'
import RotaPreview from './rota-preview'

/**
 * The public front door. Deliberately not `layout/` — same reasoning as
 * `auth-layout`: there's no sidebar or topbar to offer someone who hasn't
 * signed in. Everyone sees this page; only the calls to action change.
 *
 * The session is hydrated synchronously in `store/index.ts` before the first
 * render, so reading it here doesn't flash the wrong button.
 */

/** The three questions a shift manager actually opens the app to answer. */
const FEATURES: { icon: IconName; title: string; body: string }[] = [
  {
    icon: 'users',
    title: 'See who is unassigned',
    body: 'Every cell carries its own headcount. Someone who should be working and is not shows up in the grid, not in a report you have to go looking for.',
  },
  {
    icon: 'warning',
    title: 'Catch short-staffed shifts',
    body: 'A department below its minimum is flagged with a warning and the count, so a shortfall reads the same on a greyscale printout as it does on screen.',
  },
  {
    icon: 'download',
    title: 'Print it and pin it up',
    body: 'Landscape A4 with the legend on the page and no department split across a page break. Or take the PDF, where the text is still selectable.',
  },
]

const STEPS: { title: string; body: string }[] = [
  {
    title: 'Add your departments',
    body: 'Name each one and set how many staff a shift needs, at minimum and at most.',
  },
  {
    title: 'Add your staff',
    body: 'Contract hours, minimum hours, and the days or shifts each person cannot work.',
  },
  {
    title: 'Generate the week',
    body: 'A constraint solver fills every day, department and shift it can without breaking a rule.',
  },
  {
    title: 'Adjust and print',
    body: 'Click any cell to change who is on it. The rota is yours to correct — the solver only starts it.',
  },
]

export default function HomePage() {
  const session = useAppSelector((s) => s.auth.session)
  const navigate = useNavigate()

  return (
    <div className="flex min-h-dvh flex-col bg-bg">
      <header
        className="sticky top-0 border-b border-border bg-surface"
        style={{ zIndex: 'var(--z-sticky)' }}
      >
        <div className="mx-auto flex w-full max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <Link
            to="/"
            className="focus-ring flex items-center gap-2.5 rounded-sm text-h3 font-semibold text-fg"
          >
            <Logo size={24} className="text-brand-600" />
            ShiftPro
          </Link>

          <nav className="flex items-center gap-2" aria-label="Account">
            {session ? (
              <Button variant="primary" onClick={() => navigate('/schedule')}>
                Go to the rota
              </Button>
            ) : (
              <>
                {/* A real anchor: on a public page this one wants
                    middle-click, open-in-new-tab and a crawlable href. */}
                <Link
                  to="/sign-in"
                  className="focus-ring rounded-sm px-2 text-body font-medium text-brand-700 hover:text-brand-800"
                >
                  Sign in
                </Link>
                <Button variant="primary" onClick={() => navigate('/sign-up')}>
                  Create account
                </Button>
              </>
            )}
          </nav>
        </div>
      </header>

      <main className="flex-1">
        {/* --- hero ------------------------------------------------------- */}
        <section className="mx-auto w-full max-w-6xl px-4 pb-12 pt-12 sm:px-6 sm:pb-16 sm:pt-20">
          <div className="flex max-w-3xl flex-col gap-5">
            <h1 className="text-display font-semibold text-fg sm:text-hero">
              The week&rsquo;s rota, worked out for you.
            </h1>
            <p className="max-w-prose text-h3 font-normal text-fg-muted">
              ShiftPro builds a weekly rota for a shop floor split into
              departments. It assigns your staff across every day and shift
              while respecting contract hours, headcount and the days each
              person cannot work — then hands you the result to correct and
              print.
            </p>
            <div className="flex flex-wrap items-center gap-3 pt-1">
              {session ? (
                <Button variant="primary" onClick={() => navigate('/schedule')}>
                  Go to the rota
                </Button>
              ) : (
                <>
                  <Button variant="primary" onClick={() => navigate('/sign-up')}>
                    Create an account
                  </Button>
                  <Button onClick={() => navigate('/sign-in')}>Sign in</Button>
                </>
              )}
            </div>
          </div>
        </section>

        {/* --- what it looks like ----------------------------------------- */}
        <section className="mx-auto w-full max-w-6xl px-4 pb-16 sm:px-6 sm:pb-20">
          <RotaPreview />
          <p className="pt-3 text-small text-fg-muted">
            One cell is one department, one shift, one day. Colour names the
            shift; the count and the warning carry the staffing, so nothing
            depends on colour alone.
          </p>
        </section>

        {/* --- features ---------------------------------------------------- */}
        <section className="border-y border-border bg-surface">
          <div className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6 sm:py-20">
            <h2 className="text-h1 font-semibold text-fg">
              Built around three questions
            </h2>
            <p className="max-w-prose pt-2 text-body text-fg-muted">
              A manager checking next week&rsquo;s rota is looking for the same
              three things every time. The whole interface is arranged around
              answering them at a glance.
            </p>

            <ul className="grid gap-6 pt-10 sm:grid-cols-3 sm:gap-8">
              {FEATURES.map((feature) => (
                <li key={feature.title} className="flex flex-col gap-2">
                  <span className="flex size-10 items-center justify-center rounded-md bg-brand-50 text-brand-700">
                    <Icon name={feature.icon} size={20} />
                  </span>
                  <h3 className="pt-1 text-h3 font-semibold text-fg">
                    {feature.title}
                  </h3>
                  <p className="text-body text-fg-muted">{feature.body}</p>
                </li>
              ))}
            </ul>
          </div>
        </section>

        {/* --- how it works ------------------------------------------------ */}
        <section className="mx-auto w-full max-w-6xl px-4 py-16 sm:px-6 sm:py-20">
          <h2 className="text-h1 font-semibold text-fg">How it works</h2>

          <ol className="grid gap-6 pt-10 sm:grid-cols-2 sm:gap-8 lg:grid-cols-4">
            {STEPS.map((step, i) => (
              <li key={step.title} className="flex flex-col gap-2">
                <span className="tabular flex size-8 items-center justify-center rounded-full border border-border bg-surface text-small font-medium text-fg-muted">
                  {i + 1}
                </span>
                <h3 className="pt-1 text-h3 font-semibold text-fg">
                  {step.title}
                </h3>
                <p className="text-body text-fg-muted">{step.body}</p>
              </li>
            ))}
          </ol>
        </section>

        {/* --- closing ----------------------------------------------------- */}
        {!session && (
          <section className="border-t border-border bg-surface">
            <div className="mx-auto flex w-full max-w-6xl flex-col items-start gap-5 px-4 py-16 sm:px-6 sm:py-20">
              <h2 className="max-w-2xl text-h1 font-semibold text-fg">
                Stop building the rota by hand.
              </h2>
              <Button variant="primary" onClick={() => navigate('/sign-up')}>
                Create an account
              </Button>
            </div>
          </section>
        )}
      </main>

      <footer className="border-t border-border">
        <div className="mx-auto flex w-full max-w-6xl flex-wrap items-center justify-between gap-3 px-4 py-6 sm:px-6">
          <span className="flex items-center gap-2 text-small text-fg-muted">
            <Logo size={16} className="text-fg-subtle" />
            ShiftPro
          </span>
          <a
            href="mailto:support@shiftpro.test"
            className="focus-ring rounded-sm text-small text-fg-muted hover:text-fg"
          >
            Support
          </a>
        </div>
      </footer>
    </div>
  )
}
