<template>
  <div class="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900 py-6 sm:py-12 px-4 sm:px-6 lg:px-8 safe-area-top safe-area-bottom">
    <div class="max-w-md w-full space-y-6 sm:space-y-8">
      <!-- 테마 토글 버튼 -->
      <div class="flex justify-end">
        <ThemeToggle />
      </div>
      
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          Sign in to your account
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          Or
          <router-link to="/register" class="font-medium text-indigo-600 hover:text-indigo-500 dark:text-indigo-400">
            create a new account
          </router-link>
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleLogin">
        <div class="rounded-md shadow-sm -space-y-px">
          <div>
            <label for="email" class="sr-only">이메일</label>
            <input
              id="email"
              v-model="form.email"
              name="email"
              type="email"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-t-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="이메일 주소"
            />
          </div>
          <div>
            <label for="password" class="sr-only">비밀번호</label>
            <input
              id="password"
              v-model="form.password"
              name="password"
              type="password"
              required
              class="appearance-none rounded-none relative block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white bg-white dark:bg-gray-800 rounded-b-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm"
              placeholder="비밀번호"
            />
          </div>
        </div>

        <div class="flex items-center justify-between">
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.remember"
              name="remember-me"
              type="checkbox"
              class="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <label for="remember-me" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">
              로그인 상태 유지
            </label>
          </div>
        </div>

        <div>
          <button
            type="submit"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            로그인
          </button>
        </div>

        <div class="text-center">
          <p class="text-sm text-gray-600 dark:text-gray-400">
            테스트 계정: admin@test.com / user@test.com (비밀번호: password)
          </p>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { fetchWithCSRF } from '@/utils/csrf'

export default {
  name: 'LoginView',
  components: {
    ThemeToggle
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const form = reactive({
      email: '',
      password: '',
      remember: false
    })

    const handleLogin = async () => {
      try {
        console.log('Starting login process...')
        
        const response = await fetchWithCSRF('/api/auth/login/', {
          method: 'POST',
          body: JSON.stringify({
            username: form.email,
            password: form.password
          })
        })
        
        console.log('Login response status:', response.status)

        if (response.ok) {
          const data = await response.json()
          const userData = {
            id: data.user.id,
            name: data.user.name,
            email: data.user.email,
            username: data.user.username,
            is_admin: data.user.is_admin
          }

          await authStore.login(userData)
          
          if (userData.is_admin) {
            router.push('/admin')
          } else {
            router.push('/dashboard')
          }
        } else {
          const errorData = await response.json()
          alert(errorData.error || 'Login failed')
        }
      } catch (error) {
        alert('Network error. Please try again.')
      }
    }

    return {
      form,
      handleLogin
    }
  }
}
</script>