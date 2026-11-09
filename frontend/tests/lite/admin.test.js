import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'
import { liteApi } from '@/lite/api'
import LiteAdmin from '@/lite/views/LiteAdmin.vue'
import LiteAdminMeetup from '@/lite/views/LiteAdminMeetup.vue'
import LiteAdminSettings from '@/lite/views/LiteAdminSettings.vue'
import LiteMeetupCard from '@/lite/components/LiteMeetupCard.vue'

const push = vi.fn()
const routeQuery = {}
const replace = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, replace }),
  useRoute: () => ({ query: routeQuery, params: { id: '5' } }),
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
    { member: { id: 2, name: '지민' }, status: 'going' },
    { member: { id: 3, name: '수아' }, status: 'no' },
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

  it('비운영자에게는 비밀번호 폼을 보여 주고 목록을 부르지 않는다', async () => {
    asMember(false)
    const wrapper = mount(LiteAdmin)
    await flushPromises()

    const input = wrapper.find('input[type="password"]')
    expect(input.exists()).toBe(true)
    expect(input.attributes('autocomplete')).toBe('current-password')
    expect(wrapper.findAll('.l-row-btn')).toHaveLength(0)
    expect(replace).not.toHaveBeenCalled()
    expect(fetch).not.toHaveBeenCalled()
  })

  it('로그인에 성공하면 같은 화면에서 목록을 불러온다', async () => {
    asMember(false)
    routeFetch({
      'admin/login/': { member: { id: 1, name: '운영', is_host: true } },
      'admin/meetups/': { meetups: [card()] },
    })
    const wrapper = mount(LiteAdmin)
    await flushPromises()

    await wrapper.find('input[type="password"]').setValue('hanip')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    const login = fetch.mock.calls.find(([url]) => url.includes('admin/login/'))
    expect(JSON.parse(login[1].body)).toEqual({ password: 'hanip' })
    expect(wrapper.find('input[type="password"]').exists()).toBe(false)
    expect(wrapper.findAll('.l-row-btn')).toHaveLength(1)
  })

  it('비밀번호가 틀리면 폼을 유지하고 오류 메시지를 띄운다', async () => {
    asMember(false)
    fetch.mockResolvedValue({ ok: false, status: 403, json: () => Promise.resolve({ error: '비밀번호가 맞지 않아요' }) })
    const wrapper = mount(LiteAdmin)
    await flushPromises()

    await wrapper.find('input[type="password"]').setValue('x')
    await wrapper.find('form').trigger('submit')
    await flushPromises()

    expect(wrapper.find('input[type="password"]').exists()).toBe(true)
    expect(useLiteStore().toast).toEqual({ message: '비밀번호가 맞지 않아요', kind: 'error' })
  })
})

const chatRooms = () => ({
  rooms: [
    { room_id: 1, kind: 'meetup', title: '독서 모임', meetup_id: 5, cancelled: false, unread_count: 3, last_message: { body: '안녕하세요', created_at: '2026-10-25T10:30:00Z' } },
    { room_id: 2, kind: 'seminar', title: '1:1 · 지민', seminar_id: 7, cancelled: false, unread_count: 0, last_message: { body: '', created_at: '2026-10-25T09:00:00Z' } },
    { room_id: 3, kind: 'meetup', title: '취소된 모임', meetup_id: 6, cancelled: true, unread_count: 0, last_message: null },
  ],
})

