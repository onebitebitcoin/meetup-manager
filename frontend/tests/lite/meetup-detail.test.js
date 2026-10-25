import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import { useLiteStore } from '@/lite/store'

const push = vi.fn()
vi.mock('vue-router', () => ({
  useRouter: () => ({ push, replace: vi.fn() }),
  useRoute: () => ({ params: { id: '5' }, query: {} }),
}))

const jsonResponse = (body, status = 200) => ({ ok: status < 400, status, json: () => Promise.resolve(body) })

const card = (over = {}) => ({
  id: 5, title: '멀티시그 지갑 실습', starts_at: '2099-11-08T05:00:00Z', location: '강남 토즈', capacity: 15,
  going_count: 3, maybe_count: 0, my_status: null, from_request: false, is_today: false, room_id: 9,
  image_url: null, cancelled: false, ...over,
})

const detail = (over = {}) => ({
  meetup: card(over), description: '지갑을 직접 만들어 봅니다', audience: '처음 접하는 분',
  removed: false,
})

describe('LiteMeetupDetail (자세히 화면)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    global.fetch = vi.fn()
    push.mockReset()
  })

  it('신청한 회원에게 모임 안내와 공지 확인하기를 보여 주고, 누르면 채팅방으로 간다', async () => {
    useLiteStore().member = { id: 1, name: '지민', is_host: false }
    fetch.mockResolvedValue(jsonResponse(detail({ my_status: 'going' })))
    const { default: LiteMeetupDetail } = await import('@/lite/views/LiteMeetupDetail.vue')

    const wrapper = mount(LiteMeetupDetail)
    await flushPromises()

    expect(wrapper.findAll('.l-info dt').map((d) => d.text())).toEqual(['언제', '어디서', '정원', '대상', '내용'])
    const button = wrapper.findAll('button').find((b) => b.text() === '공지 확인하기')
    await button.trigger('click')
    expect(push).toHaveBeenCalledWith('/lite/m/5')
  })

  it('아직 신청하지 않았으면 공지 확인하기 대신 신청하기를 보여 준다', async () => {
    fetch.mockResolvedValue(jsonResponse(detail()))
    const { default: LiteMeetupDetail } = await import('@/lite/views/LiteMeetupDetail.vue')

    const wrapper = mount(LiteMeetupDetail)
    await flushPromises()

    expect(wrapper.text()).not.toContain('공지 확인하기')
    expect(wrapper.findAll('button').some((b) => b.text() === '신청하기')).toBe(true)
  })

  it('취소된 모임은 안내 문구만 두고 신청 버튼을 숨긴다', async () => {
    fetch.mockResolvedValue(jsonResponse(detail({ cancelled: true })))
    const { default: LiteMeetupDetail } = await import('@/lite/views/LiteMeetupDetail.vue')

    const wrapper = mount(LiteMeetupDetail)
    await flushPromises()

    expect(wrapper.text()).toContain('취소된 모임이에요')
    expect(wrapper.findAll('button').some((b) => b.text() === '신청하기')).toBe(false)
  })
})
