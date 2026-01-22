/**
 * Unit tests for meetups store
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useMeetupsStore } from '@/stores/meetups'

// Mock fetchWithCSRF
const mockFetchWithCSRF = vi.fn()
vi.mock('@/utils/csrf', () => ({
  fetchWithCSRF: (...args) => mockFetchWithCSRF(...args),
}))

describe('Meetups Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useMeetupsStore()
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have empty meetups array initially', () => {
      expect(store.meetups).toEqual([])
    })

    it('should have loading as false initially', () => {
      expect(store.loading).toBe(false)
    })

    it('should have empty error initially', () => {
      expect(store.error).toBe('')
    })
  })

  describe('fetchMeetups', () => {
    it('should fetch and set meetups on success', async () => {
      const mockMeetups = [
        { id: 1, name: 'Meetup 1', is_full: false, available_spots: 5 },
        { id: 2, name: 'Meetup 2', is_full: true, available_spots: 0 },
      ]

      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(mockMeetups),
      })

      await store.fetchMeetups()

      expect(store.meetups).toHaveLength(2)
      expect(store.meetups[0].name).toBe('Meetup 1')
      expect(store.error).toBe('')
    })

    it('should set loading state during fetch', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([]),
      })

      const fetchPromise = store.fetchMeetups()
      expect(store.loading).toBe(true)

      await fetchPromise
      expect(store.loading).toBe(false)
    })

    it('should set error on fetch failure', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: false,
      })

      await store.fetchMeetups()

      expect(store.error).not.toBe('')
    })

    it('should set error on network failure', async () => {
      mockFetchWithCSRF.mockRejectedValue(new Error('Network error'))

      await store.fetchMeetups()

      expect(store.error).not.toBe('')
    })
  })

  describe('addMeetup', () => {
    it('should add meetup to the list', () => {
      const newMeetup = { id: 1, name: 'New Meetup' }

      store.addMeetup(newMeetup)

      expect(store.meetups).toHaveLength(1)
      expect(store.meetups[0]).toEqual(newMeetup)
    })
  })

  describe('updateMeetup', () => {
    it('should update existing meetup', () => {
      store.meetups = [
        { id: 1, name: 'Old Name' },
        { id: 2, name: 'Other Meetup' },
      ]

      store.updateMeetup(1, { name: 'New Name' })

      expect(store.meetups[0].name).toBe('New Name')
      expect(store.meetups[1].name).toBe('Other Meetup')
    })

    it('should do nothing if meetup not found', () => {
      store.meetups = [{ id: 1, name: 'Meetup' }]

      store.updateMeetup(999, { name: 'New Name' })

      expect(store.meetups[0].name).toBe('Meetup')
    })
  })

  describe('deleteMeetup', () => {
    it('should remove meetup from the list', () => {
      store.meetups = [
        { id: 1, name: 'Meetup 1' },
        { id: 2, name: 'Meetup 2' },
      ]

      store.deleteMeetup(1)

      expect(store.meetups).toHaveLength(1)
      expect(store.meetups[0].id).toBe(2)
    })
  })

  describe('isMeetupFull', () => {
    it('should return true when meetup is full', () => {
      store.meetups = [{ id: 1, is_full: true }]

      expect(store.isMeetupFull(1)).toBe(true)
    })

    it('should return false when meetup is not full', () => {
      store.meetups = [{ id: 1, is_full: false }]

      expect(store.isMeetupFull(1)).toBe(false)
    })

    it('should return false when meetup not found', () => {
      store.meetups = []

      expect(store.isMeetupFull(999)).toBe(false)
    })
  })

  describe('getRegistrationCount', () => {
    it('should return current participants count', () => {
      store.meetups = [{ id: 1, current_participants: 5 }]

      expect(store.getRegistrationCount(1)).toBe(5)
    })

    it('should return 0 when meetup not found', () => {
      store.meetups = []

      expect(store.getRegistrationCount(999)).toBe(0)
    })
  })

  describe('waitlist operations', () => {
    it('should add to waitlist', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ position: 1 }),
      })

      const result = await store.addToWaitlist(1)

      expect(result.position).toBe(1)
      expect(mockFetchWithCSRF).toHaveBeenCalledWith(
        '/api/meetups/1/waitlist/',
        { method: 'POST' },
      )
    })

    it('should throw error on add to waitlist failure', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: false,
        json: () => Promise.resolve({ error: 'Already on waitlist' }),
      })

      await expect(store.addToWaitlist(1)).rejects.toThrow()
    })

    it('should remove from waitlist', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ message: 'Removed' }),
      })

      await store.removeFromWaitlist(1)

      expect(mockFetchWithCSRF).toHaveBeenCalledWith(
        '/api/meetups/1/waitlist/remove/',
        { method: 'DELETE' },
      )
    })

    it('should check waitlist status', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ is_waitlisted: true, position: 2 }),
      })

      const result = await store.checkWaitlistStatus(1)

      expect(result.is_waitlisted).toBe(true)
      expect(result.position).toBe(2)
    })
  })
})
