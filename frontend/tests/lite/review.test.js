import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'
import LiteChat from '@/lite/components/LiteChat.vue'
import LiteHome from '@/lite/views/LiteHome.vue'
import LiteMeetupCard from '@/lite/components/LiteMeetupCard.vue'
import LiteRecover from '@/lite/views/LiteRecover.vue'
import LiteHostClaim from '@/lite/views/LiteHostClaim.vue'

const push = vi.fn()
const replace = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, replace }),
  useRoute: () => ({ query: {}, params: {} }),
}))

const json = (body, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: () => Promise.resolve(body),
})
const msg = (id, memberId = 2) => ({ id, kind: 'user', body: `m${id}`, member: { id: memberId, name: 'x' }, created_at: '2026-10-14T00:00:00Z' })

const setVisibility = (state) => {
  Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => state })
}

const mounted = []
const mountChat = () => {
  const wrapper = mount(LiteChat, { props: { roomId: 9 } })
  mounted.push(wrapper)
  return wrapper
}

describe('LiteChat', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    setActivePinia(createPinia())
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockReset()
    setVisibility('visible')
  })
  afterEach(() => {
    mounted.splice(0).forEach((w) => w.unmount())
    vi.useRealTimers()
  })

  it('첫 조회는 after 없이 호출한다', async () => {
    fetch.mockResolvedValue(json({ messages: [msg(1)] }))
    mountChat()
    await flushPromises()

    expect(fetch.mock.calls[0][0]).toBe('/api/lite/rooms/9/messages/')
  })

  it('더 오래된 메시지가 있으면 이전 메시지 보기로 앞쪽에 붙이고, 끝까지 오면 버튼을 숨긴다', async () => {
    fetch.mockImplementation((url) => {
      if (url.includes('before=101')) return Promise.resolve(json({ messages: [msg(99), msg(100)], has_more: false }))
      return Promise.resolve(json({ messages: [msg(101), msg(102)], has_more: true }))
    })
    const wrapper = mountChat()
    await flushPromises()

    const older = wrapper.find('button.l-older')
    expect(older.exists()).toBe(true)
    await older.trigger('click')
    await flushPromises()

    expect(fetch.mock.calls.some(([url]) => url === '/api/lite/rooms/9/messages/?before=101')).toBe(true)
    expect(wrapper.findAll('.l-bub').map((b) => b.text())).toEqual(['m99', 'm100', 'm101', 'm102'])
    expect(wrapper.find('button.l-older').exists()).toBe(false)
  })

  it('최신 100개 안에 모든 메시지가 있으면 이전 메시지 버튼이 없다', async () => {
    fetch.mockResolvedValue(json({ messages: [msg(1)], has_more: false }))
    const wrapper = mountChat()
    await flushPromises()

    expect(wrapper.find('button.l-older').exists()).toBe(false)
  })

  it('내가 13번을 보내도 다른 사람의 11, 12번이 누락되지 않는다', async () => {
    let phase = 'first'
    fetch.mockImplementation((url, options) => {
      if (options?.method === 'POST') return Promise.resolve(json({ message: msg(13, 1) }, 201))
      if (phase === 'first') return Promise.resolve(json({ messages: [msg(10)] }))
      return Promise.resolve(json({ messages: [msg(11), msg(12), msg(13, 1)] }))
    })
    const wrapper = mountChat()
    await flushPromises()

    phase = 'next'
    await wrapper.find('input').setValue('hi')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    const pollUrls = fetch.mock.calls.filter(([, o]) => o?.method !== 'POST').map(([u]) => u)
    expect(pollUrls.at(-1)).toContain('?after=10')
    const text = wrapper.text()
    for (const id of [10, 11, 12, 13]) expect(text).toContain(`m${id}`)
    expect(text.match(/m13/g)).toHaveLength(1)
  })

  it('탭이 숨겨지면 멈추고 다시 보이면 즉시 한 번 가져온다', async () => {
    fetch.mockResolvedValue(json({ messages: [] }))
    mountChat()
    await flushPromises()
    const before = fetch.mock.calls.length

    setVisibility('hidden')
    document.dispatchEvent(new Event('visibilitychange'))
    await vi.advanceTimersByTimeAsync(10000)
    expect(fetch.mock.calls.length).toBe(before)

    setVisibility('visible')
    document.dispatchEvent(new Event('visibilitychange'))
    await flushPromises()
    expect(fetch.mock.calls.length).toBe(before + 1)
  })

  it('401이면 폴링을 중단한다', async () => {
    fetch.mockResolvedValue(json({ error: '이름을 먼저 입력해 주세요' }, 401))
    mountChat()
    await flushPromises()
    const count = fetch.mock.calls.length

    await vi.advanceTimersByTimeAsync(10000)
    expect(fetch.mock.calls.length).toBe(count)
  })
})

