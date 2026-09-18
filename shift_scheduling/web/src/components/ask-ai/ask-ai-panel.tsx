import { useEffect, useRef, useState, type FormEvent, type KeyboardEvent } from 'react'
import Button from '@/components/button/button'
import Icon from '@/components/icon/icon'
import Spinner from '@/components/spinner/spinner'
import { cn } from '@/lib/cn'
import { useAppDispatch, useAppSelector } from '@/store'
import { setAskAiOpen } from '@/store/slices/ui-slice'
import { useChatSocket, type ChatMessage, type ChatStatus } from './use-chat-socket'

const STATUS_LABEL: Record<ChatStatus, string> = {
  idle: 'Not connected',
  connecting: 'Connecting…',
  open: 'Online',
  closed: 'Disconnected',
}

const STATUS_DOT: Record<ChatStatus, string> = {
  idle: 'bg-fg-subtle',
  connecting: 'bg-fg-subtle',
  open: 'bg-success-600',
  closed: 'bg-danger-600',
}

function Bubble({ message }: { message: ChatMessage }) {
  if (message.role === 'error') {
    return (
      <div className="flex items-start gap-2 rounded-md border border-danger-200 bg-danger-50 px-3 py-2 text-small text-danger-700">
        <Icon name="warning" size={16} className="mt-px shrink-0" />
        <p className="whitespace-pre-wrap break-words">{message.text}</p>
      </div>
    )
  }

  const mine = message.role === 'user'
  return (
    <div className={cn('flex', mine ? 'justify-end' : 'justify-start')}>
      <p
        className={cn(
          'max-w-[85%] whitespace-pre-wrap break-words rounded-lg px-3 py-2 text-body',
          mine ? 'bg-brand-600 text-fg-inverse' : 'bg-surface-subtle text-fg',
        )}
      >
        {message.text}
      </p>
    </div>
  )
}

/**
 * AskAI — a live chat with the backend AI over /chat_ws.
 *
 * Mounted once in app.tsx rather than in Layout, which remounts per page: that
 * keeps the socket and the conversation alive while the user moves around.
 *
 * Deliberately non-modal — no backdrop, no scroll lock — so the rota stays
 * usable beside it. Closed, it is `invisible`, which keeps it out of the tab
 * order the same way the sidebar's slide-over does.
 */
export default function AskAiPanel() {
  const dispatch = useAppDispatch()
  const open = useAppSelector((s) => s.ui.askAiOpen)
  const { messages, status, awaitingReply, send, reconnect } = useChatSocket(open)

  const [draft, setDraft] = useState('')
  const listRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  const close = () => dispatch(setAskAiOpen(false))
  const canSend = status === 'open' && draft.trim().length > 0

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  useEffect(() => {
    if (!open) return
    function onKeyDown(e: globalThis.KeyboardEvent) {
      if (e.key === 'Escape') dispatch(setAskAiOpen(false))
    }
    document.addEventListener('keydown', onKeyDown)
    return () => document.removeEventListener('keydown', onKeyDown)
  }, [open, dispatch])

  // Keep the newest message in view.
  useEffect(() => {
    const list = listRef.current
    if (list) list.scrollTop = list.scrollHeight
  }, [messages, awaitingReply])

  function submit(e?: FormEvent) {
    e?.preventDefault()
    if (!canSend) return
    if (send(draft)) setDraft('')
  }

  // Enter sends, Shift+Enter is a newline.
  function onInputKeyDown(e: KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === 'Enter' && !e.shiftKey && !e.nativeEvent.isComposing) {
      e.preventDefault()
      submit()
    }
  }

  return (
    <aside
      aria-label="AskAI"
      className={cn(
        'no-print fixed inset-y-0 right-0 flex w-full flex-col border-l border-border bg-surface shadow-md sm:w-100',
        'transition-[transform,visibility] duration-(--duration-slow) ease-(--ease-drawer)',
        open ? 'visible translate-x-0' : 'invisible translate-x-full',
      )}
      style={{ zIndex: 'var(--z-overlay)' }}
    >
      <header className="flex h-(--size-topbar) shrink-0 items-center justify-between gap-4 border-b border-border px-5">
        <div className="flex min-w-0 items-center gap-2.5">
          <Icon name="sparkles" size={20} className="shrink-0 text-brand-600" />
          <div className="min-w-0">
            <h2 className="text-h3 font-semibold text-fg">AskAI</h2>
            <p className="flex items-center gap-1.5 text-caption text-fg-muted">
              <span className={cn('size-1.5 rounded-full', STATUS_DOT[status])} />
              {STATUS_LABEL[status]}
            </p>
          </div>
        </div>
        <button
          type="button"
          onClick={close}
          aria-label="Close AskAI"
          className="focus-ring flex size-8 shrink-0 items-center justify-center rounded-md text-fg-muted hover:bg-surface-subtle hover:text-fg"
        >
          <Icon name="x" size={20} />
        </button>
      </header>

      {status === 'closed' && (
        <div className="flex shrink-0 items-center justify-between gap-3 border-b border-danger-200 bg-danger-50 px-5 py-2.5 text-small text-danger-700">
          <span>Connection lost.</span>
          <Button size="sm" onClick={reconnect} iconLeft={<Icon name="refresh" size={16} />}>
            Retry
          </Button>
        </div>
      )}

      <div
        ref={listRef}
        className="flex flex-1 flex-col gap-3 overflow-y-auto px-5 py-5"
        aria-live="polite"
      >
        {messages.length === 0 ? (
          <div className="m-auto flex max-w-60 flex-col items-center gap-2 text-center">
            <Icon name="sparkles" size={24} className="text-fg-subtle" />
            <p className="text-body font-medium text-fg">Ask about your rota</p>
            <p className="text-small text-fg-muted">
              Questions about staff, departments or this week's schedule.
            </p>
          </div>
        ) : (
          messages.map((m) => <Bubble key={m.id} message={m} />)
        )}

        {awaitingReply && (
          <div className="flex items-center gap-2 text-small text-fg-muted">
            <Spinner size={16} />
            AI is typing…
          </div>
        )}
      </div>

      <form
        onSubmit={submit}
        className="flex shrink-0 items-end gap-2 border-t border-border px-5 py-4"
      >
        <textarea
          ref={inputRef}
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={onInputKeyDown}
          rows={1}
          placeholder={status === 'open' ? 'Ask AI…' : STATUS_LABEL[status]}
          aria-label="Message"
          className="focus-ring max-h-32 min-h-(--size-control) flex-1 resize-none rounded-md border border-border bg-surface px-3 py-2 text-body text-fg placeholder:text-fg-subtle field-sizing-content"
        />
        <Button
          type="submit"
          variant="primary"
          disabled={!canSend}
          aria-label="Send"
        >
          Send
        </Button>
      </form>
    </aside>
  )
}
