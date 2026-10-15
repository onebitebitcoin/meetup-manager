import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'
import LiteHome from '@/lite/views/LiteHome.vue'
import LiteRoom from '@/lite/views/LiteRoom.vue'

const push = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, replace: vi.fn() }),
  useRoute: () => ({ query: {}, params: { id: '5' } }),
}))

const jsonResponse = (body, status = 200) => ({
  ok: true,
  status,
  json: () => Promise.resolve(body),
})

const card = (over = {}) => ({
  id: 5,
  title: '라이트닝 노드 실습',
  starts_at: '2026-10-25T10:30:00Z',
  location: '강남',
  capacity: 12,
  going_count: 3,
  maybe_count: 1,
  my_status: null,
  from_request: false,
  is_today: false,
  room_id: 9,
  ...over,
})

const routeFetch = (routes) => {
  fetch.mockImplementation((url) => {
    const key = Object.keys(routes).find((k) => url.includes(k))
    return Promise.resolve(jsonResponse(routes[key]))
  })
}

const memberStore = (isHost = false) => {
  const store = useLiteStore()
  store.member = { id: 1, name: '지민', is_host: isHost }
  return store
}

describe('LiteHome', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    push.mockReset()
  })

  it('이름이 없으면 온보딩을 보여준다', () => {
    const wrapper = mount(LiteHome)

    expect(wrapper.text()).toContain('이름만 알려주세요')
  })

  it('미신청 모임에는 신청하기만 보이고 못 가요는 없다', async () => {
    memberStore()
    routeFetch({ 'home/': { meetups: [card()], my_seminar: null, seminars: [], ready_request_count: 0 } })

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.text()).toContain('라이트닝 노드 실습')
    expect(wrapper.text()).toContain('신청하기')
    expect(wrapper.text()).not.toContain('못 가요')
    expect(wrapper.text()).toContain('1:1 세미나')
  })

  it('신청한 모임에는 응답 칩만 보인다', async () => {
    memberStore()
    routeFetch({ 'home/': { meetups: [card({ my_status: 'going' })], my_seminar: null, seminars: [], ready_request_count: 0 } })

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.text()).toContain('참석')
    expect(wrapper.text()).not.toContain('신청하기')
  })

  it('신청하기를 누르면 PUT rsvp 후 채팅방으로 이동한다', async () => {
    memberStore()
    fetch.mockImplementation((url, options) => {
      if (options?.method === 'PUT') return Promise.resolve(jsonResponse({ meetup: card({ my_status: 'going' }) }))
      return Promise.resolve(jsonResponse({ meetups: [card()], my_seminar: null, seminars: [], ready_request_count: 0 }))
    })

    const wrapper = mount(LiteHome)
    await flushPromises()
    await wrapper.findAll('button').find((b) => b.text() === '신청하기').trigger('click')
    await flushPromises()

    expect(push).toHaveBeenCalledWith('/lite/m/5')
  })
})

describe('LiteRoom', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
  })

  it('미신청자에게는 메시지 대신 참석 인원과 신청하기를 보여준다', async () => {
    memberStore()
    routeFetch({
      'meetups/5/': { meetup: card(), checkin_code: null, checked_in: false, checked_in_count: 0 },
    })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    expect(wrapper.text()).toContain('3명 참석')
    expect(wrapper.text()).toContain('신청하기')
    expect(wrapper.text()).not.toContain('못 가요')
    expect(wrapper.find('.l-composer').exists()).toBe(false)
    expect(fetch.mock.calls.some(([url]) => url.includes('rooms/'))).toBe(false)
  })

  it('내보내진 회원에게는 신청, 응답 버튼을 숨기고 안내 문구만 보여준다', async () => {
    memberStore()
    routeFetch({
      'meetups/5/': { meetup: card({ my_status: 'no' }), checkin_code: null, checked_in: false, checked_in_count: 0, removed: true },
    })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    expect(wrapper.text()).toContain('운영자가 내보낸 모임이에요')
    expect(wrapper.text()).not.toContain('신청하기')
    expect(wrapper.text()).not.toContain('다시 신청하기')
    expect(wrapper.find('.l-bar button').exists()).toBe(false)
  })
})
