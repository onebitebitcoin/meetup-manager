import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { chatBackTo } from '@/lite/format'
import LiteRoom from '@/lite/views/LiteRoom.vue'
import LiteSeminar from '@/lite/views/LiteSeminar.vue'

const push = vi.fn()
const routeState = { query: {}, params: { id: '5' } }
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, replace: vi.fn() }),
  useRoute: () => routeState,
}))

const mountView = async (view, query) => {
  routeState.query = query
  fetch.mockResolvedValue({ ok: false, status: 500, json: () => Promise.resolve({ error: '서버 오류' }) })
  const wrapper = mount(view, { global: { stubs: { LiteChat: true } } })
  await flushPromises()
  return wrapper
}

describe('채팅방 뒤로 버튼', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    push.mockReset()
  })

  it.each([['LiteRoom', LiteRoom], ['LiteSeminar', LiteSeminar]])('%s: from=admin이면 /admin?tab=chat으로 간다', async (_, view) => {
    const wrapper = await mountView(view, { from: 'admin' })
    await wrapper.find('button[aria-label="뒤로"]').trigger('click')
    expect(push).toHaveBeenCalledWith('/admin?tab=chat')
  })

  it.each([['LiteRoom', LiteRoom], ['LiteSeminar', LiteSeminar]])('%s: 쿼리가 없으면 기존처럼 홈으로 간다', async (_, view) => {
    const wrapper = await mountView(view, {})
    await wrapper.find('button[aria-label="뒤로"]').trigger('click')
    expect(push).toHaveBeenCalledWith('/')
  })

  it('chatBackTo는 다른 값을 경로로 쓰지 않는다', () => {
    expect(chatBackTo({ from: 'https://evil.example' })).toBe('/')
    expect(chatBackTo({ from: '/admin' })).toBe('/')
    expect(chatBackTo({ from: ['admin'] })).toBe('/')
    expect(chatBackTo(undefined)).toBe('/')
  })
})
