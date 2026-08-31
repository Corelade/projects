import { useState } from 'react'
import { Link } from 'react-router'

import Button from '@/components/button/button'
import ErrorPanel from '@/components/error-panel/error-panel'
import Field from '@/components/field/field'
import Input from '@/components/input/input'
import { useAppDispatch } from '@/store'
import { errorMessage } from '@/store/api/base-api'
import { useSignUpMutation } from '@/store/api/auth-api'
import { signedIn } from '@/store/slices/auth-slice'
import AuthLayout from './auth-layout'
import { useAuthForm } from './use-auth-form'
import {
  MIN_PASSWORD_LENGTH,
  MIN_USERNAME_LENGTH,
  validatePassword,
  validateUsername,
} from './validate'

const VALIDATORS = {
  username: validateUsername,
  password: validatePassword,
  confirm: (value: string, values: { password: string }) =>
    value === values.password ? undefined : 'Both passwords must match.',
}

export default function SignUpPage() {
  const dispatch = useAppDispatch()
  const [signUp, { isLoading }] = useSignUpMutation()
  const [formError, setFormError] = useState<string | null>(null)

  const { values, errors, setValue, blur, validateAll, setFieldError } =
    useAuthForm({ username: '', password: '', confirm: '' }, VALIDATORS)

  async function submit(event: React.FormEvent) {
    event.preventDefault()
    setFormError(null)

    const valid = validateAll()
    if (!valid) return

    try {
      const { token, user } = await signUp({
        username: valid.username.trim(),
        password: valid.password,
      }).unwrap()
      // RedirectIfSignedIn takes it from here.
      dispatch(signedIn({ token, user, expiresAt: null }))
    } catch (err) {
      const message = errorMessage(err, "Couldn't create your account.")
      // A taken username is a fact about one field, so it belongs on that field.
      if ((err as { status?: number })?.status === 409) {
        setFieldError('username', message)
      } else {
        setFormError(message)
      }
    }
  }

  return (
    <AuthLayout
      title="Create an account"
      description="No email needed — pick a username and you're in."
      footer={
        <>
          Already have one?{' '}
          <Link to="/sign-in" className="focus-ring rounded-sm font-medium text-brand-700">
            Sign in
          </Link>
        </>
      }
    >
      <form className="flex flex-col gap-4" onSubmit={submit} noValidate>
        {formError && (
          <ErrorPanel title="Couldn't create account" message={formError} />
        )}

        <Field
          id="username"
          label="Username"
          error={errors.username}
          hint={`At least ${MIN_USERNAME_LENGTH} characters. Letters, numbers, and . _ -`}
          required
        >
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

        <Field
          id="password"
          label="Password"
          error={errors.password}
          hint={`At least ${MIN_PASSWORD_LENGTH} characters.`}
          required
        >
          {(props) => (
            <Input
              {...props}
              type="password"
              autoComplete="new-password"
              value={values.password}
              invalid={Boolean(errors.password)}
              disabled={isLoading}
              onChange={(e) => setValue('password', e.target.value)}
              onBlur={() => blur('password')}
            />
          )}
        </Field>

        <Field
          id="confirm"
          label="Confirm password"
          error={errors.confirm}
          required
        >
          {(props) => (
            <Input
              {...props}
              type="password"
              autoComplete="new-password"
              value={values.confirm}
              invalid={Boolean(errors.confirm)}
              disabled={isLoading}
              onChange={(e) => setValue('confirm', e.target.value)}
              onBlur={() => blur('confirm')}
            />
          )}
        </Field>

        <Button type="submit" variant="primary" loading={isLoading} fullWidth>
          Create account
        </Button>
      </form>
    </AuthLayout>
  )
}
