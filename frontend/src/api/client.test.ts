import { describe, expect, it } from 'vitest'
import { mockFetch } from '../test/fetchMock'
import { ApiError, apiRequest, describeError } from './client'

describe('apiRequest', function apiRequestSuite() {
  it('sends the current user as the X-User-Id header', async function sendsTheCurrentUserAsTheXUserIdHeader() {
    const fetchStub = mockFetch({ 'GET /api/groups': { body: [] } })

    await apiRequest({ method: 'GET', path: '/groups', userId: 7 })

    const [, init] = fetchStub.mock.calls[0]
    expect(new Headers(init?.headers).get('X-User-Id')).toBe('7')
  })

  it('sends a JSON body', async function sendsAJsonBody() {
    const fetchStub = mockFetch({ 'POST /api/users': { status: 201, body: { id: 1, name: 'A' } } })

    const user = await apiRequest({ method: 'POST', path: '/users', body: { name: 'A' } })

    const [, init] = fetchStub.mock.calls[0]
    expect(init?.body).toBe('{"name":"A"}')
    expect(new Headers(init?.headers).get('Content-Type')).toBe('application/json')
    expect(user).toEqual({ id: 1, name: 'A' })
  })

  it('returns undefined for 204 No Content', async function returnsUndefinedFor204NoContent() {
    mockFetch({ 'DELETE /api/groups/1/members/2': { status: 204 } })

    const result = await apiRequest({ method: 'DELETE', path: '/groups/1/members/2', userId: 1 })

    expect(result).toBeUndefined()
  })

  it('throws an ApiError carrying the status and the backend message', async function throwsAnApiErrorCarryingTheStatusAndTheBackendMessage() {
    mockFetch({
      'GET /api/groups/1': { status: 403, body: { detail: 'You are not a member of this group.' } },
    })

    const request = apiRequest({ method: 'GET', path: '/groups/1', userId: 9 })

    await expect(request).rejects.toThrow(ApiError)
    await expect(request).rejects.toMatchObject({
      status: 403,
      message: 'You are not a member of this group.',
    })
  })

  it('joins validation issues into one readable message', async function joinsValidationIssuesIntoOneReadableMessage() {
    mockFetch({
      'POST /api/groups/1/expenses': {
        status: 400,
        body: { detail: [{ loc: ['body', 'amount'], msg: 'Input should be greater than 0' }] },
      },
    })

    const request = apiRequest({ method: 'POST', path: '/groups/1/expenses', body: {} })

    await expect(request).rejects.toMatchObject({
      status: 400,
      message: 'amount: Input should be greater than 0',
    })
  })
})

describe('describeError', function describeErrorSuite() {
  it('uses the message of an ApiError and a generic text otherwise', function usesTheMessageOfAnApiErrorAndAGenericTextOtherwise() {
    expect(describeError(new ApiError(409, 'Balance is not zero.'))).toBe('Balance is not zero.')
    expect(describeError(new TypeError('Failed to fetch'))).toBe(
      'Something went wrong. Please try again.',
    )
  })
})
