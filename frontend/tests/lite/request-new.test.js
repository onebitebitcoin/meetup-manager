import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useLiteStore } from '@/lite/store'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push, replace: vi.fn() }), useRoute: () => ({ params: {}, query: {} }) }))

const jsonResponse = (body, status = 200) => ({ ok: status < 400, status, json: () => Promise.resolve(body) })

describe('LiteRequestNew (이런 모임 열어주세요 입력)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    global.fetch = vi.fn()
    push.mockReset()
  })

  it('이름 없는 방문자도 바로 입력하고, 올리는 순간 자동 가입한 뒤 홈으로 돌아간다', async () => {
    fetch
      .mockResolvedValueOnce(jsonResponse({ token: 't', member: { id: 1, name: '해맑은 오리', is_host: false } }, 201))
      .mockResolvedValueOnce(jsonResponse({ request: { id: 3, title: '라이트닝 실습' } }, 201))
    const { default: LiteRequestNew } = await import('@/lite/views/LiteRequestNew.vue')

    const wrapper = mount(LiteRequestNew)
    await flushPromises()
    expect(push).not.toHaveBeenCalled()

    await wrapper.find('input.l-big-input').setValue('라이트닝 실습')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    const urls = fetch.mock.calls.map(([url]) => url)
    expect(urls[0]).toContain('members/')
    expect(urls[1]).toContain('requests/')
    expect(push).toHaveBeenCalledWith('/')
  })

  it('운영자는 올린 뒤 요청 목록으로 돌아간다', async () => {
    useLiteStore().member = { id: 9, name: '운영', is_host: true }
    fetch.mockResolvedValueOnce(jsonResponse({ request: { id: 4, title: '노드 운영' } }, 201))
    const { default: LiteRequestNew } = await import('@/lite/views/LiteRequestNew.vue')

    const wrapper = mount(LiteRequestNew)
    await wrapper.find('input.l-big-input').setValue('노드 운영')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(fetch).toHaveBeenCalledTimes(1)
    expect(push).toHaveBeenCalledWith('/requests')
  })
})
