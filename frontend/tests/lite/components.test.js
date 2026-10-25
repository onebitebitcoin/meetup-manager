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

  it('이름이 없어도 모임을 보여 주고, 참석 스위치를 켜면 자동 닉네임으로 가입한 뒤 참석으로 신청한다', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('members/')) return Promise.resolve(jsonResponse({ token: 't1', member: { id: 1, name: '느긋한 수달', is_host: false } }, 201))
      if (url.includes('rsvp/')) return Promise.resolve(jsonResponse({ meetup: card({ my_status: 'going' }) }))
      return Promise.resolve(jsonResponse({ meetups: [card()], my_seminar: null, seminars: [], ready_request_count: 0 }))
    })

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.text()).toContain('라이트닝 노드 실습')
    expect(fetch.mock.calls.some(([url]) => url.includes('members/'))).toBe(false)
    const sw = wrapper.find('[role="switch"]')
    expect(sw.attributes('aria-checked')).toBe('false')
    expect(sw.text()).toBe('불참')
    await sw.trigger('click')
    await flushPromises()

    const calls = fetch.mock.calls.map(([url, init]) => `${init?.method || 'GET'} ${url}`)
    const created = calls.findIndex((c) => c.startsWith('POST') && c.includes('members/'))
    const joined = calls.findIndex((c) => c.startsWith('PUT') && c.includes('meetups/5/rsvp/'))
    expect(created).toBeGreaterThan(-1)
    expect(joined).toBeGreaterThan(created)
    // 홈에 머문 채 목록을 다시 불러온다
    expect(push).not.toHaveBeenCalled()
    expect(calls.filter((c) => c.includes('home/')).length).toBeGreaterThanOrEqual(2)
  })

  it('응답하지 않은 모임도 신청하기 대신 꺼진 불참 스위치로 보여 준다', async () => {
    memberStore()
    routeFetch({ 'home/': { meetups: [card()], my_seminar: null, seminars: [], ready_request_count: 0 } })

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.text()).not.toContain('신청하기')
    expect(wrapper.find('[role="switch"]').attributes('aria-checked')).toBe('false')
    expect(wrapper.find('.l-fab-btn').exists()).toBe(true)
  })

  it('참석한 모임은 켜진 참석 스위치로 보이고, 끄면 불참으로 바꾼다', async () => {
    memberStore()
    fetch.mockImplementation((url, options) => {
      if (options?.method === 'PUT') return Promise.resolve(jsonResponse({ meetup: card({ my_status: 'no' }) }))
      return Promise.resolve(jsonResponse({ meetups: [card({ my_status: 'going' })], my_seminar: null, seminars: [], ready_request_count: 0 }))
    })

    const wrapper = mount(LiteHome)
    await flushPromises()
    const sw = wrapper.find('[role="switch"]')
    expect(sw.attributes('aria-checked')).toBe('true')
    expect(sw.text()).toBe('참석')
    await sw.trigger('click')
    await flushPromises()

    const put = fetch.mock.calls.find(([, init]) => init?.method === 'PUT')
    expect(JSON.parse(put[1].body)).toEqual({ status: 'no' })
  })
})

