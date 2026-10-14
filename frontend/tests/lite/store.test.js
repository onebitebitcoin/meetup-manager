import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'

const jsonResponse = (body, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: () => Promise.resolve(body),
})

describe('lite store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
  })

  it('가입하면 토큰을 localStorage에 저장한다', async () => {
    fetch.mockResolvedValue(jsonResponse({ token: 'tok', member: { id: 1, name: '지민', is_host: false } }, 201))
    const store = useLiteStore()

    const ok = await store.register('지민')

    expect(ok).toBe(true)
    expect(localStorage.setItem).toHaveBeenCalledWith('lite_token', 'tok')
    expect(store.member.name).toBe('지민')
  })

  it('새 스토어는 저장된 토큰을 복구한다', () => {
    localStorage.setItem('lite_token', 'saved')

    expect(useLiteStore().token).toBe('saved')
  })

  it('init에서 401이면 토큰을 지운다', async () => {
    localStorage.setItem('lite_token', 'stale')
    fetch.mockResolvedValue(jsonResponse({ error: '이름을 먼저 입력해 주세요' }, 401))
    const store = useLiteStore()

    await store.init()

    expect(store.ready).toBe(true)
    expect(store.token).toBeNull()
    expect(localStorage.removeItem).toHaveBeenCalledWith('lite_token')
  })

  it('act는 실패 시 서버 문구로 에러 토스트를 띄운다', async () => {
    const store = useLiteStore()

    const result = await store.act(() => Promise.reject(new Error('코드가 달라요')))

    expect(result).toBeNull()
    expect(store.toast).toEqual({ message: '코드가 달라요', kind: 'error' })
  })

  it('localStorage가 던져도 가입 흐름이 깨지지 않는다', () => {
    localStorage.getItem.mockImplementationOnce(() => {
      throw new Error('blocked')
    })

    expect(useLiteStore().token).toBeNull()
  })
})
