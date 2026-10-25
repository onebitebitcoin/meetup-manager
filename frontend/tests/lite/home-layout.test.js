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

  it('일반 회원은 1:1 세미나와 요청을 목록 대신 플로팅 버튼 메뉴로 연다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse({ meetups: [card()], my_seminar: { id: 3, status: 'received', mode: 'online' }, seminars: [], ready_request_count: 0 }))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.find('.l-top h2').text()).toBe('한입 모임')
    expect(wrapper.find('nav').exists()).toBe(false)
    const titles = wrapper.findAll('.l-title').map((t) => t.text())
    expect(titles).not.toContain('1:1 세미나')
    expect(titles).not.toContain('이런 모임 열어주세요')
    expect(wrapper.find('.l-fab-menu').exists()).toBe(false)

    await wrapper.find('.l-fab-btn').trigger('click')
    const items = wrapper.findAll('.l-fab-menu button')
    expect(items.map((b) => b.text())).toEqual(['1:1 세미나접수됨', '이런 모임 열어주세요'])

    await items[1].trigger('click')
    expect(push).toHaveBeenCalledWith('/lite/new-request')
    expect(wrapper.find('.l-fab-menu').exists()).toBe(false)
  })

  it('운영자는 플로팅 버튼 없이 세미나 대화 카드와 요청 항목을 목록에서 본다', async () => {
    useLiteStore().member = { id: 9, name: '운영', is_host: true }
    fetch.mockResolvedValue(jsonResponse({
      meetups: [], my_seminar: null, ready_request_count: 2,
      seminars: [{ id: 4, status: 'received', mode: null, member: { id: 1, name: '지민' } }],
    }))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    expect(wrapper.find('.l-fab-btn').exists()).toBe(false)
    const titles = wrapper.findAll('.l-title').map((t) => t.text())
    expect(titles).toEqual(['1:1 · 지민', '이런 모임 열어주세요'])
    expect(wrapper.text()).toContain('개설 가능 2')
  })

  it('다음 모임 카드에 날짜 배지를, 목록 줄에 썸네일을 보여주고, 이미지가 없으면 PC 카드용 빈 자리만 둔다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse({
      meetups: [
        card({ id: 4, title: '가장 가까운 모임', starts_at: '2099-10-18T04:00:00Z', image_url: null }),
        card(),
        card({ id: 6, title: '이미지 없음', image_url: null }),
      ],
      my_seminar: null, seminars: [], ready_request_count: 0,
    }))
    const { default: LiteHome } = await import('@/lite/views/LiteHome.vue')

    const wrapper = mount(LiteHome)
    await flushPromises()

    const thumbs = wrapper.findAll('img.l-thumb')
    expect(thumbs).toHaveLength(1)
    expect(thumbs[0].attributes('src')).toBe('/media/meetups/a.png')
    // 빈 자리는 모바일에서 숨기고 1024px 이상 카드 그리드에서만 이미지 영역으로 보인다
    expect(wrapper.findAll('.l-mrow .l-thumb-empty')).toHaveLength(1)
    expect(wrapper.find('.l-body').classes()).toContain('l-home')
    expect(wrapper.find('.l-next .l-next-badge b').text()).toBe('10/18 (일)')
  })
})