describe('LiteRoom', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
  })

  it('이름이 없어도 이름을 묻지 않고, 신청하기를 누르면 자동 닉네임으로 가입·신청해 채팅방을 연다', async () => {
    let status = null
    fetch.mockImplementation((url, init = {}) => {
      if (url.includes('members/')) return Promise.resolve(jsonResponse({ token: 't1', member: { id: 1, name: '느긋한 수달', is_host: false } }, 201))
      if (url.includes('rsvp/')) {
        status = 'going'
        return Promise.resolve(jsonResponse({ meetup: card({ my_status: status }) }))
      }
      if (url.includes('rooms/')) return Promise.resolve(jsonResponse({ messages: [], has_more: false, pinned: null }))
      return Promise.resolve(jsonResponse({ meetup: card({ my_status: status }), removed: false, method: init.method }))
    })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    expect(wrapper.text()).not.toContain('이름을 알려주세요')
    expect(wrapper.find('input[aria-label="이름"]').exists()).toBe(false)

    await wrapper.findAll('button').find((b) => b.text() === '신청하기').trigger('click')
    await flushPromises()

    const calls = fetch.mock.calls.map(([url, init]) => `${init?.method || 'GET'} ${url}`)
    const created = calls.findIndex((c) => c.startsWith('POST') && c.includes('members/'))
    const joined = calls.findIndex((c) => c.startsWith('PUT') && c.includes('meetups/5/rsvp/'))
    expect(created).toBeGreaterThan(-1)
    expect(joined).toBeGreaterThan(created)
    expect(wrapper.find('input[aria-label="메시지"]').exists()).toBe(true)
  })

  it('미신청자에게는 메시지 대신 참석 인원과 신청하기를 보여준다', async () => {
    memberStore()
    routeFetch({
      'meetups/5/': { meetup: card() },
    })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    expect(wrapper.text()).toContain('3명 참석')
    expect(wrapper.text()).toContain('신청하기')
    expect(wrapper.text()).not.toContain('못 가요')
    expect(wrapper.find('.l-composer').exists()).toBe(false)
    expect(fetch.mock.calls.some(([url]) => url.includes('rooms/'))).toBe(false)
  })

  it('썸네일이 있으면 상단 줄에 달력 아이콘 대신 보여준다', async () => {
    memberStore()
    // 상단 요약 줄은 신청한 회원에게 보인다
    routeFetch({
      'meetups/5/': { meetup: card({ my_status: 'going', image_url: '/media/meetups/a.png' }) },
      'rooms/': { messages: [], has_more: false, pinned: null },
    })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    const img = wrapper.find('.l-bar img.l-thumb')
    expect(img.exists()).toBe(true)
    expect(img.attributes('src')).toBe('/media/meetups/a.png')
  })

  it('썸네일이 없으면 상단 줄에 이미지를 그리지 않는다', async () => {
    memberStore()
    // 상단 요약 줄은 신청한 회원에게 보인다
    routeFetch({
      'meetups/5/': { meetup: card({ my_status: 'going', image_url: null }) },
      'rooms/': { messages: [], has_more: false, pinned: null },
    })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    expect(wrapper.find('.l-bar img').exists()).toBe(false)
    expect(wrapper.find('.l-bar svg').exists()).toBe(true)
  })

  it('내보내진 회원에게는 신청, 응답 버튼을 숨기고 안내 문구만 보여준다', async () => {
    memberStore()
    routeFetch({
      'meetups/5/': { meetup: card({ my_status: 'no' }), removed: true },
    })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    expect(wrapper.text()).toContain('운영자가 내보낸 모임이에요')
    expect(wrapper.text()).not.toContain('신청하기')
    expect(wrapper.text()).not.toContain('다시 신청하기')
    expect(wrapper.find('.l-bar button').exists()).toBe(false)
  })
})

describe('LiteRoom 모임 안내와 참석 응답', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    push.mockReset()
  })

  const info = { description: '멀티시그 지갑을 직접 만들어 봅니다', audience: '비트코인을 처음 접하는 분' }

  it('미신청자에게 언제·어디서·정원·대상·내용을 풀어 쓴 안내로 보여준다', async () => {
    memberStore()
    routeFetch({ 'meetups/5/': { meetup: card(), ...info } })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    const rows = wrapper.findAll('.l-info-row').map((r) => [r.find('dt').text(), r.find('dd').text()])
    expect(rows.map(([label]) => label)).toEqual(['언제', '어디서', '정원', '대상', '내용'])
    // 2026-10-25T10:30Z는 서울 기준 10월 25일 일요일 오후 7시 30분이다
    expect(rows[0][1]).toContain('10월 25일 일요일 오후 7시 30분')
    expect(rows[2][1]).toContain('12명')
    expect(rows[2][1]).toContain('지금 3명 참석')
    expect(rows[3][1]).toBe(info.audience)
    expect(rows[4][1]).toBe(info.description)
  })

  it('대상과 내용이 비어 있으면 그 줄을 그리지 않는다', async () => {
    memberStore()
    routeFetch({ 'meetups/5/': { meetup: card(), description: '', audience: '' } })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    expect(wrapper.findAll('.l-info dt').map((d) => d.text())).toEqual(['언제', '어디서', '정원'])
  })

  it('신청한 회원은 참석·불참 두 버튼으로 바로 응답을 바꾸고, 안내는 눌러서 펼친다', async () => {
    memberStore()
    fetch.mockImplementation((url, init = {}) => {
      if (url.includes('rsvp/')) return Promise.resolve(jsonResponse({ meetup: card({ my_status: 'no' }), method: init.method }))
      if (url.includes('rooms/')) return Promise.resolve(jsonResponse({ messages: [], has_more: false, pinned: null }))
      return Promise.resolve(jsonResponse({ meetup: card({ my_status: 'going' }), ...info }))
    })

    const wrapper = mount(LiteRoom)
    await flushPromises()

    const choices = wrapper.findAll('.l-rsvp button')
    expect(choices.map((b) => b.text())).toEqual(['참석', '불참'])
    expect(choices[0].attributes('aria-pressed')).toBe('true')
    expect(wrapper.text()).not.toContain('미정')

    expect(wrapper.find('.l-info').exists()).toBe(false)
    const toggle = wrapper.findAll('.l-bar > button').find((b) => b.text().startsWith('안내'))
    await toggle.trigger('click')
    expect(wrapper.find('.l-info').text()).toContain(info.audience)

    await choices[1].trigger('click')
    await flushPromises()
    const rsvpCall = fetch.mock.calls.find(([url]) => url.includes('rsvp/'))
    expect(JSON.parse(rsvpCall[1].body)).toEqual({ status: 'no' })
    wrapper.unmount()
  })
})
