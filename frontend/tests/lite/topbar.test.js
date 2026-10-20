import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import LiteTopbar from '@/lite/components/LiteTopbar.vue'

vi.mock('vue-router', () => ({ useRouter: () => ({ push: vi.fn() }) }))

describe('LiteTopbar 구분선', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    window.scrollY = 0
  })
  afterEach(() => { window.scrollY = 0 })

  it('맨 위에서는 구분선이 없고 스크롤하면 생긴다', async () => {
    const wrapper = mount(LiteTopbar, { props: { title: '한입 모임' } })
    expect(wrapper.classes()).not.toContain('scrolled')

    window.scrollY = 40
    window.dispatchEvent(new Event('scroll'))
    await wrapper.vm.$nextTick()
    expect(wrapper.classes()).toContain('scrolled')

    window.scrollY = 0
    window.dispatchEvent(new Event('scroll'))
    await wrapper.vm.$nextTick()
    expect(wrapper.classes()).not.toContain('scrolled')
    wrapper.unmount()
  })
})