describe('LiteAdmin 채팅 탭', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    push.mockReset()
    replace.mockReset()
    delete routeQuery.tab
  })

  const openChat = async () => {
    asMember(true)
    routeFetch({ 'admin/rooms/': chatRooms(), 'admin/meetups/': { meetups: [card()] } })
    const wrapper = mount(LiteAdmin)
    await flushPromises()
    await wrapper.find('input[name="tab"][value="chat"]').setValue()
    await flushPromises()
    return wrapper
  }

  it('채팅 탭으로 바꾸면 쿼리를 남기고 방 목록을 보여 준다', async () => {
    const wrapper = await openChat()

    expect(replace).toHaveBeenCalledWith({ query: { tab: 'chat' } })
    const rows = wrapper.findAll('.l-row-btn')
    expect(rows).toHaveLength(3)
    expect(rows[0].text()).toContain('독서 모임')
    expect(rows[0].text()).toContain('안녕하세요')
    expect(rows[0].find('.l-badge').text()).toBe('3')
    expect(rows[1].text()).toContain('세미나')
    expect(rows[1].text()).toContain('첨부 파일')
    expect(rows[2].text()).toContain('취소됨')
    expect(rows[2].text()).toContain('메시지가 없어요')
  })

  it('모임 방은 /m/:id, 세미나 방은 /seminar/:id로 이동한다', async () => {
    const wrapper = await openChat()
    const rows = wrapper.findAll('.l-row-btn')

    await rows[0].trigger('click')
    await rows[1].trigger('click')

    expect(push).toHaveBeenNthCalledWith(1, '/m/5?from=admin')
    expect(push).toHaveBeenNthCalledWith(2, '/seminar/7?from=admin')
  })

  it('?tab=chat이면 처음부터 채팅 탭이고 모임 목록은 부르지 않는다', async () => {
    routeQuery.tab = 'chat'
    asMember(true)
    routeFetch({ 'admin/rooms/': chatRooms() })
    const wrapper = mount(LiteAdmin)
    await flushPromises()

    expect(wrapper.findAll('.l-row-btn')).toHaveLength(3)
    expect(fetch.mock.calls.some(([url]) => url.includes('admin/meetups/'))).toBe(false)
  })

  it('방이 없으면 빈 상태를 보여 준다', async () => {
    routeQuery.tab = 'chat'
    asMember(true)
    routeFetch({ 'admin/rooms/': { rooms: [] } })
    const wrapper = mount(LiteAdmin)
    await flushPromises()

    expect(wrapper.text()).toContain('채팅방이 없어요')
  })

  it('불러오기에 실패하면 에러를 보여 준다', async () => {
    routeQuery.tab = 'chat'
    asMember(true)
    fetch.mockResolvedValue({ ok: false, status: 500, json: () => Promise.resolve({ error: '서버 오류' }) })
    const wrapper = mount(LiteAdmin)
    await flushPromises()

    expect(wrapper.text()).toContain('서버 오류')
    expect(wrapper.findAll('.l-row-btn')).toHaveLength(0)
  })
})

describe('LiteAdminSettings', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    push.mockReset()
    replace.mockReset()
  })

  const settings = () => ({
    vote_threshold: 5, seminar_guide_1: 'a', seminar_guide_2: 'b', seminar_guide_3: 'c', seminar_guide_4: 'd', join_guide: 'e',
  })

  it('비운영자는 /admin으로 보낸다', async () => {
    asMember(false)
    mount(LiteAdminSettings)
    await flushPromises()

    expect(replace).toHaveBeenCalledWith('/admin')
    expect(fetch).not.toHaveBeenCalled()
  })

  it('불러온 값을 채우고 저장 버튼 하나로 PATCH한다', async () => {
    asMember(true)
    routeFetch({ 'admin/settings/': settings() })
    const wrapper = mount(LiteAdminSettings)
    await flushPromises()

    expect(wrapper.findAll('textarea')).toHaveLength(5)
    expect(wrapper.find('input[type="number"]').element.value).toBe('5')
    await wrapper.findAll('textarea')[4].setValue('환영해요')
    await wrapper.findAll('form')[0].trigger('submit')
    await flushPromises()

    const patch = fetch.mock.calls.find(([, init]) => init.method === 'PATCH')
    expect(JSON.parse(patch[1].body)).toMatchObject({ vote_threshold: 5, join_guide: '환영해요' })
    expect(useLiteStore().toast.message).toBe('저장했어요')
  })

  it('불러오기에 실패하면 에러를 보이고 폼을 채우지 않는다', async () => {
    asMember(true)
    fetch.mockResolvedValue({ ok: false, status: 500, json: () => Promise.resolve({ error: '서버 오류' }) })
    const wrapper = mount(LiteAdminSettings)
    await flushPromises()

    expect(wrapper.text()).toContain('서버 오류')
    expect(wrapper.findAll('textarea')).toHaveLength(0)
  })

  it('비밀번호 변경 성공 시 입력을 비운다', async () => {
    asMember(true)
    routeFetch({ 'admin/settings/': settings(), 'admin/password/': { changed: true } })
    const wrapper = mount(LiteAdminSettings)
    await flushPromises()

    const [current, next] = wrapper.findAll('input[type="password"]')
    expect(current.attributes('autocomplete')).toBe('current-password')
    expect(next.attributes('autocomplete')).toBe('new-password')
    await current.setValue('hanip')
    await next.setValue('new-password-1')
    await wrapper.findAll('form')[1].trigger('submit')
    await flushPromises()

    const put = fetch.mock.calls.find(([, init]) => init.method === 'PUT')
    expect(JSON.parse(put[1].body)).toEqual({ current_password: 'hanip', new_password: 'new-password-1' })
    expect(next.element.value).toBe('')
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
    expect(push).toHaveBeenCalledWith('/admin')
  })

  it('내보내기는 확인 후에만 실행한다', async () => {
    asMember(true)
    routeFetch({ 'admin/meetups/5/': detail() })
    const wrapper = mount(LiteAdminMeetup)
    await flushPromises()
    fetch.mockClear()

    expect(wrapper.text()).not.toContain('내보냄')
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
