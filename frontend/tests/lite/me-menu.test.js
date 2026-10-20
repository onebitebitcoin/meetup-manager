import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'
import { TOKEN_KEY } from '@/lite/api'
import LiteMeMenu from '@/lite/components/LiteMeMenu.vue'

describe('LiteMeMenu 이 기기에서 이름 지우기', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.setItem(TOKEN_KEY, 'tok')
    global.fetch = vi.fn()
  })

  it('확인을 거쳐 지우면 저장된 토큰과 회원 정보를 지우고 서버는 호출하지 않는다', async () => {
    const store = useLiteStore()
    store.setToken('tok')
    store.member = { id: 1, name: '지민', is_host: false }
    const wrapper = mount(LiteMeMenu)

    await wrapper.find('.l-me').trigger('click')
    expect(wrapper.text()).toContain('이 기기에서 이름을 지울까요?')
    await wrapper.findAll('.l-me-menu button').find((b) => b.text() === '지우기').trigger('click')

    expect(store.member).toBeNull()
    expect(localStorage.getItem(TOKEN_KEY)).toBeNull()
    expect(store.toast.message).toBe('이 기기에서 이름을 지웠어요')
    expect(fetch).not.toHaveBeenCalled()
  })

  it('그만두기를 누르면 아무것도 지우지 않고 닫는다', async () => {
    const store = useLiteStore()
    store.setToken('tok')
    store.member = { id: 1, name: '지민', is_host: false }
    const wrapper = mount(LiteMeMenu)

    await wrapper.find('.l-me').trigger('click')
    await wrapper.findAll('.l-me-menu button').find((b) => b.text() === '그만두기').trigger('click')

    expect(store.member.name).toBe('지민')
    expect(localStorage.getItem(TOKEN_KEY)).toBe('tok')
    expect(wrapper.find('.l-me-menu').exists()).toBe(false)
  })
})
