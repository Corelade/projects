/**
 * Invite links — disabled while staff emails are placeholders. Staff create a
 * password at /portal/create-password instead. Uncomment (with the matching
 * endpoints in backend/api.py) for a real deployment where staff have working
 * emails.
 */

// import { useState } from 'react'
// import { Link, useNavigate, useSearchParams } from 'react-router'
//
// import Button from '@/components/button/button'
// import ErrorPanel from '@/components/error-panel/error-panel'
// import Field from '@/components/field/field'
// import PasswordInput from '@/components/password-input/password-input'
// import Spinner from '@/components/spinner/spinner'
// import AuthLayout from '@/pages/auth/auth-layout'
// import { useAuthForm } from '@/pages/auth/use-auth-form'
// import { validatePassword } from '@/pages/auth/validate'
// import { useAppDispatch } from '@/store'
// import { errorMessage } from '@/store/api/base-api'
// import { useGetInviteQuery, useSetupAccountMutation } from '@/store/api/portal-api'
// import { signedIn } from '@/store/slices/auth-slice'
//
// const VALIDATORS = {
//   password: validatePassword,
//   confirm: (v: string, values: { password: string }) =>
//     v === values.password ? undefined : "Passwords don't match.",
// }
//
// /**
//  * Where an invite link lands: /portal/setup?token=…
//  *
//  * Deliberately not behind RedirectIfSignedIn — a manager testing a link on
//  * their own browser should still see the form, not get bounced to the rota.
//  * Finishing it replaces whatever session this browser had with the staff one.
//  */
// export default function PortalSetupPage() {
//   const dispatch = useAppDispatch()
//   const navigate = useNavigate()
//   const [searchParams] = useSearchParams()
//   const token = searchParams.get('token') ?? ''
//
//   const invite = useGetInviteQuery(token, { skip: !token })
//   const [setupAccount, { isLoading }] = useSetupAccountMutation()
//   const [formError, setFormError] = useState<string | null>(null)
//
//   const { values, errors, setValue, blur, validateAll } = useAuthForm(
//     { password: '', confirm: '' },
//     VALIDATORS,
//   )
//
//   async function submit(event: React.FormEvent) {
//     event.preventDefault()
//     setFormError(null)
//
//     const valid = validateAll()
//     if (!valid) return
//
//     try {
//       dispatch(signedIn(await setupAccount({ token, password: valid.password }).unwrap()))
//       navigate('/portal', { replace: true })
//     } catch (err) {
//       setFormError(errorMessage(err, "Couldn't set your password."))
//     }
//   }
//
//   if (!token || invite.isError) {
//     return (
//       <AuthLayout
//         title="Invite link not valid"
//         footer={
//           <Link
//             to="/portal/sign-in"
//             className="focus-ring rounded-sm font-medium text-brand-700"
//           >
//             Go to staff sign in
//           </Link>
//         }
//       >
//         <ErrorPanel
//           title="This link can't be used"
//           message={
//             invite.isError
//               ? errorMessage(invite.error)
//               : 'The link is missing its invite code. Ask your manager for a new one.'
//           }
//         />
//       </AuthLayout>
//     )
//   }
//
//   if (!invite.data) {
//     return (
//       <AuthLayout title="Checking your invite…">
//         <div className="flex justify-center py-6">
//           <Spinner size={32} />
//         </div>
//       </AuthLayout>
//     )
//   }
//
//   return (
//     <AuthLayout
//       title={`Welcome, ${invite.data.first_name}`}
//       description="Create a password to see your shifts and availability."
//     >
//       <form className="flex flex-col gap-4" onSubmit={submit} noValidate>
//         {formError && <ErrorPanel title="Couldn't save" message={formError} />}
//
//         <div className="flex flex-col gap-1.5">
//           <span className="caption">Your sign-in email</span>
//           <span className="text-body font-medium text-fg">{invite.data.email}</span>
//         </div>
//
//         {/* Lets password managers file the new password under the right account. */}
//         <input
//           type="email"
//           autoComplete="username"
//           value={invite.data.email}
//           readOnly
//           hidden
//         />
//
//         <Field
//           id="password"
//           label="Password"
//           hint="At least 8 characters: letters, numbers and @ ! _ -"
//           error={errors.password}
//           required
//         >
//           {(props) => (
//             <PasswordInput
//               {...props}
//               autoComplete="new-password"
//               autoFocus
//               value={values.password}
//               invalid={Boolean(errors.password)}
//               disabled={isLoading}
//               onChange={(e) => setValue('password', e.target.value)}
//               onBlur={() => blur('password')}
//             />
//           )}
//         </Field>
//
//         <Field id="confirm" label="Confirm password" error={errors.confirm} required>
//           {(props) => (
//             <PasswordInput
//               {...props}
//               autoComplete="new-password"
//               value={values.confirm}
//               invalid={Boolean(errors.confirm)}
//               disabled={isLoading}
//               onChange={(e) => setValue('confirm', e.target.value)}
//               onBlur={() => blur('confirm')}
//             />
//           )}
//         </Field>
//
//         <Button type="submit" variant="primary" loading={isLoading} fullWidth>
//           Create password
//         </Button>
//       </form>
//     </AuthLayout>
//   )
// }

export {}
