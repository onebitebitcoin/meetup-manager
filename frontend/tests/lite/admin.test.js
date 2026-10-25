import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'
import { liteApi } from '@/lite/api'
import LiteAdmin from '@/lite/views/LiteAdmin.vue'
import LiteAdminMeetup from '@/lite/views/LiteAdminMeetup.vue'
import LiteMeetupCard from '@/lite/components/LiteMeetupCard.vue'

const push = vi.fn()
const replace = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, replace }),
  useRoute: () => ({ query: {}, params: { id: '5' } }),
}))

const jsonResponse = (body) => ({ ok: true, status: 200, json: () => Promise.resolve(body) })

const card = (over = {}) => ({
  id: 5,
  title: '라이트닝 노드 실습',
  starts_at: '2026-10-25T10:30:00Z',
  location: '강남',
  capacity: 12,
  going_count: 3,
  maybe_count: 1,
  my_status: null,
  is_today: false,
  cancelled: false,
  room_id: 9,
  ...over,
})

const routeFetch = (routes) => {
  fetch.mockImplementation((url) => {
    const key = Object.keys(routes).find((k) => url.includes(k))
    return Promise.resolve(jsonResponse(routes[key]))
  })
}

const asMember = (isHost) => {
  const store = useLiteStore()
  store.member = { id: 1, name: '운영', is_host: isHost }
}

const detail = () => ({
  meetup: card(),
  description: '',
  image_url: null,
  attendees: [
    { member: { id: 2, name: '지민' }, status: 'going', removed: false },
    { member: { id: 3, name: '수아' }, status: 'no', removed: true },
  ],
})

describe('LiteAdmin', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    push.mockReset()
    replace.mockReset()
  })

  it('모임 행과 취소됨 칩을 보여준다', async () => {
    asMember(true)
    routeFetch({ 'admin/meetups/': { meetups: [card(), card({ id: 6, title: '취소된 모임', cancelled: true })] } })
    const wrapper = mount(LiteAdmin)
    await flushPromises()

    expect(wrapper.findAll('.l-row-btn')).toHaveLength(2)
    expect(wrapper.text()).toContain('라이트닝 노드 실습')
    expect(wrapper.text()).toContain('3/12')
    expect(wrapper.text()).toContain('취소됨')
  })

  it('비운영자는 홈으로 보낸다', async () => {
    asMember(false)
    mount(LiteAdmin)
    await flushPromises()

    expect(replace).toHaveBeenCalledWith('/lite')
    expect(fetch).not.toHaveBeenCalled()
  })
})

describe('LiteAdminMeetup', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    push.mockReset()
    replace.mockReset()
  })

  it('삭제 확인이 펼쳐지기 전에는 API를 호출하지 않는다', async () => {
    asMember(true)
    routeFetch({ 'admin/meetups/5/': detail() })
    const wrapper = mount(LiteAdminMeetup)
    await flushPromises()
    fetch.mockClear()

    await wrapper.findAll('button').find((b) => b.text() === '삭제').trigger('click')

    expect(wrapper.text()).toContain('삭제할까요?')
    expect(fetch).not.toHaveBeenCalled()

    await wrapper.findAll('button').find((b) => b.text() === '삭제').trigger('click')
    await flushPromises()

    expect(fetch).toHaveBeenCalledTimes(1)
    expect(fetch.mock.calls[0][1].method).toBe('DELETE')
    expect(push).toHaveBeenCalledWith('/lite/admin')
  })

  it('내보내기는 확인 후에만 실행하고 내보낸 회원에는 버튼이 없다', async () => {
    asMember(true)
    routeFetch({ 'admin/meetups/5/': detail() })
    const wrapper = mount(LiteAdminMeetup)
    await flushPromises()
    fetch.mockClear()

    expect(wrapper.text()).toContain('내보냄')
    const kick = () => wrapper.findAll('.l-person button').find((b) => b.text() === '내보내기')
    await kick().trigger('click')

    expect(wrapper.text()).toContain('내보낼까요?')
    expect(fetch).not.toHaveBeenCalled()

    await kick().trigger('click')
    await flushPromises()

    expect(fetch.mock.calls[0][0]).toContain('admin/meetups/5/members/2/')
  })
})

