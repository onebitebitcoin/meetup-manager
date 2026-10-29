import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useLiteStore } from '@/lite/store'

const push = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, replace: vi.fn() }),
  useRoute: () => ({ params: { id: '5' }, query: {} }),
}))

const jsonResponse = (body, status = 200) => ({ ok: status < 400, status, json: () => Promise.resolve(body) })

const card = (over = {}) => ({
  id: 5, title: '멀티시그 지갑 실습', starts_at: '2099-11-08T05:00:00Z', location: '강남 토즈', capacity: 15,
  going_count: 3, maybe_count: 0, my_status: null, from_request: false, is_today: false, room_id: 9,
  thumb_url: null, cancelled: false, ...over,
})

const home = (over = {}) => ({ meetups: [card()], my_seminar: null, seminars: [], ready_request_count: 0, is_open: false, ...over })

describe('오픈 전 잠금', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    global.fetch = vi.fn()
    push.mockReset()
  })

  it('오픈 전이면 방문자는 모임 목록만 보고, 참석 스위치와 문의 버튼은 보이지 않는다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse(home()))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.text()).toContain('멀티시그 지갑 실습')
    expect(wrapper.text()).toContain('오픈 준비 중이에요')
    expect(wrapper.find('[role="switch"]').exists()).toBe(false)
    expect(wrapper.find('.l-fab').exists()).toBe(false)
  })

  it('운영자는 오픈 전에도 홈에서 오픈하기를 눌러 연다', async () => {
    useLiteStore().member = { id: 1, name: '운영자', is_host: true }
    fetch.mockImplementation((url, init) => Promise.resolve(jsonResponse(
      url.includes('admin/open/') ? { is_open: JSON.parse(init.body).is_open } : home(),
    )))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()
    expect(wrapper.text()).toContain('오픈 전이에요')
    expect(wrapper.text()).not.toContain('오픈 준비 중이에요')

    const button = wrapper.findAll('.l-bar button').find((b) => b.text() === '오픈하기')
    await button.trigger('click')
    await flushPromises()

    const [url, init] = fetch.mock.calls.at(-1)
    expect(url).toContain('/api/lite/admin/open/')
    expect(init.method).toBe('PUT')
    expect(JSON.parse(init.body)).toEqual({ is_open: true })
    expect(useLiteStore().isOpen).toBe(true)
    expect(wrapper.text()).toContain('오픈 중이에요')
    expect(useLiteStore().toast).toEqual({ message: '오픈했어요', kind: 'ok' })
  })

  it('오픈 전이면 자세히 화면에서 참석하기와 공지 확인하기를 숨긴다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse({
      meetup: card({ my_status: 'going' }), description: '', audience: '', removed: false, is_open: false,
    }))
    const { default: LiteMeetupDetail } = await import('@/lite/views/LiteMeetupDetail.vue')

    const wrapper = mount(LiteMeetupDetail)
    await flushPromises()

    expect(wrapper.text()).toContain('오픈 준비 중이에요')
    expect(wrapper.text()).not.toContain('공지 확인하기')
    expect(wrapper.text()).not.toContain('참석하기')
  })
})
