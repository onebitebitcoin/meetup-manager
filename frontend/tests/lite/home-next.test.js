import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { splitNextMeetups } from '@/lite/format'
import { useLiteStore } from '@/lite/store'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push, replace: vi.fn() }), useRoute: () => ({ params: {}, query: {} }) }))

const jsonResponse = (body, status = 200) => ({ ok: status < 400, status, json: () => Promise.resolve(body) })

const card = (over = {}) => ({
  id: 1, title: '거래소 탈출', starts_at: '2099-11-08T04:00:00Z', location: '석우동카페', capacity: 10,
  going_count: 0, maybe_count: 0, my_status: null, from_request: false, is_today: false, room_id: 1,
  thumb_url: null, cancelled: false, ...over,
})

describe('splitNextMeetups (서울 날짜 기준)', () => {
  it('가장 가까운 날짜의 모임을 모두 next로, 나머지를 rest로 나눈다', () => {
    const a = card({ id: 1, starts_at: '2099-11-08T04:00:00Z' }) // 서울 11/8 13:00
    const b = card({ id: 2, starts_at: '2099-11-08T06:00:00Z' }) // 서울 11/8 15:00
    const c = card({ id: 3, starts_at: '2099-11-11T11:00:00Z' })

    const { next, rest } = splitNextMeetups([a, b, c])

    expect(next.map((m) => m.id)).toEqual([1, 2])
    expect(rest.map((m) => m.id)).toEqual([3])
  })

  it('UTC로는 같은 날이어도 서울 날짜가 다르면 묶지 않는다', () => {
    const a = card({ id: 1, starts_at: '2099-11-08T14:00:00Z' }) // 서울 11/8 23:00
    const b = card({ id: 2, starts_at: '2099-11-08T15:30:00Z' }) // 서울 11/9 00:30

    expect(splitNextMeetups([a, b]).next.map((m) => m.id)).toEqual([1])
  })

  it('취소된 모임은 next 기준에서 빼고 rest에 남긴다', () => {
    const cancelled = card({ id: 1, cancelled: true })
    const later = card({ id: 2, starts_at: '2099-11-11T11:00:00Z' })

    const { next, rest } = splitNextMeetups([cancelled, later])

    expect(next.map((m) => m.id)).toEqual([2])
    expect(rest.map((m) => m.id)).toEqual([1])
  })

  it('모임이 없으면 둘 다 비어 있다', () => {
    expect(splitNextMeetups([])).toEqual({ next: [], rest: [] })
  })
})

describe('LiteHome 다음 모임 카드', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    global.fetch = vi.fn()
    push.mockReset()
  })

  it('같은 날 세션은 노란 카드 하나에, 이후 모임은 목록에 보인다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse({
      meetups: [
        card({ id: 1, title: '거래소 탈출' }),
        card({ id: 2, title: '셀프 커스터디', starts_at: '2099-11-08T06:00:00Z', my_status: 'going' }),
        card({ id: 3, title: '온라인 AI 밋업', starts_at: '2099-11-11T11:00:00Z', location: '온라인', capacity: 30 }),
      ],
      my_seminar: null, seminars: [], ready_request_count: 0, is_open: true,
    }))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    const hero = wrapper.find('.l-next')
    expect(hero.findAll('.l-next-title').map((t) => t.text())).toEqual(['거래소 탈출', '셀프 커스터디'])
    // 정원과 장소는 홈 카드에 두지 않고 자세히(모임 화면)에서 보여 준다
    expect(hero.text()).not.toContain('정원')
    expect(hero.text()).not.toContain('석우동카페')
    // 응답하지 않은 모임은 꺼진 불참 스위치, 참석한 모임은 켜진 참석 스위치로 보인다
    expect(hero.findAll('.l-pill-btn').length).toBe(0)
    const switches = hero.findAll('[role="switch"]')
    expect(switches.map((sw) => [sw.attributes('aria-checked'), sw.text()])).toEqual([['false', '불참'], ['true', '참석']])
    // 다가오는 모임 목록에도 스위치가 있다
    expect(wrapper.find('.l-mrow [role="switch"]').attributes('aria-checked')).toBe('false')
    expect(hero.findAll('.l-more').map((b) => b.text())).toEqual(['자세히', '자세히'])
    expect(wrapper.findAll('.l-mrow-title').map((t) => t.text())).toEqual(['온라인 AI 밋업'])

    // 다가오는 모임도 스위치 옆에 자세히가 있고, 줄과 자세히 모두 모임 정보 화면으로 간다
    const row = wrapper.find('.l-mrow')
    expect(row.find('.l-mrow-actions .l-more').text()).toBe('자세히')
    await row.find('.l-mrow-actions .l-more').trigger('click')
    expect(push).toHaveBeenLastCalledWith('/m/3/info')
    await row.find('.l-mrow-open').trigger('click')
    expect(push).toHaveBeenLastCalledWith('/m/3/info')
  })

  it('운영자에게는 참석 스위치를 보이지 않는다', async () => {
    useLiteStore().member = { id: 9, name: '운영', is_host: true }
    fetch.mockResolvedValue(jsonResponse({ meetups: [card()], my_seminar: null, seminars: [], ready_request_count: 0, is_open: true }))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.find('.l-next').exists()).toBe(true)
    expect(wrapper.find('[role="switch"]').exists()).toBe(false)
  })
})

