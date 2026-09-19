import { useCallback, useEffect, useRef, useState } from 'react'
import { useAppDispatch, useAppSelector } from '@/store'
import { ENDPOINTS } from '@/store/api/endpoints'
import { signedOut } from '@/store/slices/auth-slice'
// import { readStoredMessages, writeStoredMessages } from './chat-storage'

const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === 'true'

export type ChatRole = 'user' | 'ai' | 'error'

export interface ChatMessage {
  id: string
  role: ChatRole
  text: string
}

export type ChatStatus = 'idle' | 'connecting' | 'open' | 'closed'

let messageSeq = 0
const nextId = () => `m${++messageSeq}`

function greeting(username: string | undefined) {
  const hi = username ? `Hi ${username}!` : 'Hi!'
  return `${hi} How can I help with your staff and schedules today?`
}

/** Close code chat_endpoint sends for a missing, invalid or expired token. */
const UNAUTHORIZED = 4401

/**
 * http://host:8000 -> ws://host:8000/chat_ws?token=..., https -> wss. Browsers
 * can't set headers on a WebSocket, so the JWT rides in the query string.
 */
function socketUrl(token: string) {
  const base = new URL(import.meta.env.VITE_API_BASE_URL ?? window.location.origin)
  base.protocol = base.protocol === 'https:' ? 'wss:' : 'ws:'
  base.pathname = base.pathname.replace(/\/$/, '') + ENDPOINTS.chat.socket
  base.searchParams.set('token', token)
  return base.toString()
}

/**
 * Frames are JSON both ways: we send {"message": "..."} and expect
 * {"message": "..."} back, or {"error": "..."}. A frame that isn't JSON is
 * shown as-is rather than dropped, so a backend mid-change still reads.
 */
function parseFrame(raw: unknown): Omit<ChatMessage, 'id'> {
  if (typeof raw !== 'string') return { role: 'error', text: 'Unreadable reply.' }
  try {
    const data = JSON.parse(raw) as { message?: unknown; error?: unknown }
    if (typeof data?.message === 'string') return { role: 'ai', text: data.message }
    if (typeof data?.error === 'string') return { role: 'error', text: data.error }
  } catch {
    // Not JSON — fall through to the raw text.
  }
  return { role: 'ai', text: raw }
}

/**
 * Owns the AskAI socket. Connects the first time `enabled` is true and then
 * stays up for the life of the component, so closing the panel doesn't drop
 * the conversation. No auto-reconnect loop: a dropped socket shows a Retry.
 *
 * With VITE_USE_MOCKS=true there is no socket at all — replies are faked, the
 * same switch base-api.ts uses for HTTP.
 */
export function useChatSocket(enabled: boolean) {
  const username = useAppSelector((s) => s.auth.session?.user.username)

  const [messages, setMessages] = useState<ChatMessage[]>(() => {
    // Chat persistence is off for now, so each page load is a fresh session.
    // const stored = readStoredMessages()
    // // Continue numbering past the restored ids so React keys stay unique.
    // for (const m of stored) {
    //   const n = Number(m.id.slice(1))
    //   if (Number.isInteger(n) && n > messageSeq) messageSeq = n
    // }
    // if (stored.length > 0) return stored

    // A fresh chat opens with a greeting. It's written locally rather than
    // asked of the server: instant and free. It also goes to the model as history.
    return [{ id: nextId(), role: 'ai', text: greeting(username) }]
  })
  const [awaitingReply, setAwaitingReply] = useState(false)
  // Bumped by reconnect() to re-run the connect effect.
  const [attempt, setAttempt] = useState(0)
  // Only the socket's own events write this, tagged with the attempt they
  // belong to; "connecting" is simply "no event yet for this attempt".
  const [socketEvent, setSocketEvent] = useState<{
    attempt: number
    status: 'open' | 'closed'
  } | null>(null)

  // The token is only checked when the socket connects. Read it through a ref
  // so the keep-alive swapping in a fresh token doesn't drop a live chat.
  const token = useAppSelector((s) => s.auth.session?.token)
  const tokenRef = useRef(token)
  useEffect(() => {
    tokenRef.current = token
  }, [token])
  const dispatch = useAppDispatch()

  const socketRef = useRef<WebSocket | null>(null)
  // Latches on first open; state set during render is React's sanctioned
  // "derive from props" pattern and avoids an extra effect pass.
  const [started, setStarted] = useState(false)
  if (enabled && !started) setStarted(true)

  const status: ChatStatus = !started
    ? 'idle'
    : USE_MOCKS
      ? 'open'
      : socketEvent?.attempt === attempt
        ? socketEvent.status
        : 'connecting'

  const push = useCallback((message: Omit<ChatMessage, 'id'>) => {
    setMessages((prev) => [...prev, { id: nextId(), ...message }])
  }, [])

  // Chat persistence is off for now (see the messages initializer above).
  // useEffect(() => {
  //   writeStoredMessages(messages)
  // }, [messages])

  useEffect(() => {
    const token = tokenRef.current
    if (!started || USE_MOCKS || !token) return

    const ws = new WebSocket(socketUrl(token))
    socketRef.current = ws

    // Every handler checks it's still the current socket: StrictMode and
    // reconnect() both leave a stale socket whose late close must not win.
    ws.onopen = () => {
      if (socketRef.current === ws) setSocketEvent({ attempt, status: 'open' })
    }
    ws.onmessage = (event) => {
      if (socketRef.current !== ws) return
      push(parseFrame(event.data))
      setAwaitingReply(false)
    }
    ws.onclose = (event) => {
      if (socketRef.current !== ws) return
      // Same as a 401 over HTTP (base-api.ts): the session is dead, sign out.
      if (event.code === UNAUTHORIZED) {
        dispatch(signedOut())
        return
      }
      setSocketEvent({ attempt, status: 'closed' })
      setAwaitingReply(false)
    }

    return () => {
      if (socketRef.current === ws) socketRef.current = null
      ws.close()
    }
  }, [started, attempt, push, dispatch])

  const send = useCallback(
    (text: string) => {
      const message = text.trim()
      if (!message) return false

      if (USE_MOCKS) {
        push({ role: 'user', text: message })
        setAwaitingReply(true)
        setTimeout(() => {
          push({ role: 'ai', text: `(mock) You said: ${message}` })
          setAwaitingReply(false)
        }, 600)
        return true
      }

      const ws = socketRef.current
      if (!ws || ws.readyState !== WebSocket.OPEN) return false
      const userMessage = { role: 'user' as const, text: message }
      // setMessages won't have applied yet, so build the outgoing history here.
      ws.send(JSON.stringify({
        current_message: message,
        input_list: [...messages, userMessage],
      }))
      push(userMessage)
      setAwaitingReply(true)
      return true
    },
    [push, messages],
  )

  const reconnect = useCallback(() => setAttempt((n) => n + 1), [])

  return { messages, status, awaitingReply, send, reconnect }
}
