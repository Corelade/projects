import { useState } from 'react'
import { Link, useSearchParams } from 'react-router'

import Button from '@/components/button/button'
import ErrorPanel from '@/components/error-panel/error-panel'
import Field from '@/components/field/field'
import Input from '@/components/input/input'
import PasswordInput from '@/components/password-input/password-input'
import AuthLayout from '@/pages/auth/auth-layout'
import { useAuthForm } from '@/pages/auth/use-auth-form'
import { validatePassword } from '@/pages/auth/validate'
import { useAppDispatch } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import {
  useCheckAccountMutation,
  useCreatePasswordMutation,
  useResetPasswordMutation,
} from '@/store/api/portal-api'
import { signedIn } from '@/store/slices/auth-slice'

export type PasswordMode = 'create' | 'reset'

const COPY: Record<
  PasswordMode,
  { title: string; description: string; submit: string }
> = {
  create: {
    title: 'Create password',
    description: 'First time here? Enter the work email your manager added you with.',
    submit: 'Create password',
  },
  reset: {
    title: 'Forgot password',
    description: 'Enter your work email to set a new password.',
    submit: 'Set new password',
  },
}

const LINK = 'focus-ring rounded-sm font-medium text-brand-700'

const VALIDATORS = {
  password: validatePassword,
  confirm: (v: string, values: { password: string }) =>
    v === values.password ? undefined : "Passwords don't match.",
}

/**
 * Create password and Forgot password, as one two-step page:
 *
 *   1. Email — checked against has_account on the server.
 *   2. Password — only once the email is right for this mode. An email that
 *      already has a password is sent to sign in / forgot password instead of
 *      creating; one that never had a password is sent to create instead of
 *      resetting.
 *
 * Success signs them in; RedirectIfSignedIn (fallback /portal) takes it from
 * there, same as the sign-in pages.
 */
