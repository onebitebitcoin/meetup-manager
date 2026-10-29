import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'
import { TOKEN_KEY } from '@/lite/api'
import LiteMeMenu from '@/lite/components/LiteMeMenu.vue'

const jsonResponse = (body, status = 200) => ({ ok: status < 400, status, json: () => Promise.resolve(body) })

describe('LiteMeMenu 새 이름 받기', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.setItem(TOKEN_KEY, 'tok')
    global.fetch = vi.fn()
  })

  const mountWithMember = () => {
    const store = useLiteStore()
    store.setToken('tok')
    store.member = { id: 1, name: '지민', is_host: false }
    return { store, wrapper: mount(LiteMeMenu) }
  }

  const confirmRename = async (wrapper) => {
    const ok = wrapper.findAll('.l-me-confirm button').find((b) => b.text() === '바꾸기')
    await ok.trigger('click')
    await flushPromises()
  }

  it('새로고침을 누르면 바로 바꾸지 않고 확인을 묻고, 그만두기를 누르면 닫는다', async () => {
    const { store, wrapper } = mountWithMember()

    await wrapper.find('button[aria-label="새 이름 받기"]').trigger('click')

    expect(fetch).not.toHaveBeenCalled()
    expect(wrapper.find('.l-me-confirm').text()).toContain('새 이름으로 바꿀까요?')

    const cancel = wrapper.findAll('.l-me-confirm button').find((b) => b.text() === '그만두기')
    await cancel.trigger('click')

    expect(wrapper.find('.l-me-confirm').exists()).toBe(false)
    expect(fetch).not.toHaveBeenCalled()
    expect(store.member.name).toBe('지민')
  })

  it('이름 지우기 메뉴 없이 새로고침 버튼만 둔다', () => {
    const { wrapper } = mountWithMember()
    expect(wrapper.text()).toContain('지민')
    expect(wrapper.text()).not.toContain('지우기')
    expect(wrapper.find('button[aria-label="새 이름 받기"]').exists()).toBe(true)
  })

  it('새로고침을 누르면 자동 닉네임으로 이름만 바꾸고 토큰은 그대로 둔다', async () => {
    const { store, wrapper } = mountWithMember()
    fetch.mockImplementation((url, init) => Promise.resolve(
      jsonResponse({ member: { id: 1, name: JSON.parse(init.body).name, is_host: false } }),
    ))

    await wrapper.find('button[aria-label="새 이름 받기"]').trigger('click')
    await confirmRename(wrapper)

    const [url, init] = fetch.mock.calls[0]
    expect(url).toContain('/api/lite/me/')
    expect(init.method).toBe('PATCH')
    expect(store.member.name).toBe(JSON.parse(init.body).name)
    expect(store.member.name).not.toBe('지민')
    expect(localStorage.getItem(TOKEN_KEY)).toBe('tok')
    expect(store.toast).toEqual({ message: `이제 ${store.member.name}님이에요`, kind: 'ok' })
    expect(wrapper.find('.l-me-confirm').exists()).toBe(false)
  })

  it('이름이 겹치면(409) 다시 뽑고, 실패하면 에러 알림을 띄운다', async () => {
    const { store, wrapper } = mountWithMember()
    fetch
      .mockResolvedValueOnce(jsonResponse({ error: '이미 사용 중인 이름이에요' }, 409))
      .mockResolvedValueOnce(jsonResponse({ error: '요청이 너무 많아요' }, 429))

    await wrapper.find('button[aria-label="새 이름 받기"]').trigger('click')
    await confirmRename(wrapper)

    expect(fetch).toHaveBeenCalledTimes(2)
    expect(store.member.name).toBe('지민')
    expect(store.toast.kind).toBe('error')
  })
})
