/**
 * Client-side rules only pre-empt round trips — the server stays the authority.
 * Keep these in step with whatever the backend enforces.
 */

export const MIN_USERNAME_LENGTH = 3
export const MAX_USERNAME_LENGTH = 30
export const MIN_PASSWORD_LENGTH = 8

/** Letters, digits, and . _ - between them. No spaces, no leading punctuation. */
const USERNAME_PATTERN = /^[a-zA-Z][a-zA-Z0-9._-]*$/
const PASSWORD_PATTERN = /^[a-zA-Z0-9@!_-]*$/

export function validateUsername(value: string): string | undefined {
  const username = value.trim()

  if (!username) return 'Choose a username.'
  if (username.length < MIN_USERNAME_LENGTH) {
    return `Usernames are at least ${MIN_USERNAME_LENGTH} characters.`
  }
  if (username.length > MAX_USERNAME_LENGTH) {
    return `Usernames are at most ${MAX_USERNAME_LENGTH} characters.`
  }
  if (!USERNAME_PATTERN.test(username)) {
    return 'Use letters and numbers, starting with one. . _ - are allowed inside.'
  }
  return undefined
}

export function validatePassword(value: string): string | undefined {
  if (!value) return 'Choose a password.'
  if (!PASSWORD_PATTERN.test(value)) {
    return 'Only alphanumeric characters and @ ! _ - are allowed.'
  }

  if (value.length < MIN_PASSWORD_LENGTH) {
    return `Use at least ${MIN_PASSWORD_LENGTH} characters.`
  }
  return undefined
}
