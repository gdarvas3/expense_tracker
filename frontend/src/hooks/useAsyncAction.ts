import { useState } from 'react'
import { describeError } from '../api/client'

export interface AsyncAction<Args extends unknown[]> {
  /** Run the action; resolves to true on success, false if it failed (see `error`). */
  run(...args: Args): Promise<boolean>
  error: string | null
  isRunning: boolean
}

/** Wrap an API call triggered by the user, keeping its error message for display. */
export function useAsyncAction<Args extends unknown[]>(
  action: (...args: Args) => Promise<unknown>,
): AsyncAction<Args> {
  const [error, setError] = useState<string | null>(null)
  const [isRunning, setIsRunning] = useState(false)

  async function run(...args: Args): Promise<boolean> {
    setError(null)
    setIsRunning(true)
    try {
      await action(...args)
      return true
    } catch (caught) {
      setError(describeError(caught))
      return false
    } finally {
      setIsRunning(false)
    }
  }

  return { run, error, isRunning }
}
