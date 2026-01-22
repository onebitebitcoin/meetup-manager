/**
 * Unit tests for auth store
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useAuthStore } from '@/stores/auth'

// Mock fetchWithCSRF
vi.mock('@/utils/csrf', () => ({
  fetchWithCSRF: vi.fn(),
  resetCSRFToken: vi.fn()
}))

describe('Auth Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useAuthStore()
    localStorage.clear()
  })

  describe('initial state', () => {
    it('should have null user initially', () => {
      expect(store.user).toBeNull()
    })

    it('should have isLoggedIn as false initially', () => {
      expect(store.isLoggedIn).toBe(false)
    })

    it('should have isAdmin as false initially', () => {
      expect(store.isAdmin).toBe(false)
    })

    it('should have isGuest as false initially', () => {
      expect(store.isGuest).toBe(false)
    })
  })

  describe('login', () => {
    it('should set user data on login', async () => {
      const userData = {
        id: 1,
        name: 'Test User',
        email: 'test@example.com',
        is_admin: false
      }

      await store.login(userData)

      expect(store.user).toEqual(userData)
      expect(store.isLoggedIn).toBe(true)
      expect(store.isAdmin).toBe(false)
    })

    it('should set admin flag when user is admin', async () => {
      const adminUser = {
        id: 1,
        name: 'Admin User',
        email: 'admin@example.com',
        is_admin: true
      }

      await store.login(adminUser)

      expect(store.isAdmin).toBe(true)
    })

    it('should set guest flag when user is guest', async () => {
      const guestUser = {
        id: 1,
        name: 'Guest',
        is_guest: true
      }

      await store.login(guestUser)

      expect(store.isGuest).toBe(true)
    })

    it('should store user in localStorage', async () => {
      const userData = { id: 1, name: 'Test User' }

      await store.login(userData)

      expect(localStorage.setItem).toHaveBeenCalledWith(
        'user',
        JSON.stringify(userData)
      )
    })
  })

  describe('logout', () => {
    it('should clear user data on logout', async () => {
      const userData = { id: 1, name: 'Test User' }
      await store.login(userData)

      await store.logout()

      expect(store.user).toBeNull()
      expect(store.isLoggedIn).toBe(false)
      expect(store.isAdmin).toBe(false)
      expect(store.isGuest).toBe(false)
    })

    it('should remove user from localStorage', async () => {
      const userData = { id: 1, name: 'Test User' }
      await store.login(userData)

      await store.logout()

      expect(localStorage.removeItem).toHaveBeenCalledWith('user')
    })
  })

  describe('checkAuth', () => {
    it('should restore user from localStorage', () => {
      const userData = { id: 1, name: 'Stored User', is_admin: false }
      localStorage.store['user'] = JSON.stringify(userData)

      store.checkAuth()

      expect(store.user).toEqual(userData)
      expect(store.isLoggedIn).toBe(true)
    })

    it('should not set user if localStorage is empty', () => {
      store.checkAuth()

      expect(store.user).toBeNull()
      expect(store.isLoggedIn).toBe(false)
    })
  })
})