describe('LiteHome 빈 상태', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
  })

  it('예정된 모임이 없으면 안내 한 줄을 보여준다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(json({ meetups: [], my_seminar: null, seminars: [], ready_request_count: 0 }))
    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.text()).toContain('예정된 모임이 없어요')
  })
})

describe('LiteMeetupCard 구조', () => {
  it('신청 버튼은 카드 이동 버튼의 형제이고 중첩되지 않는다', () => {
    setActivePinia(createPinia())
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    const meetup = { id: 5, title: 't', starts_at: '2026-10-25T10:30:00Z', location: 'l', capacity: 10, going_count: 1, my_status: null, is_today: false }
    const wrapper = mount(LiteMeetupCard, { props: { meetup } })

    expect(wrapper.find('[role="button"]').exists()).toBe(false)
    expect(wrapper.find('button button').exists()).toBe(false)
    expect(wrapper.findAll('button').length).toBe(2)
  })
})

const setLocation = (path, hash) => {
  window.location = { pathname: path, search: '', hash }
  vi.spyOn(window.history, 'replaceState').mockImplementation(() => {})
}

describe('복구 링크와 운영자 링크', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    replace.mockReset()
    localStorage.setItem.mockClear?.()
  })

  it('복구: me/가 성공한 뒤에만 새 토큰을 저장하고 fragment를 지운다', async () => {
    setLocation('/lite/r', '#newtok')
    fetch.mockResolvedValue(json({ member: { id: 1, name: '지민', is_host: false } }))
    mount(LiteRecover)
    await flushPromises()

    expect(fetch.mock.calls[0][1].headers['X-Member-Token']).toBe('newtok')
    expect(localStorage.setItem).toHaveBeenCalledWith('lite_token', 'newtok')
    expect(window.history.replaceState).toHaveBeenCalledWith(window.history.state, '', '/lite/r')
    expect(replace).toHaveBeenCalledWith('/lite')
  })

  it('복구: 실패하면 기존 토큰을 유지하고 에러 토스트를 띄운다', async () => {
    localStorage.setItem('lite_token', 'old')
    const store = useLiteStore()
    setLocation('/lite/r', '#bad')
    fetch.mockResolvedValue(json({ error: '이름을 먼저 입력해 주세요' }, 401))
    mount(LiteRecover)
    await flushPromises()

    expect(store.token).toBe('old')
    expect(localStorage.setItem).not.toHaveBeenCalledWith('lite_token', 'bad')
    expect(store.toast.kind).toBe('error')
  })

  it('운영자: 이름이 없으면 온보딩을 거친 뒤 claim을 호출한다', async () => {
    setLocation('/lite/host', '#secret')
    const store = useLiteStore()
    const wrapper = mount(LiteHostClaim)
    await flushPromises()

    expect(window.history.replaceState).toHaveBeenCalledWith(window.history.state, '', '/lite/host')
    expect(wrapper.text()).toContain('이름만 알려주세요')
    expect(fetch).not.toHaveBeenCalled()

    fetch.mockImplementation((url) => {
      if (url.endsWith('members/')) return Promise.resolve(json({ token: 't', member: { id: 1, name: '지민', is_host: false } }, 201))
      return Promise.resolve(json({ member: { id: 1, name: '지민', is_host: true } }))
    })
    await wrapper.find('input').setValue('지민')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    const claim = fetch.mock.calls.filter(([u]) => u.endsWith('host/claim/'))
    expect(claim).toHaveLength(1)
    expect(JSON.parse(claim[0][1].body)).toEqual({ key: 'secret' })
    expect(store.isHost).toBe(true)
    expect(replace).toHaveBeenCalledWith('/lite')
  })
})
