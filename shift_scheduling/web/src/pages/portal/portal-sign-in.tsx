import { useState } from 'react'
import { Link } from 'react-router'

import Button from '@/components/button/button'
import ErrorPanel from '@/components/error-panel/error-panel'
import Field from '@/components/field/field'
import Input from '@/components/input/input'
import PasswordInput from '@/components/password-input/password-input'
import AuthLayout from '@/pages/auth/auth-layout'
import { useAuthForm } from '@/pages/auth/use-auth-form'
import { useAppDispatch } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import { usePortalSignInMutation } from '@/store/api/portal-api'
import { signedIn } from '@/store/slices/auth-slice'

const VALIDATORS = {
  email: (v: string) => (v.trim() ? undefined : 'Enter your work email.'),
  password: (v: string) => (v ? undefined : 'Enter your password.'),
}

/**
 * Staff-only sign in, with the email their manager added them under. Admins
 * have their own page (/sign-in) and reach the staff view from the admin app.
 * Like the admin sign-in, RedirectIfSignedIn owns the redirect afterwards.
 */
export default function PortalSignInPage() {
  const dispatch = useAppDispatch()
  const [signIn, { isLoading }] = usePortalSignInMutation()
  const [formError, setFormError] = useState<string | null>(null)

  const { values, errors, setValue, blur, validateAll } = useAuthForm(
    { email: '', password: '' },
    VALIDATORS,
  )

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setFormError(null)

    const valid = validateAll()
    if (!valid) return

    try {
      dispatch(
        signedIn(
          await signIn({
            email: valid.email.trim(),
            password: valid.password,
          }).unwrap(),
        ),
      )
    } catch (err) {
      setFormError(errorMessage(err, "Couldn't sign you in."))
    }
  }

  return (
    <AuthLayout
      title="Staff sign in"
      description="See your shifts and availability."
      footer={
        <>
          First time here?{' '}
          <Link
            to="/portal/create-password"
            className="focus-ring rounded-sm font-medium text-brand-700"
          >
            Create password
          </Link>
        </>
      }
    >
      <form className="flex flex-col gap-4" onSubmit={submit} noValidate>
        {formError && <ErrorPanel title="Couldn't sign in" message={formError} />}

        <Field id="email" label="Work email" error={errors.email} required>
          {(props) => (
            <Input
              {...props}
              type="email"
              autoComplete="username"
              autoCapitalize="none"
              spellCheck={false}
              autoFocus
              value={values.email}
              invalid={Boolean(errors.email)}
              disabled={isLoading}
              onChange={(e) => setValue('email', e.target.value)}
              onBlur={() => blur('email')}
            />
          )}
        </Field>

        <div className="flex flex-col gap-1">
          <Field id="password" label="Password" error={errors.password} required>
            {(props) => (
              <PasswordInput
                {...props}
                autoComplete="current-password"
                value={values.password}
                invalid={Boolean(errors.password)}
                disabled={isLoading}
                onChange={(e) => setValue('password', e.target.value)}
                onBlur={() => blur('password')}
              />
            )}
          </Field>
          <Link
            to={
              values.email.trim()
                ? `/portal/forgot-password?email=${encodeURIComponent(values.email.trim())}`
                : '/portal/forgot-password'
            }
            className="focus-ring self-end rounded-sm text-small font-medium text-brand-700"
          >
            Forgot password?
          </Link>
        </div>

        <Button type="submit" variant="primary" loading={isLoading} fullWidth>
          Sign in
        </Button>
      </form>
    </AuthLayout>
  )
}
