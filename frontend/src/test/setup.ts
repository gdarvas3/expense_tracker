import '@testing-library/jest-dom/vitest'
import { cleanup } from '@testing-library/react'
import { afterEach, vi } from 'vitest'

function resetTestEnvironment(): void {
  cleanup()
  localStorage.clear()
  vi.unstubAllGlobals()
}

afterEach(resetTestEnvironment)
