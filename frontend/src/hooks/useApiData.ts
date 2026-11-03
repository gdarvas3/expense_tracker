import { useEffect, useState } from 'react'
import { describeError } from '../api/client'

export interface ApiData<T> {
  data: T | null
  error: string | null
  isLoading: boolean
  reload(): void
}

interface LoadState<T> {
  data: T | null
  error: string | null
  isLoading: boolean
}

const LOADING: LoadState<never> = { data: null, error: null, isLoading: true }

/**
 * Load data from the API whenever `load` changes; reload() fetches it again.
 * Pass a stable `load` (module function or useCallback), or it refetches on every render.
 * Responses that arrive after `load` changed are ignored.
 */
export function useApiData<T>(load: () => Promise<T>): ApiData<T> {
  const [state, setState] = useState<LoadState<T>>(LOADING)
  const [reloadCount, setReloadCount] = useState(0)

  useEffect(
    function loadData() {
      let isStale = false

      function showData(data: T): void {
        if (!isStale) {
          setState({ data, error: null, isLoading: false })
        }
      }

      function showError(error: unknown): void {
        if (!isStale) {
          setState({ data: null, error: describeError(error), isLoading: false })
        }
      }

      load().then(showData, showError)
      return function ignoreLateResponse(): void {
        isStale = true
      }
    },
    [load, reloadCount],
  )

  function reload(): void {
    setReloadCount(incrementCount)
  }

  return { ...state, reload }
}

function incrementCount(count: number): number {
  return count + 1
}
