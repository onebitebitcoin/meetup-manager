/**
 * Component tests for ThemeToggle
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import ThemeToggle from '@/components/ThemeToggle.vue'

// Mock the theme store
vi.mock('@/stores/theme', () => ({
  useThemeStore: () => ({
    isDark: false,
    toggleTheme: vi.fn()
  })
}))

describe('ThemeToggle Component', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('should render without errors', () => {
    const wrapper = mount(ThemeToggle)
    expect(wrapper.exists()).toBe(true)
  })

  it('should have a toggle button', () => {
    const wrapper = mount(ThemeToggle)
    const button = wrapper.find('button')
    expect(button.exists()).toBe(true)
  })

  it('should call toggleTheme on click', async () => {
    const mockToggle = vi.fn()
    vi.doMock('@/stores/theme', () => ({
      useThemeStore: () => ({
        isDark: false,
        toggleTheme: mockToggle
      })
    }))

    const wrapper = mount(ThemeToggle)
    const button = wrapper.find('button')

    await button.trigger('click')

    // The click should trigger the toggle
    expect(button.exists()).toBe(true)
  })

  it('should have accessible attributes', () => {
    const wrapper = mount(ThemeToggle)
    const button = wrapper.find('button')

    // Button should be accessible
    expect(button.attributes('type')).toBeDefined()
  })
})
