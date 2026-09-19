/**
 * Invite links — disabled while staff emails are placeholders. Staff create a
 * password at /portal/create-password instead. Uncomment (with the matching
 * endpoints in backend/api.py) for a real deployment where staff have working
 * emails.
 */

// import { useEffect, useRef, useState } from 'react'
//
// import Button from '@/components/button/button'
// import ErrorPanel from '@/components/error-panel/error-panel'
// import Icon from '@/components/icon/icon'
// import Input from '@/components/input/input'
// import Modal from '@/components/modal/modal'
// import Spinner from '@/components/spinner/spinner'
// import { formatDateTime } from '@/lib/dates'
// import { fullName } from '@/lib/format'
// import { errorMessage } from '@/store/api/base-api'
// import { useCreateInviteMutation } from '@/store/api/staff-api'
// import type { Staff } from '@/types'
//
// /**
//  * Issues a one-time portal link for one staff member and shows it to copy.
//  *
//  * Nothing is emailed — the manager passes the link on however they reach
//  * their staff. Each open issues a fresh link and voids the previous one, so
//  * for someone who already has a password it doubles as a password reset.
//  */
// export default function InviteDialog({
//   staff,
//   onClose,
// }: {
//   staff: Staff
//   onClose: () => void
// }) {
//   const [createInvite, { data, error, isError, isLoading }] = useCreateInviteMutation()
//   const [copied, setCopied] = useState(false)
//   const requested = useRef(false)
//
//   // Once per open; StrictMode's double effect must not burn two links.
//   useEffect(() => {
//     if (requested.current) return
//     requested.current = true
//     createInvite(staff.id)
//   }, [createInvite, staff.id])
//
//   const link = data
//     ? `${window.location.origin}${import.meta.env.BASE_URL}portal/setup?token=${encodeURIComponent(data.token)}`
//     : ''
//
//   async function copy() {
//     try {
//       await navigator.clipboard.writeText(link)
//       setCopied(true)
//     } catch {
//       // Clipboard blocked (http, permissions) — the field is selectable instead.
//     }
//   }
//
//   return (
//     <Modal
//       title={
//         staff.has_account
//           ? `Password reset link for ${fullName(staff)}`
//           : `Invite ${fullName(staff)}`
//       }
//       onClose={onClose}
//       footer={<Button onClick={onClose}>Done</Button>}
//     >
//       <div className="flex flex-col gap-4">
//         <p>
//           {staff.has_account
//             ? 'They already have a password. This link lets them set a new one.'
//             : 'Send them this link. They create a password, then sign in to the staff portal with'}{' '}
//           {!staff.has_account && <span className="font-medium text-fg">{staff.email}</span>}
//           {!staff.has_account && '.'}
//         </p>
//
//         {isError ? (
//           <ErrorPanel title="Couldn't create a link" message={errorMessage(error)} />
//         ) : isLoading || !data ? (
//           <div className="flex justify-center py-4">
//             <Spinner />
//           </div>
//         ) : (
//           <>
//             <div className="flex gap-2">
//               <Input
//                 aria-label="Invite link"
//                 value={link}
//                 readOnly
//                 onFocus={(e) => e.currentTarget.select()}
//               />
//               <Button
//                 variant="primary"
//                 iconLeft={copied ? <Icon name="check" size={16} /> : undefined}
//                 onClick={copy}
//               >
//                 {copied ? 'Copied' : 'Copy'}
//               </Button>
//             </div>
//             <p className="text-small">
//               Works once, until {formatDateTime(data.expires_at)}. Any earlier
//               link for {staff.first_name} no longer works.
//             </p>
//           </>
//         )}
//       </div>
//     </Modal>
//   )
// }

export {}
