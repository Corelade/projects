import { useRef } from 'react'
import Button from '@/components/button/button'
import Modal from '@/components/modal/modal'

export interface ConfirmDialogProps {
  /** Names the subject: "Delete Kolade Adeyemi?" */
  title: string
  /** States the consequence. */
  description: string
  confirmLabel: string
  cancelLabel?: string
  destructive?: boolean
  loading?: boolean
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmDialog({
  title,
  description,
  confirmLabel,
  cancelLabel = 'Cancel',
  destructive = true,
  loading = false,
  onConfirm,
  onCancel,
}: ConfirmDialogProps) {
  // Default focus lands on Cancel for destructive actions.
  const cancelRef = useRef<HTMLButtonElement>(null)

  return (
    <Modal
      title={title}
      onClose={loading ? () => {} : onCancel}
      initialFocusRef={cancelRef}
      footer={
        <>
          <Button ref={cancelRef} onClick={onCancel} disabled={loading}>
            {cancelLabel}
          </Button>
          <Button
            variant={destructive ? 'danger' : 'primary'}
            onClick={onConfirm}
            loading={loading}
          >
            {confirmLabel}
          </Button>
        </>
      }
    >
      {description}
    </Modal>
  )
}
