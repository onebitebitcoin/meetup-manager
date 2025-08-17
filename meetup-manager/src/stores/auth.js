import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchWithCSRF, resetCSRFToken } from '@/utils/csrf'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const isAdmin = ref(false)
  const isGuest = ref(false)

  const login = async (userData) => {
    user.value = userData
    isLoggedIn.value = true
    isAdmin.value = userData.is_admin || false
    isGuest.value = userData.is_guest || false
    localStorage.setItem('user', JSON.stringify(userData))
    
    // Reset CSRF token immediately after login for fresh session
    resetCSRFToken()
    
    // Pre-fetch CSRF token for subsequent requests
    if (!userData.is_guest) {
      try {
        await fetch('/api/csrf/', {
          credentials: 'include',
          headers: {
            'Origin': window.location.origin,
            'Referer': window.location.href
          }
        })
      } catch (error) {
        console.warn('Failed to pre-fetch CSRF token after login:', error)
      }
    }
  }

  const logout = async () => {
    // Clear client state immediately to avoid guard redirect loops
    const wasGuest = isGuest.value
    user.value = null
    isLoggedIn.value = false
    isAdmin.value = false
    isGuest.value = false
    localStorage.removeItem('user')

    // Fire-and-forget server logout for non-guest users
    if (!wasGuest) {
      try {
        fetchWithCSRF('/api/auth/logout/', { method: 'POST' })
          .catch(err => console.warn('Logout API error (ignored):', err))
      } catch (error) {
        console.warn('Logout scheduling error (ignored):', error)
      }
    }
  }

  const checkAuth = () => {
    const stored = localStorage.getItem('user')
    if (stored) {
      const userData = JSON.parse(stored)
      login(userData)
    }
  }

  return {
    user,
    isLoggedIn,
    isAdmin,
    isGuest,
    login,
    logout,
    checkAuth
  }
})
