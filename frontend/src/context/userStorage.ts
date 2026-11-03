/**
 * Remembers the logged-in user across reloads. Storage can be unavailable (private mode,
 * blocked site data), so every access is guarded and failure just means "not remembered".
 */

import type { User } from '../types/api'

const STORAGE_KEY = 'expense-splitter.current-user'

export function loadStoredUser(): User | null {
  try {
    const stored = localStorage.getItem(STORAGE_KEY)
    return stored === null ? null : parseUser(stored)
  } catch {
    return null
  }
}

export function storeUser(user: User): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(user))
  } catch {
    // Not remembering the login is acceptable; the session still works.
  }
}

export function clearStoredUser(): void {
  try {
    localStorage.removeItem(STORAGE_KEY)
  } catch {
    // Nothing to clear if storage is unavailable.
  }
}

function parseUser(stored: string): User | null {
  const value: unknown = JSON.parse(stored)
  if (typeof value !== 'object' || value === null) {
    return null
  }
  const { id, name } = value as Record<string, unknown>
  return typeof id === 'number' && typeof name === 'string' ? { id, name } : null
}
