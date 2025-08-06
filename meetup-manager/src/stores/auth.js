import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchWithCSRF, resetCSRFToken } from '@/utils/csrf'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const isLoggedIn = ref(false)
  const isAdmin = ref(false)

  const login = async (userData) => {
    user.value = userData
    isLoggedIn.value = true
    isAdmin.value = userData.is_admin || false
    localStorage.setItem('user', JSON.stringify(userData))
    
    // Reset CSRF token so next request gets fresh one
    resetCSRFToken()
  }

  const logout = async () => {
    try {
      await fetchWithCSRF('/api/auth/logout/', {
        method: 'POST'
      })
    } catch (error) {
      console.error('Logout error:', error)
    }
    
    user.value = null
    isLoggedIn.value = false
    isAdmin.value = false
    localStorage.removeItem('user')
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
    login,
    logout,
    checkAuth
  }
})