export default function PortalPasswordPage({ mode }: { mode: PasswordMode }) {
  const dispatch = useAppDispatch()
  const [searchParams] = useSearchParams()
  const copy = COPY[mode]

  const [email, setEmail] = useState(searchParams.get('email') ?? '')
  const [emailError, setEmailError] = useState<string>()
  /** Set once the server has confirmed this email suits this mode. */
  const [confirmedEmail, setConfirmedEmail] = useState<string | null>(null)
  /** The email is real, but belongs on the other flow. */
  const [wrongFlow, setWrongFlow] = useState(false)
  const [formError, setFormError] = useState<string | null>(null)

  const [checkAccount, checkState] = useCheckAccountMutation()
  const [createPassword, createState] = useCreatePasswordMutation()
  const [resetPassword, resetState] = useResetPasswordMutation()
  const saving = createState.isLoading || resetState.isLoading

  const { values, errors, setValue, blur, validateAll } = useAuthForm(
    { password: '', confirm: '' },
    VALIDATORS,
  )

  async function submitEmail(event: React.FormEvent) {
    event.preventDefault()
    setFormError(null)
    setWrongFlow(false)

    const trimmed = email.trim()
    if (!trimmed) return setEmailError('Enter your work email.')
    setEmailError(undefined)

    try {
      const { has_account } = await checkAccount(trimmed).unwrap()
      if (has_account === (mode === 'create')) {
        setWrongFlow(true)
      } else {
        setConfirmedEmail(trimmed)
      }
    } catch (err) {
      setEmailError(errorMessage(err, "Couldn't check that email."))
    }
  }

  async function submitPassword(event: React.FormEvent) {
    event.preventDefault()
    setFormError(null)

    const valid = validateAll()
    if (!valid || !confirmedEmail) return

    const body = { email: confirmedEmail, password: valid.password }
    try {
      const session =
        mode === 'create'
          ? await createPassword(body).unwrap()
          : await resetPassword(body).unwrap()
      dispatch(signedIn(session))
    } catch (err) {
      setFormError(errorMessage(err, "Couldn't save your password."))
    }
  }

  const footer = (
    <>
      {mode === 'create' ? 'Already have a password?' : 'Remembered it?'}{' '}
      <Link to="/portal/sign-in" className={LINK}>
        Sign in
      </Link>
    </>
  )

  if (!confirmedEmail) {
    return (
      <AuthLayout title={copy.title} description={copy.description} footer={footer}>
        <form className="flex flex-col gap-4" onSubmit={submitEmail} noValidate>
          {wrongFlow && <WrongFlowPanel mode={mode} email={email.trim()} />}

          <Field id="email" label="Work email" error={emailError} required>
            {(props) => (
              <Input
                {...props}
                type="email"
                autoComplete="username"
                autoCapitalize="none"
                spellCheck={false}
                autoFocus
                value={email}
                invalid={Boolean(emailError)}
                disabled={checkState.isLoading}
                onChange={(e) => {
                  setEmail(e.target.value)
                  setWrongFlow(false)
                }}
              />
            )}
          </Field>

          <Button type="submit" variant="primary" loading={checkState.isLoading} fullWidth>
            Continue
          </Button>
        </form>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout title={copy.title} footer={footer}>
      <form className="flex flex-col gap-4" onSubmit={submitPassword} noValidate>
        {formError && <ErrorPanel title="Couldn't save" message={formError} />}

        <div className="flex items-end justify-between gap-3">
          <div className="flex min-w-0 flex-col gap-1.5">
            <span className="caption">Work email</span>
            <span className="truncate text-body font-medium text-fg">{confirmedEmail}</span>
          </div>
          <Button
            type="button"
            variant="ghost"
            size="sm"
            disabled={saving}
            onClick={() => setConfirmedEmail(null)}
          >
            Change
          </Button>
        </div>

        {/* Lets password managers file the new password under the right account. */}
        <input type="email" autoComplete="username" value={confirmedEmail} readOnly hidden />

        <Field
          id="password"
          label={mode === 'create' ? 'Password' : 'New password'}
          hint="At least 8 characters: letters, numbers and @ ! _ -"
          error={errors.password}
          required
        >
          {(props) => (
            <PasswordInput
              {...props}
              autoComplete="new-password"
              autoFocus
              value={values.password}
              invalid={Boolean(errors.password)}
              disabled={saving}
              onChange={(e) => setValue('password', e.target.value)}
              onBlur={() => blur('password')}
            />
          )}
        </Field>

        <Field id="confirm" label="Confirm password" error={errors.confirm} required>
          {(props) => (
            <PasswordInput
              {...props}
              autoComplete="new-password"
              value={values.confirm}
              invalid={Boolean(errors.confirm)}
              disabled={saving}
              onChange={(e) => setValue('confirm', e.target.value)}
              onBlur={() => blur('confirm')}
            />
          )}
        </Field>

        <Button type="submit" variant="primary" loading={saving} fullWidth>
          {copy.submit}
        </Button>
      </form>
    </AuthLayout>
  )
}

/** The email is on the roster, but this is the wrong page for it. */
function WrongFlowPanel({ mode, email }: { mode: PasswordMode; email: string }) {
  const query = `?email=${encodeURIComponent(email)}`

  return (
    <div
      role="status"
      className="flex flex-col gap-2 rounded-md border border-info-200 bg-info-50 p-4 text-body"
    >
      {mode === 'create' ? (
        <>
          <p className="font-medium text-fg">You already have a password</p>
          <p className="text-fg-muted">
            <Link to="/portal/sign-in" className={LINK}>
              Sign in
            </Link>{' '}
            with it, or{' '}
            <Link to={`/portal/forgot-password${query}`} className={LINK}>
              use Forgot password
            </Link>{' '}
            to set a new one.
          </p>
        </>
      ) : (
        <>
          <p className="font-medium text-fg">You haven't created a password yet</p>
          <p className="text-fg-muted">
            <Link to={`/portal/create-password${query}`} className={LINK}>
              Create one
            </Link>{' '}
            to get started.
          </p>
        </>
      )}
    </div>
  )
}
