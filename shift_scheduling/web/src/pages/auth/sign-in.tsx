import { useState } from 'react'
import { Link } from 'react-router'

import Button from '@/components/button/button'
import ErrorPanel from '@/components/error-panel/error-panel'
import Field from '@/components/field/field'
import Input from '@/components/input/input'
import { useAppDispatch } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import { useSignInMutation } from '@/store/api/auth-api'
import { signedIn } from '@/store/slices/auth-slice'
import AuthLayout from './auth-layout'
import { useAuthForm } from './use-auth-form'

const VALIDATORS = {
  // Deliberately looser than sign-up: an existing account may predate whatever
  // the current rules are, and the server decides anyway.
  username: (v: string) => (v.trim() ? undefined : 'Enter your username.'),
  password: (v: string) => (v ? undefined : 'Enter your password.'),
}

export default function SignInPage() {
  const dispatch = useAppDispatch()
  const [signIn, { isLoading }] = useSignInMutation()
  const [formError, setFormError] = useState<string | null>(null)

  const { values, errors, setValue, blur, validateAll } = useAuthForm(
    { username: '', password: '' },
    VALIDATORS,
  )

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setFormError(null)

    const valid = validateAll()
    if (!valid) return

    try {
      const { token, user } = await signIn(valid).unwrap()
      // RedirectIfSignedIn takes it from here, honouring ?from=.
      dispatch(signedIn({ token, user, expiresAt: null }))
    } catch (err) {
      // A rejected sign-in is a form error, not a field one — the server won't
      // say which half was wrong, and neither should this screen.
      setFormError(errorMessage(err, "Couldn't sign you in."))
    }
  }

  return (
    <AuthLayout
      title="Sign in"
      description="Pick up the rota where you left it."
      footer={
        <>
          No account?{' '}
          <Link to="/sign-up" className="focus-ring rounded-sm font-medium text-brand-700">
            Create one
          </Link>
        </>
      }
    >
      <form className="flex flex-col gap-4" onSubmit={submit} noValidate>
        {formError && <ErrorPanel title="Couldn't sign in" message={formError} />}

        <Field id="username" label="Username" error={errors.username} required>
          {(props) => (
            <Input
              {...props}
              autoComplete="username"
              autoCapitalize="none"
              spellCheck={false}
              autoFocus
              value={values.username}
              invalid={Boolean(errors.username)}
              disabled={isLoading}
              onChange={(e) => setValue('username', e.target.value)}
              onBlur={() => blur('username')}
            />
          )}
        </Field>

        <Field id="password" label="Password" error={errors.password} required>
          {(props) => (
            <Input
              {...props}
              type="password"
              autoComplete="current-password"
              value={values.password}
              invalid={Boolean(errors.password)}
              disabled={isLoading}
              onChange={(e) => setValue('password', e.target.value)}
              onBlur={() => blur('password')}
            />
          )}
        </Field>

        <Button type="submit" variant="primary" loading={isLoading} fullWidth>
          Sign in
        </Button>
      </form>
    </AuthLayout>
  )
}
