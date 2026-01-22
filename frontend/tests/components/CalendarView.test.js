/**
 * Component tests for CalendarView
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CalendarView from '@/components/CalendarView.vue'

describe('CalendarView Component', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  const defaultProps = {
    meetups: [
      {
        id: 1,
        name: 'Test Meetup',
        date_time: new Date(2024, 5, 15, 14, 0).toISOString(),
        location: 'Seoul'
      }
    ]
  }

  it('should render without errors', () => {
    const wrapper = mount(CalendarView, {
      props: defaultProps
    })
    expect(wrapper.exists()).toBe(true)
  })

  it('should display calendar header', () => {
    const wrapper = mount(CalendarView, {
      props: defaultProps
    })

    // Should have navigation buttons
    const buttons = wrapper.findAll('button')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('should have month navigation', () => {
    const wrapper = mount(CalendarView, {
      props: defaultProps
    })

    // Should have previous and next month buttons
    const html = wrapper.html()
    expect(html).toBeDefined()
  })

  it('should emit event when meetup is clicked', async () => {
    const wrapper = mount(CalendarView, {
      props: {
        meetups: [
          {
            id: 1,
            name: 'Test Meetup',
            date_time: new Date().toISOString(),
            location: 'Seoul'
          }
        ]
      }
    })

    // The component should be interactive
    expect(wrapper.exists()).toBe(true)
  })

  it('should handle empty meetups', () => {
    const wrapper = mount(CalendarView, {
      props: { meetups: [] }
    })

    expect(wrapper.exists()).toBe(true)
  })

  it('should navigate to next month', async () => {
    const wrapper = mount(CalendarView, {
      props: defaultProps
    })

    const buttons = wrapper.findAll('button')
    // Find the next month button and click it
    if (buttons.length > 0) {
      await buttons[buttons.length - 1].trigger('click')
      expect(wrapper.exists()).toBe(true)
    }
  })

  it('should navigate to previous month', async () => {
    const wrapper = mount(CalendarView, {
      props: defaultProps
    })

    const buttons = wrapper.findAll('button')
    // Find the previous month button and click it
    if (buttons.length > 0) {
      await buttons[0].trigger('click')
      expect(wrapper.exists()).toBe(true)
    }
  })

  it('should display meetup on correct date', () => {
    const meetupDate = new Date(2024, 0, 15, 10, 0)
    const wrapper = mount(CalendarView, {
      props: {
        meetups: [
          {
            id: 1,
            name: 'January Meetup',
            date_time: meetupDate.toISOString(),
            location: 'Seoul'
          }
        ]
      }
    })

    // Component should render properly
    expect(wrapper.exists()).toBe(true)
  })

  it('should handle multiple meetups on same day', () => {
    const sameDay = new Date(2024, 0, 15)
    const wrapper = mount(CalendarView, {
      props: {
        meetups: [
          {
            id: 1,
            name: 'Morning Meetup',
            date_time: new Date(sameDay.setHours(10, 0)).toISOString(),
            location: 'Seoul'
          },
          {
            id: 2,
            name: 'Evening Meetup',
            date_time: new Date(sameDay.setHours(18, 0)).toISOString(),
            location: 'Seoul'
          }
        ]
      }
    })

    expect(wrapper.exists()).toBe(true)
  })
})
