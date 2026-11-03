import { vi, type Mock } from 'vitest'

export interface MockResponse {
  status?: number
  body?: unknown
}

/** Routes are keyed by "METHOD /api/path", e.g. "GET /api/users". */
export type MockRoutes = Record<string, MockResponse>

const NOT_FOUND: MockResponse = { status: 404, body: { detail: 'No mock route.' } }

/** Replace the global fetch with a stub that answers from the given routes. */
export function mockFetch(routes: MockRoutes): Mock {
  async function answer(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
    const route = `${init?.method ?? 'GET'} ${String(input)}`
    const { status = 200, body } = routes[route] ?? NOT_FOUND
    return new Response(body === undefined ? null : JSON.stringify(body), { status })
  }

  const fetchStub = vi.fn(answer)
  vi.stubGlobal('fetch', fetchStub)
  return fetchStub
}
