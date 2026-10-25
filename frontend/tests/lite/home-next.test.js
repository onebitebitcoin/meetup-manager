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
  image_url: null, cancelled: false, ...over,
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
      my_seminar: null, seminars: [], ready_request_count: 0,
    }))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    const hero = wrapper.find('.l-next')
    expect(hero.findAll('.l-next-title').map((t) => t.text())).toEqual(['거래소 탈출', '셀프 커스터디'])
    expect(hero.text()).toContain('정원 각 10명')
    expect(hero.findAll('.l-pill-btn').length).toBe(1)
    expect(hero.find('.l-chip.going').text()).toBe('참석')
    expect(wrapper.findAll('.l-mrow-title').map((t) => t.text())).toEqual(['온라인 AI 밋업'])

    await wrapper.find('.l-mrow').trigger('click')
    expect(push).toHaveBeenCalledWith('/lite/m/3')
  })

  it('운영자에게는 신청 버튼을 보이지 않는다', async () => {
    useLiteStore().member = { id: 9, name: '운영', is_host: true }
    fetch.mockResolvedValue(jsonResponse({ meetups: [card()], my_seminar: null, seminars: [], ready_request_count: 0 }))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.find('.l-next').exists()).toBe(true)
    expect(wrapper.find('.l-pill-btn').exists()).toBe(false)
  })
})
