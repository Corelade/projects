import { cn } from '@/lib/cn'

/**
 * The ShiftPro mark: a rota tile with one shift assigned.
 *
 * Carries no colour of its own — it inherits text colour, so the caller sets
 * `text-brand-600` (or `text-fg` for print). Mirrors `public/logo-mark.svg`,
 * which is the same drawing for anything outside the app.
 *
 * Below 20px the 2.5 strokes and the two secondary bars merge, so `16` renders
 * a heavier optical cut rather than a scaled-down copy — the same split as
 * `logo-mark.svg` / `logo-mark-16.svg`.
 */
export interface LogoProps {
  /** 16 uses the optical cut; 20+ use the full mark. */
  size?: 16 | 20 | 24 | 32
  className?: string
}

export default function Logo({ size = 24, className }: LogoProps) {
  const shared = {
    width: size,
    height: size,
    viewBox: '0 0 32 32',
    className: cn('shrink-0', className),
    'aria-hidden': true,
    focusable: 'false' as const,
  }

  if (size === 16) {
    return (
      <svg {...shared}>
        <g
          stroke="currentColor"
          strokeWidth={3.5}
          fill="none"
          strokeLinecap="round"
        >
          <rect x="3.5" y="6" width="25" height="23" rx="5" />
          <path d="M3.5 13.5H28.5" />
          <path d="M10.5 3v5M21.5 3v5" />
        </g>
        <rect x="9" y="18.5" width="14" height="5" rx="2.5" fill="currentColor" />
      </svg>
    )
  }

  return (
    <svg {...shared}>
      <g
        stroke="currentColor"
        strokeWidth={2.5}
        fill="none"
        strokeLinecap="round"
      >
        <rect x="3.25" y="5.25" width="25.5" height="23.5" rx="5" />
        <path d="M3.25 12.5H28.75" />
        <path d="M10.5 3v4.5M21.5 3v4.5" />
      </g>
      <rect x="8" y="17" width="16" height="4" rx="2" fill="currentColor" />
      <rect x="8" y="23" width="9" height="3" rx="1.5" fill="currentColor" opacity="0.4" />
      <rect x="19" y="23" width="5" height="3" rx="1.5" fill="currentColor" opacity="0.4" />
    </svg>
  )
}