describe('LiteNextCard 사진', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useLiteStore().isOpen = true
  })

  it('같은 날 모임이 여럿이면 줄마다 자기 썸네일을 보여 주고, 사진이 없는 모임은 썸네일 자리를 두지 않는다', async () => {
    const { default: LiteNextCard } = await import('@/lite/components/LiteNextCard.vue')

    const wrapper = mount(LiteNextCard, { props: { meetups: [
      card({ id: 1, thumb_url: '/media/lite/thumbs/exit.webp' }),
      card({ id: 2, title: '셀프 커스터디', thumb_url: '/media/lite/thumbs/custody.webp' }),
      card({ id: 3, title: '사진 없는 모임' }),
    ] } })

    const slots = wrapper.findAll('.l-next-slot')
    expect(slots.map((s) => s.find('img.l-next-thumb').exists() ? s.find('img.l-next-thumb').attributes('src') : null))
      .toEqual(['/media/lite/thumbs/exit.webp', '/media/lite/thumbs/custody.webp', null])
  })
})

describe('LiteNextCard 참석 스위치와 자세히', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    useLiteStore().isOpen = true
    global.fetch = vi.fn()
    push.mockReset()
  })

  it('스위치를 끄면 불참으로 바꾸고 홈에 다시 불러오라고 알린다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse({ meetup: card({ my_status: 'no' }) }))
    const { default: LiteNextCard } = await import('@/lite/components/LiteNextCard.vue')

    const wrapper = mount(LiteNextCard, { props: { meetups: [card({ id: 7, my_status: 'going' })] } })
    await wrapper.find('[role="switch"]').trigger('click')
    await flushPromises()

    const [url, init] = fetch.mock.calls[0]
    expect(url).toContain('meetups/7/rsvp/')
    expect(JSON.parse(init.body)).toEqual({ status: 'no' })
    expect(wrapper.emitted('changed')).toHaveLength(1)
    expect(useLiteStore().toast).toEqual({ message: '불참으로 바꿨어요', kind: 'no' })
  })

  it('불참 상태에서 켜면 참석으로 바꾸고, 자세히를 누르면 모임 화면으로 간다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse({ meetup: card({ my_status: 'going' }) }))
    const { default: LiteNextCard } = await import('@/lite/components/LiteNextCard.vue')

    const wrapper = mount(LiteNextCard, { props: { meetups: [card({ id: 7, my_status: 'no' })] } })
    const sw = wrapper.find('[role="switch"]')
    expect(sw.attributes('aria-checked')).toBe('false')
    expect(sw.text()).toBe('불참')
    await sw.trigger('click')
    await flushPromises()
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ status: 'going' })

    await wrapper.find('.l-more').trigger('click')
    expect(push).toHaveBeenCalledWith('/m/7/info')
  })

  it('모임마다 원형 배지에 "11/8 (일)"과 "오후 1시"를 두고 옆에 제목을 쓴다', async () => {
    const { default: LiteNextCard } = await import('@/lite/components/LiteNextCard.vue')
    // 2099-11-08T04:00Z = 서울 11월 8일 일요일 오후 1시, 06:30Z = 오후 3시 30분
    const wrapper = mount(LiteNextCard, { props: { meetups: [card(), card({ id: 2, title: '셀프 커스터디', starts_at: '2099-11-08T06:30:00Z' })] } })
    const badges = wrapper.findAll('.l-next-badge')
    expect(badges.map((b) => [b.find('b').text(), b.find('span').text()])).toEqual([['11/8 (일)', '오후 1시'], ['11/8 (일)', '오후 3시 30분']])
    expect(wrapper.findAll('.l-next-title').map((t) => t.text())).toEqual(['거래소 탈출', '셀프 커스터디'])
  })
})
