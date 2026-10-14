import { describe, it, expect, beforeEach } from 'vitest'
import { request, liteApi } from '@/lite/api'

const jsonResponse = (body, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: () => Promise.resolve(body),
})

describe('lite api', () => {
  beforeEach(() => {
    fetch.mockReset()
  })

  it('저장된 토큰을 X-Member-Token 헤더로 보낸다', async () => {
    localStorage.setItem('lite_token', 'abc')
    fetch.mockResolvedValue(jsonResponse({ member: { id: 1 } }))

    await liteApi.me()

    const [url, options] = fetch.mock.calls[0]
    expect(url).toBe('/api/lite/me/')
    expect(options.headers['X-Member-Token']).toBe('abc')
  })

  it('토큰이 없으면 헤더를 붙이지 않는다', async () => {
    fetch.mockResolvedValue(jsonResponse({ token: 't' }, 201))

    await liteApi.createMember('지민')

    const [, options] = fetch.mock.calls[0]
    expect(options.headers['X-Member-Token']).toBeUndefined()
    expect(JSON.parse(options.body)).toEqual({ name: '지민' })
  })

  it('실패 응답의 error 문구를 그대로 던진다', async () => {
    fetch.mockResolvedValue(jsonResponse({ error: '정원이 찼어요' }, 409))

    await expect(liteApi.rsvp(3, 'going')).rejects.toMatchObject({
      message: '정원이 찼어요',
      status: 409,
    })
  })

  it('네트워크 오류는 고정 문구로 던진다', async () => {
    fetch.mockRejectedValue(new TypeError('Failed to fetch'))

    await expect(request('home/')).rejects.toThrow('네트워크 오류')
  })

  it('메시지 조회는 after 쿼리를 붙인다', async () => {
    fetch.mockResolvedValue(jsonResponse({ messages: [] }))

    await liteApi.messages(7, 12)

    expect(fetch.mock.calls[0][0]).toBe('/api/lite/rooms/7/messages/?after=12')
  })
})
