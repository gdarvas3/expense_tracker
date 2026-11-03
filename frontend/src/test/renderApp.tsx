import { render } from '@testing-library/react'
import type { Mock } from 'vitest'
import { MemoryRouter } from 'react-router'
import { App } from '../App'
import { CurrentUserProvider } from '../context/CurrentUserProvider'
import { mockFetch, type MockRoutes } from './fetchMock'

/** Render the whole app at a route, answering API calls from the given mock routes. */
export function renderApp(startPath: string, routes: MockRoutes): Mock {
  const fetchStub = mockFetch(routes)
  render(
    <CurrentUserProvider>
      <MemoryRouter initialEntries={[startPath]}>
        <App />
      </MemoryRouter>
    </CurrentUserProvider>,
  )
  return fetchStub
}

/** Count the calls made to one "METHOD /api/path" route. */
export function countCalls(fetchStub: Mock, route: string): number {
  return fetchStub.mock.calls.filter(isCallTo).length

  function isCallTo(call: unknown[]): boolean {
    const [input, init] = call as [RequestInfo | URL, RequestInit | undefined]
    return `${init?.method ?? 'GET'} ${String(input)}` === route
  }
}
