<template>
  <div class="min-h-screen flex items-center justify-center bg-beige-50 dark:bg-neutral-950 py-6 sm:py-12 px-4 sm:px-6 lg:px-8 safe-area-top safe-area-bottom transition-all duration-300">
    <!-- Subtle background decoration with beige accent -->
    <div class="absolute inset-0 overflow-hidden pointer-events-none">
      <div class="absolute -top-40 -right-40 w-80 h-80 bg-beige-100/50 dark:bg-neutral-800/20 rounded-full blur-3xl" />
      <div class="absolute -bottom-40 -left-40 w-80 h-80 bg-beige-200/40 dark:bg-neutral-800/20 rounded-full blur-3xl" />
    </div>

    <div class="relative z-10 max-w-md w-full">
      <!-- Theme toggle positioned at top right -->
      <div class="flex justify-end mb-8">
        <ThemeToggle variant="neutral" />
      </div>

      <!-- Main login card -->
      <div class="card card-elevated p-8 animate-slide-up">
        <!-- Header section -->
        <div class="text-center mb-8">
          <div class="mb-6">
            <h1 class="text-4xl font-bold mb-3 text-neutral-900 dark:text-neutral-100 text-balance">
              한입 모임
            </h1>
            <p class="text-neutral-600 dark:text-neutral-400 text-balance">
              환영합니다! 계속하려면 로그인해주세요
            </p>
          </div>
          
          <div class="text-sm text-neutral-500 dark:text-neutral-500">
            또는
            <router-link
              to="/register"
              class="font-semibold text-neutral-700 hover:text-neutral-900 dark:text-neutral-300 dark:hover:text-neutral-100 underline underline-offset-2 transition-colors ml-1"
            >
              새 계정 만들기
            </router-link>
          </div>
        </div>

        <!-- Login form -->
        <form class="space-y-6" @submit.prevent="handleLogin">
          <div class="space-y-4">
            <div>
              <label for="username" class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                사용자명 또는 이메일
              </label>
              <input
                id="username"
                v-model="form.username"
                name="username"
                type="text"
                required
                autocomplete="username"
                class="input-primary focus:ring-neutral-500 focus:border-neutral-500"
                placeholder="사용자명 또는 이메일을 입력해주세요"
              >
            </div>
            
            <div>
              <label for="password" class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                비밀번호
              </label>
              <input
                id="password"
                v-model="form.password"
                name="password"
                type="password"
                required
                autocomplete="current-password"
                class="input-primary focus:ring-neutral-500 focus:border-neutral-500"
                placeholder="비밀번호를 입력해주세요"
              >
            </div>
            <p
              v-if="errorMessage"
              class="text-sm text-red-600 dark:text-red-400"
            >
              {{ errorMessage }}
            </p>
          </div>

          <!-- Remember me checkbox -->
          <div class="flex items-center">
            <input
              id="remember-me"
              v-model="form.remember"
              name="remember-me"
              type="checkbox"
              class="h-4 w-4 text-neutral-700 focus:ring-neutral-500 border-neutral-300 dark:border-neutral-600 rounded bg-white dark:bg-neutral-900"
            >
            <label for="remember-me" class="ml-3 block text-sm text-neutral-700 dark:text-neutral-300">
              로그인 상태 유지
            </label>
          </div>

          <!-- Action buttons -->
          <div class="space-y-3">
            <button
              type="submit"
              class="w-full inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-white bg-neutral-900 hover:bg-neutral-800 dark:bg-neutral-700 dark:hover:bg-neutral-600 rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900 disabled:opacity-60 disabled:cursor-not-allowed"
              :disabled="!form.username || !form.password"
            >
              로그인
            </button>

            <div class="relative">
              <div class="absolute inset-0 flex items-center">
                <div class="w-full border-t border-neutral-200 dark:border-neutral-700" />
              </div>
              <div class="relative flex justify-center text-sm">
                <span class="px-3 bg-white dark:bg-neutral-900 text-neutral-500 dark:text-neutral-400">또는</span>
              </div>
            </div>

            <button
              type="button"
              class="btn-secondary w-full"
              @click="handleGuestLogin"
            >
              <svg
                class="w-4 h-4 mr-2"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              게스트로 입장
            </button>
          </div>

          <!-- Help and info -->
          <div class="text-center space-y-3 pt-4 border-t border-neutral-100 dark:border-neutral-800">
            <div class="status-info">
              <svg
                class="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                />
              </svg>
              게스트 모드: 모임 조회만 가능
            </div>
            
            <router-link
              to="/help"
              class="inline-flex items-center text-sm text-neutral-700 hover:text-neutral-900 dark:text-neutral-300 dark:hover:text-neutral-100 underline underline-offset-2 transition-colors"
            >
              <svg
                class="w-4 h-4 mr-1"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                />
              </svg>
              사용 가이드 보기
            </router-link>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import ThemeToggle from '@/components/ThemeToggle.vue'
import { fetchWithCSRF } from '@/utils/csrf'
import { convertPasswordInput } from '@/utils/keyboardConverter'

export default {
  name: 'LoginView',
  components: {
    ThemeToggle,
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()

    const form = reactive({
      username: '',
      password: '',
      remember: false,
    })
    const errorMessage = ref('')

    const handleLogin = async () => {
      try {
        console.log('Starting login process...')
        errorMessage.value = ''

        // Convert Korean password input to English if necessary
        const convertedPassword = convertPasswordInput(form.password)

        const response = await fetchWithCSRF('/api/auth/login/', {
          method: 'POST',
          body: JSON.stringify({
            username: form.username,
            password: convertedPassword,
          }),
        })

        console.log('Login response status:', response.status)

        if (response.ok) {
          const data = await response.json()
          const userData = {
            id: data.user.id,
            name: data.user.name,
            email: data.user.email,
            username: data.user.username,
            is_admin: data.user.is_admin,
            is_guest: false,
          }

          await authStore.login(userData)

          // Small delay to ensure authentication state is fully established
          await new Promise((resolve) => setTimeout(resolve, 100))

          if (userData.is_admin) {
            router.push('/admin')
          } else {
            router.push('/dashboard')
          }
          errorMessage.value = ''
        } else {
          let fallbackMessage = '입력한 아이디 / 비밀번호가 틀렸습니다.'
          try {
            const errorData = await response.json()
            fallbackMessage = errorData.error || fallbackMessage
          } catch (parseError) {
            console.error('Failed to parse login error response:', parseError)
          }
          errorMessage.value = fallbackMessage
        }
      } catch (error) {
        console.error('Login request failed:', error)
        errorMessage.value = '입력한 아이디 / 비밀번호가 틀렸습니다.'
      }
    }

    const handleGuestLogin = async () => {
      try {
        const guestUserData = {
          id: 'guest',
          name: '게스트 사용자',
          email: 'guest@example.com',
          username: 'guest',
          is_admin: false,
          is_guest: true,
        }

        await authStore.login(guestUserData)
        router.push('/dashboard')
      } catch (error) {
        alert('게스트 로그인에 실패했습니다.')
      }
    }

    return {
      form,
      errorMessage,
      handleLogin,
      handleGuestLogin,
    }
  },
}
</script>
