import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import { useLiteStore } from '@/lite/store'
import { liteApi } from '@/lite/api'
import LiteChat from '@/lite/components/LiteChat.vue'
import LiteMessage from '@/lite/components/LiteMessage.vue'

vi.mock('vue-router', () => ({
  useRouter: () => ({ push: vi.fn(), replace: vi.fn() }),
  useRoute: () => ({ query: {}, params: {} }),
}))

const json = (body, status = 200) => ({
  ok: status >= 200 && status < 300,
  status,
  json: () => Promise.resolve(body),
})
const msg = (extra = {}) => ({
  id: 1, kind: 'user', body: '', member: { id: 2, name: '민수' }, created_at: '2026-10-14T00:00:00Z', attachment: null, ...extra,
})
const image = { url: '/media/lite/chat/a.png', name: 'a.png', size: 2048, kind: 'image' }
const file = { url: '/media/lite/chat/b.pdf', name: '계획서.pdf', size: 3 * 1024 * 1024, kind: 'file' }

const mounted = []
const mountMsg = (message) => {
  const w = mount(LiteMessage, { props: { message } })
  mounted.push(w)
  return w
}

describe('LiteMessage 링크·첨부', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    fetch.mockReset()
    fetch.mockResolvedValue(json({ preview: null }))
  })
  afterEach(() => mounted.splice(0).forEach((w) => w.unmount()))

  it('본문 링크는 새 탭으로 여는 a 태그로 렌더링한다', async () => {
    const wrapper = mountMsg(msg({ body: '참고 https://ex-link.com/a.' }))
    await flushPromises()
    const a = wrapper.find('a.l-link')
    expect(a.attributes('href')).toBe('https://ex-link.com/a')
    expect(a.attributes('target')).toBe('_blank')
    expect(a.attributes('rel')).toContain('noopener')
  })

  it('이미지 첨부는 썸네일로 보이고 누르면 뷰어가 열린다', async () => {
    const wrapper = mountMsg(msg({ attachment: image }))
    const thumb = wrapper.find('img.l-att-img')
    expect(thumb.attributes('src')).toBe(image.url)
    expect(thumb.attributes('loading')).toBe('lazy')
    expect(wrapper.find('.l-viewer').exists()).toBe(false)
    await wrapper.find('button.l-att-open').trigger('click')
    expect(wrapper.find('.l-viewer').exists()).toBe(true)
    expect(wrapper.find('.l-viewer a[download]').attributes('href')).toBe(image.url)
    await wrapper.find('.l-viewer button[aria-label="닫기"]').trigger('click')
    expect(wrapper.find('.l-viewer').exists()).toBe(false)
  })

  it('파일 첨부는 이름과 크기, download 속성을 가진 행으로 보인다', () => {
    const wrapper = mountMsg(msg({ attachment: file }))
    const row = wrapper.find('a.l-att-file')
    expect(row.attributes('download')).toBeDefined()
    expect(row.attributes('href')).toBe(file.url)
    expect(row.text()).toContain('계획서.pdf')
    expect(row.text()).toContain('3.0MB')
  })

  it('body가 비어 있으면 텍스트 말풍선을 그리지 않는다', () => {
    const wrapper = mountMsg(msg({ attachment: file }))
    expect(wrapper.findAll('.l-bub').length).toBe(0)
  })

  it('미리보기가 null이면 카드가 없고 있으면 카드를 그린다', async () => {
    const none = mountMsg(msg({ body: 'https://none-preview.com' }))
    await flushPromises()
    expect(none.find('.l-lp').exists()).toBe(false)

    fetch.mockResolvedValue(json({ preview: { url: 'https://has-preview.com', title: '제목', description: '설명', image: null, site_name: '사이트' } }))
    const some = mountMsg(msg({ id: 2, body: 'https://has-preview.com' }))
    await flushPromises()
    expect(some.find('a.l-lp').attributes('href')).toBe('https://has-preview.com')
    expect(some.find('.l-lp').text()).toContain('제목')
  })

  it('미리보기 요청이 실패해도 카드와 에러 토스트를 띄우지 않는다', async () => {
    fetch.mockRejectedValue(new Error('x'))
    const wrapper = mountMsg(msg({ body: 'https://fail-preview.com' }))
    await flushPromises()
    expect(wrapper.find('.l-lp').exists()).toBe(false)
    expect(useLiteStore().toast).toBeFalsy()
  })
})

