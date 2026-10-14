import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import LiteProgress from '@/lite/components/LiteProgress.vue'

describe('LiteProgress', () => {
  it('공감 수만큼 칸을 채우고 나머지는 비운다', () => {
    const wrapper = mount(LiteProgress, { props: { count: 3, total: 5 } })

    const cells = wrapper.findAll('i')
    expect(cells).toHaveLength(5)
    expect(cells.filter((c) => c.classes('on'))).toHaveLength(3)
    expect(wrapper.attributes('aria-label')).toBe('5명 중 3명')
  })

  it('공감 수가 기준을 넘어도 기준 칸 수까지만 채운다', () => {
    const wrapper = mount(LiteProgress, { props: { count: 7, total: 5 } })

    expect(wrapper.findAll('i.on')).toHaveLength(5)
    expect(wrapper.attributes('aria-label')).toBe('5명 중 5명')
  })
})
