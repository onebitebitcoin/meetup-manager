import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'
import LiteChat from '@/lite/components/LiteChat.vue'
import LiteMessage from '@/lite/components/LiteMessage.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useRoute: () => ({ query: {}, params: {} }),
}))

const json = (body, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: () => Promise.resolve(body),
})
const msg = (id, kind = 'user') => ({ id, kind, body: `m${id}`, member: { id: 2, name: '민수' }, created_at: '2026-10-14T00:00:00Z' })

const mounted = []
const mountChat = () => {
  const wrapper = mount(LiteChat, { props: { roomId: 9 } })
  mounted.push(wrapper)
  return wrapper
}
const setHost = (isHost) => {
  useLiteStore().member = { id: 1, name: '운영자', is_host: isHost }
}
const MORE = 'button[aria-label="메시지 관리"]'
const callsTo = (method, suffix) =>
  fetch.mock.calls.filter(([url, opts]) => url.endsWith(suffix) && opts?.method === method)

describe('LiteMessage 운영 메뉴', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it('운영자에게만 user 메시지 메뉴 버튼이 보인다', () => {
    setHost(false)
    expect(mount(LiteMessage, { props: { message: msg(1) } }).find(MORE).exists()).toBe(false)

    setHost(true)
    expect(mount(LiteMessage, { props: { message: msg(1) } }).find(MORE).exists()).toBe(true)
  })

  it('system, guide 메시지에는 운영자여도 메뉴가 없다', () => {
    setHost(true)
    expect(mount(LiteMessage, { props: { message: msg(1, 'system') } }).find(MORE).exists()).toBe(false)
    expect(mount(LiteMessage, { props: { message: msg(2, 'guide') } }).find(MORE).exists()).toBe(false)
  })
})

describe('LiteChat 운영 기능', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    setActivePinia(createPinia())
    fetch.mockReset()
    Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'visible' })
  })
  afterEach(() => {
    mounted.splice(0).forEach((w) => w.unmount())
    vi.useRealTimers()
  })

  it('삭제는 확인 전에는 호출되지 않고, 확인하면 호출되며 목록에서 사라진다', async () => {
    setHost(true)
    fetch.mockImplementation((url, opts) => {
      if (opts?.method === 'DELETE') return Promise.resolve(json({ deleted: true }))
      return Promise.resolve(json({ messages: [msg(1), msg(2)], pinned: null }))
    })
    const wrapper = mountChat()
    await flushPromises()

    await wrapper.findAll(MORE)[0].trigger('click')
    await wrapper.findAll('.l-msg-menu button').find((b) => b.text() === '삭제').trigger('click')
    expect(wrapper.text()).toContain('삭제할까요?')
    expect(callsTo('DELETE', '/rooms/9/messages/1/')).toHaveLength(0)

    await wrapper.findAll('.l-msg-menu button').find((b) => b.text() === '삭제').trigger('click')
    await flushPromises()

    expect(callsTo('DELETE', '/rooms/9/messages/1/')).toHaveLength(1)
    expect(wrapper.text()).not.toContain('m1')
    expect(wrapper.text()).toContain('m2')
  })

  it('고정된 메시지를 삭제하면 고정 바도 사라진다', async () => {
    setHost(true)
    fetch.mockImplementation((url, opts) => {
      if (opts?.method === 'DELETE') return Promise.resolve(json({ deleted: true }))
      return Promise.resolve(json({ messages: [msg(1)], pinned: msg(1) }))
    })
    const wrapper = mountChat()
    await flushPromises()
    expect(wrapper.find('.l-pinbar').exists()).toBe(true)

    await wrapper.find(MORE).trigger('click')
    await wrapper.findAll('.l-msg-menu button').find((b) => b.text() === '삭제').trigger('click')
    await wrapper.findAll('.l-msg-menu button').find((b) => b.text() === '삭제').trigger('click')
    await flushPromises()

    expect(wrapper.find('.l-pinbar').exists()).toBe(false)
  })

  it('pinned가 있으면 고정 바가 보이고 해제 버튼은 운영자에게만 보인다', async () => {
    setHost(false)
    fetch.mockResolvedValue(json({ messages: [msg(1)], pinned: msg(1) }))
    const member = mountChat()
    await flushPromises()

    expect(member.find('.l-pinbar').text()).toContain('민수')
    expect(member.find('button[aria-label="공지 해제"]').exists()).toBe(false)
    expect(member.find(MORE).exists()).toBe(false)

    setHost(true)
    const host = mountChat()
    await flushPromises()
    expect(host.find('button[aria-label="공지 해제"]').exists()).toBe(true)
  })

  it('고정과 해제는 pinMessage를 올바른 인자로 호출한다', async () => {
    setHost(true)
    fetch.mockImplementation((url, opts) => {
      if (opts?.method === 'PUT') {
        const id = JSON.parse(opts.body).message_id
        return Promise.resolve(json({ pinned: id === null ? null : msg(id) }))
      }
      return Promise.resolve(json({ messages: [msg(1)], pinned: null }))
    })
    const wrapper = mountChat()
    await flushPromises()
    expect(wrapper.find('.l-pinbar').exists()).toBe(false)

    await wrapper.find(MORE).trigger('click')
    await wrapper.findAll('.l-msg-menu button').find((b) => b.text() === '공지로 고정').trigger('click')
    await flushPromises()

    const puts = callsTo('PUT', '/rooms/9/pin/')
    expect(JSON.parse(puts[0][1].body)).toEqual({ message_id: 1 })
    expect(wrapper.find('.l-pinbar').exists()).toBe(true)

    await wrapper.find('button[aria-label="공지 해제"]').trigger('click')
    await flushPromises()

    expect(JSON.parse(callsTo('PUT', '/rooms/9/pin/')[1][1].body)).toEqual({ message_id: null })
    expect(wrapper.find('.l-pinbar').exists()).toBe(false)
  })
})