describe('LiteChat 첨부 전송', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    setActivePinia(createPinia())
    fetch.mockReset()
    Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'visible' })
    URL.createObjectURL = vi.fn(() => 'blob:x')
    URL.revokeObjectURL = vi.fn()
  })
  afterEach(() => {
    mounted.splice(0).forEach((w) => w.unmount())
    vi.useRealTimers()
  })

  const mountChat = async () => {
    fetch.mockImplementation((url, opts) => {
      if (opts?.method === 'POST') return Promise.resolve(json({ message: msg({ id: 5, body: '사진', attachment: image }) }, 201))
      return Promise.resolve(json({ messages: [], pinned: null }))
    })
    const wrapper = mount(LiteChat, { props: { roomId: 9 } })
    mounted.push(wrapper)
    await flushPromises()
    return wrapper
  }
  const pick = async (wrapper, f) => {
    const input = wrapper.find('input[type="file"]')
    Object.defineProperty(input.element, 'files', { configurable: true, value: [f] })
    await input.trigger('change')
  }
  const posts = () => fetch.mock.calls.filter(([, o]) => o?.method === 'POST')

  it('10MB를 넘는 파일은 선택 즉시 에러를 띄우고 업로드하지 않는다', async () => {
    const wrapper = await mountChat()
    const big = new File(['x'], 'big.png', { type: 'image/png' })
    Object.defineProperty(big, 'size', { value: 10 * 1024 * 1024 + 1 })
    await pick(wrapper, big)
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(useLiteStore().toast.kind).toBe('error')
    expect(wrapper.find('.l-attach-preview').exists()).toBe(false)
    expect(posts().length).toBe(0)
  })

  it('이미지를 고르면 미리보기가 보이고 취소하면 사라진다', async () => {
    const wrapper = await mountChat()
    await pick(wrapper, new File(['x'], 'a.png', { type: 'image/png' }))
    expect(wrapper.find('.l-attach-preview img').exists()).toBe(true)
    await wrapper.find('.l-attach-preview button[aria-label="첨부 취소"]').trigger('click')
    expect(wrapper.find('.l-attach-preview').exists()).toBe(false)
  })

  it('첨부가 있으면 uploadFile로 file과 body를 FormData에 담아 보낸다', async () => {
    const wrapper = await mountChat()
    await pick(wrapper, new File(['x'], 'a.png', { type: 'image/png' }))
    await wrapper.find('input[aria-label="메시지"]').setValue('사진')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    const [url, opts] = posts()[0]
    expect(url).toBe('/api/lite/rooms/9/files/')
    expect(opts.body).toBeInstanceOf(FormData)
    expect(opts.body.get('file').name).toBe('a.png')
    expect(opts.body.get('body')).toBe('사진')
    expect(wrapper.find('.l-attach-preview').exists()).toBe(false)
  })

  it('첨부만 있어도 보낼 수 있고 첨부가 없으면 기존 메시지 전송을 쓴다', async () => {
    const wrapper = await mountChat()
    await pick(wrapper, new File(['x'], 'b.pdf', { type: 'application/pdf' }))
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(posts()[0][0]).toBe('/api/lite/rooms/9/files/')

    await wrapper.find('input[aria-label="메시지"]').setValue('안녕')
    await wrapper.find('form').trigger('submit')
    await flushPromises()
    expect(posts()[1][0]).toBe('/api/lite/rooms/9/messages/')
  })
})

describe('공지 바', () => {
  beforeEach(() => {
    vi.useFakeTimers()
    setActivePinia(createPinia())
    fetch.mockReset()
    Object.defineProperty(document, 'visibilityState', { configurable: true, get: () => 'visible' })
  })
  afterEach(() => {
    mounted.splice(0).forEach((w) => w.unmount())
    vi.useRealTimers()
  })

  it('첨부만 있는 공지는 사진 또는 파일 이름으로 보여 준다', async () => {
    for (const [attachment, text] of [[image, '사진'], [file, '파일 · 계획서.pdf']]) {
      fetch.mockResolvedValue(json({ messages: [], pinned: msg({ attachment }) }))
      const wrapper = mount(LiteChat, { props: { roomId: 9 } })
      mounted.push(wrapper)
      await flushPromises()
      expect(wrapper.find('.l-pinbar-body').text()).toBe(text)
    }
  })
})

describe('liteApi 업로드', () => {
  beforeEach(() => fetch.mockReset())

  it('Content-Type을 직접 지정하지 않고 FormData를 그대로 보낸다', async () => {
    fetch.mockResolvedValue(json({ message: {} }, 201))
    await liteApi.uploadFile(3, new File(['x'], 'a.png'), '')
    const [url, opts] = fetch.mock.calls[0]
    expect(url).toBe('/api/lite/rooms/3/files/')
    expect(opts.headers['Content-Type']).toBeUndefined()
    expect(opts.body).toBeInstanceOf(FormData)
    expect(opts.body.has('body')).toBe(false)
  })

  it('실패하면 서버 error 메시지와 status를 담은 에러를 던진다', async () => {
    fetch.mockResolvedValue(json({ error: '파일은 10MB까지 올릴 수 있어요' }, 413))
    await expect(liteApi.uploadFile(3, new File(['x'], 'a.png'), '')).rejects.toMatchObject({
      message: '파일은 10MB까지 올릴 수 있어요',
      status: 413,
    })
  })

  it('linkPreview는 url을 인코딩해 조회한다', async () => {
    fetch.mockResolvedValue(json({ preview: null }))
    await liteApi.linkPreview('https://a.com/?q=1&b=2')
    expect(fetch.mock.calls[0][0]).toBe('/api/lite/link-preview/?url=https%3A%2F%2Fa.com%2F%3Fq%3D1%26b%3D2')
  })
})