describe('LiteAdminMeetup 폼 유지와 부분 저장', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    push.mockReset()
    replace.mockReset()
  })

  const titleInput = (wrapper) => wrapper.find('input[aria-label="모임 이름"]')
  const button = (wrapper, label) => wrapper.findAll('button').find((b) => b.text() === label)

  it('제목을 고친 상태에서 내보내기를 해도 입력한 제목이 유지된다', async () => {
    asMember(true)
    routeFetch({ 'admin/meetups/5/': detail() })
    const wrapper = mount(LiteAdminMeetup)
    await flushPromises()

    await titleInput(wrapper).setValue('고치는 중인 제목')
    await wrapper.findAll('.l-person button').find((b) => b.text() === '내보내기').trigger('click')
    await wrapper.findAll('.l-person button').find((b) => b.text() === '내보내기').trigger('click')
    await flushPromises()

    expect(fetch.mock.calls.at(-1)[1].method).toBe('DELETE')
    expect(titleInput(wrapper).element.value).toBe('고치는 중인 제목')
  })

  it('제목만 바꾸면 PATCH 본문에 starts_at이 없다', async () => {
    asMember(true)
    routeFetch({ 'admin/meetups/5/': detail() })
    const wrapper = mount(LiteAdminMeetup)
    await flushPromises()
    fetch.mockClear()

    await titleInput(wrapper).setValue('새 제목')
    await button(wrapper, '저장').trigger('click')
    await flushPromises()

    const body = JSON.parse(fetch.mock.calls[0][1].body)
    expect(fetch.mock.calls[0][1].method).toBe('PATCH')
    expect(body).toEqual({ title: '새 제목' })
  })

  it('날짜를 바꾸면 starts_at을 보낸다', async () => {
    asMember(true)
    routeFetch({ 'admin/meetups/5/': detail() })
    const wrapper = mount(LiteAdminMeetup)
    await flushPromises()
    fetch.mockClear()

    await wrapper.find('input[aria-label="날짜"]').setValue('2026-11-01')
    await button(wrapper, '저장').trigger('click')
    await flushPromises()

    const body = JSON.parse(fetch.mock.calls[0][1].body)
    expect(Object.keys(body)).toEqual(['starts_at'])
  })

  it('바뀐 내용이 없으면 요청하지 않고 안내한다', async () => {
    asMember(true)
    routeFetch({ 'admin/meetups/5/': detail() })
    const wrapper = mount(LiteAdminMeetup)
    await flushPromises()
    fetch.mockClear()

    await button(wrapper, '저장').trigger('click')
    await flushPromises()

    expect(fetch).not.toHaveBeenCalled()
    expect(useLiteStore().toast.message).toBe('바뀐 내용이 없어요')
  })

  it('참석 인원은 going 상태이고 내보내지 않은 회원만 정원과 함께 센다', async () => {
    asMember(true)
    routeFetch({ 'admin/meetups/5/': detail() })
    const wrapper = mount(LiteAdminMeetup)
    await flushPromises()

    expect(wrapper.find('.l-section h3').text()).toBe('참석 1/12명')
  })
})

describe('관리 api 함수', () => {
  beforeEach(() => {
    fetch.mockReset()
    fetch.mockResolvedValue(jsonResponse({}))
  })

  it.each([
    ['adminMeetups', ['past'], 'admin/meetups/?scope=past', 'GET'],
    ['adminMeetup', [5], 'admin/meetups/5/', 'GET'],
    ['updateMeetup', [5, { title: 'a' }], 'admin/meetups/5/', 'PATCH'],
    ['deleteMeetup', [5], 'admin/meetups/5/', 'DELETE'],
    ['cancelMeetup', [5, true], 'admin/meetups/5/cancel/', 'POST'],
    ['removeAttendee', [5, 2], 'admin/meetups/5/members/2/', 'DELETE'],
    ['deleteMessage', [9, 7], 'rooms/9/messages/7/', 'DELETE'],
    ['pinMessage', [9, null], 'rooms/9/pin/', 'PUT'],
  ])('%s', async (name, args, path, method) => {
    await liteApi[name](...args)

    expect(fetch.mock.calls[0][0]).toBe(`/api/lite/${path}`)
    expect(fetch.mock.calls[0][1].method).toBe(method)
  })
})

describe('LiteMeetupCard 취소 표시', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    asMember(false)
  })

  it('취소된 모임은 칩을 보이고 참석 신청 줄을 숨긴다', () => {
    const wrapper = mount(LiteMeetupCard, { props: { meetup: card({ cancelled: true }) } })

    expect(wrapper.text()).toContain('취소됨')
    expect(wrapper.findComponent({ name: 'LiteJoinRow' }).exists()).toBe(false)
  })

  it('취소되지 않았으면 참석 신청 줄이 보인다', () => {
    const wrapper = mount(LiteMeetupCard, { props: { meetup: card() } })

    expect(wrapper.text()).not.toContain('취소됨')
    expect(wrapper.findComponent({ name: 'LiteJoinRow' }).exists()).toBe(true)
  })
})
