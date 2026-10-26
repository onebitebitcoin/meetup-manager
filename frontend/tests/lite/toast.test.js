import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'
import LiteToast from '@/lite/components/LiteToast.vue'

describe('LiteToast 색 구분', () => {
  beforeEach(() => setActivePinia(createPinia()))

  it.each([
    ['참석으로 바꿨어요', 'going'],
    ['불참으로 바꿨어요', 'no'],
    ['저장했어요', 'ok'],
    ['네트워크 오류', 'error'],
  ])('%s 알림은 %s 클래스를 붙인다', async (message, kind) => {
    const store = useLiteStore()
    store.notify(message, kind)
    const wrapper = mount(LiteToast)

    const toast = wrapper.find('.l-toast')
    expect(toast.classes()).toContain(kind)
    expect(toast.text()).toBe(message)
  })

  it('act는 성공 알림에 지정한 종류를 쓴다', async () => {
    const store = useLiteStore()
    await store.act(() => Promise.resolve({}), '참석으로 바꿨어요', 'going')
    expect(store.toast).toEqual({ message: '참석으로 바꿨어요', kind: 'going' })
  })
})
