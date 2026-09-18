import type { ChatMessage } from './use-chat-socket'

const OPEN_KEY = 'shiftpro.askai.open'
const MESSAGES_KEY = 'shiftpro.askai.messages'

const ROLES: readonly string[] = ['user', 'ai', 'error']

/**
 * AskAI's open flag and conversation survive a reload. Same rules as the
 * session in auth-slice: every access is wrapped, because storage throws in
 * private mode or when full, and a lost chat beats a crashed app.
 */
export function readStoredOpen(): boolean {
  try {
    return localStorage.getItem(OPEN_KEY) === 'true'
  } catch {
    return false
  }
}

export function writeStoredOpen(open: boolean) {
  try {
    localStorage.setItem(OPEN_KEY, String(open))
  } catch {
    // Storage unavailable — the panel just won't reopen after a reload.
  }
}

export function readStoredMessages(): ChatMessage[] {
  try {
    const parsed: unknown = JSON.parse(localStorage.getItem(MESSAGES_KEY) ?? '[]')
    if (!Array.isArray(parsed)) return []
    return parsed.filter(
      (m): m is ChatMessage =>
        typeof m?.id === 'string' && ROLES.includes(m?.role) && typeof m?.text === 'string',
    )
  } catch {
    // Unreadable storage, or a shape written by an older build.
    return []
  }
}

export function writeStoredMessages(messages: ChatMessage[]) {
  try {
    localStorage.setItem(MESSAGES_KEY, JSON.stringify(messages))
  } catch {
    // Storage unavailable or full — the conversation still works for this tab.
  }
}

/** On sign-out, so the next person on this browser starts with a clean chat. */
export function clearStoredChat() {
  try {
    localStorage.removeItem(OPEN_KEY)
    localStorage.removeItem(MESSAGES_KEY)
  } catch {
    // Nothing to do.
  }
}
