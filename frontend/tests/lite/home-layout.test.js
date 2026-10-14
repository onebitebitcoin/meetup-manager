import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import dayjs from 'dayjs'
import { daysUntilLabel } from '@/lite/format'
import { useLiteStore } from '@/lite/store'

const push = vi.fn()
vi.mock('vue-router', () => ({ useRouter: () => ({ push, replace: vi.fn() }), useRoute: () => ({ params: {}, query: {} }) }))

const jsonResponse = (body, status = 200) => ({ ok: status < 400, status, json: () => Promise.resolve(body) })

describe('daysUntilLabel (서울 날짜 기준)', () => {
  const now = dayjs('2026-10-14T03:00:00Z') // 서울 10/14 12:00

  it('오늘, 내일, N일 후를 구분한다', () => {
    expect(daysUntilLabel('2026-10-14T14:30:00Z', now)).toBe('오늘') // 서울 10/14 23:30
    expect(daysUntilLabel('2026-10-14T15:30:00Z', now)).toBe('내일') // 서울 10/15 00:30
    expect(daysUntilLabel('2026-10-17T11:00:00Z', now)).toBe('3일 후')
  })

  it('지난 모임은 빈 문자열을 돌려준다', () => {
    expect(daysUntilLabel('2026-10-12T03:00:00Z', now)).toBe('')
  })
})

describe('LiteHome 레이아웃', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    global.fetch = vi.fn()
    push.mockReset()
  })

  const card = (over = {}) => ({
    id: 5, title: '거래소 탈출', starts_at: '2099-10-25T04:00:00Z', location: '석우동카페', capacity: 10,
    going_count: 6, maybe_count: 0, my_status: null, from_request: false, is_today: false, room_id: 9,
    image_url: '/media/meetups/a.png', ...over,
  })

  it('제목은 한입 모임이고, 하단 탭 없이 1:1 세미나 아래에 요청 항목이 있다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse({ meetups: [card()], my_seminar: null, seminars: [], ready_request_count: 0 }))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.find('.l-top h2').text()).toBe('한입 모임')
    expect(wrapper.find('nav').exists()).toBe(false)
    const titles = wrapper.findAll('.l-title').map((t) => t.text())
    expect(titles.indexOf('1:1 세미나')).toBe(0)
    expect(titles.indexOf('이런 모임 열어주세요')).toBe(1)
    await wrapper.findAll('button').find((b) => b.text().includes('이런 모임 열어주세요')).trigger('click')
    expect(push).toHaveBeenCalledWith('/lite/requests')
  })

  it('모임 카드에 썸네일과 남은 날짜를 보여주고, 이미지가 없으면 썸네일을 그리지 않는다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse({
      meetups: [card(), card({ id: 6, title: '이미지 없음', image_url: null })],
      my_seminar: null, seminars: [], ready_request_count: 0,
    }))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    const thumbs = wrapper.findAll('img.l-thumb')
    expect(thumbs).toHaveLength(1)
    expect(thumbs[0].attributes('src')).toBe('/media/meetups/a.png')
    expect(wrapper.findAll('.l-dday')[0].text()).toMatch(/일 후$/)
  })
})
