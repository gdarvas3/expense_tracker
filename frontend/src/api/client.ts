/** The only module that calls fetch: adds the X-User-Id header and turns errors into ApiError. */

const API_BASE_PATH = '/api'
const NO_CONTENT_STATUS = 204
const GENERIC_ERROR_MESSAGE = 'Something went wrong. Please try again.'

export type HttpMethod = 'GET' | 'POST' | 'DELETE'

export interface ApiRequest {
  method: HttpMethod
  path: string
  userId?: number
  body?: unknown
}

export class ApiError extends Error {
  readonly status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

/**
 * Send a request to the backend and return the parsed JSON response.
 * @throws {ApiError} When the backend answers with a non-2xx status.
 */
export async function apiRequest<T>(request: ApiRequest): Promise<T> {
  const response = await fetch(API_BASE_PATH + request.path, {
    method: request.method,
    headers: buildHeaders(request),
    body: request.body === undefined ? undefined : JSON.stringify(request.body),
  })
  if (!response.ok) {
    throw new ApiError(response.status, await readErrorMessage(response))
  }
  if (response.status === NO_CONTENT_STATUS) {
    return undefined as T
  }
  return (await response.json()) as T
}

/** Turn any thrown value into a message that can be shown to the user. */
export function describeError(error: unknown): string {
  return error instanceof ApiError ? error.message : GENERIC_ERROR_MESSAGE
}

function buildHeaders(request: ApiRequest): Record<string, string> {
  const headers: Record<string, string> = {}
  if (request.body !== undefined) {
    headers['Content-Type'] = 'application/json'
  }
  if (request.userId !== undefined) {
    headers['X-User-Id'] = String(request.userId)
  }
  return headers
}

async function readErrorMessage(response: Response): Promise<string> {
  try {
    return describeErrorDetail(await response.json()) ?? GENERIC_ERROR_MESSAGE
  } catch {
    // The body was not JSON (e.g. a proxy error page).
    return GENERIC_ERROR_MESSAGE
  }
}

/** FastAPI sends either a string or a list of validation issues as "detail". */
function describeErrorDetail(payload: unknown): string | null {
  if (!isRecord(payload)) {
    return null
  }
  if (typeof payload.detail === 'string') {
    return payload.detail
  }
  if (Array.isArray(payload.detail)) {
    return payload.detail.map(describeValidationIssue).join('; ')
  }
  return null
}

function describeValidationIssue(issue: unknown): string {
  if (!isRecord(issue) || typeof issue.msg !== 'string') {
    return 'Invalid input'
  }
  const field = Array.isArray(issue.loc) ? issue.loc.at(-1) : undefined
  return field === undefined ? issue.msg : `${String(field)}: ${issue.msg}`
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null
}
