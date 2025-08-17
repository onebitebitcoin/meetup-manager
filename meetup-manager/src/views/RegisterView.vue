<template>
  <div class="min-h-screen flex items-center justify-center bg-beige-50 dark:bg-neutral-950 py-12 px-4 sm:px-6 lg:px-8 safe-area-top safe-area-bottom transition-all duration-300">
    <div class="max-w-md w-full space-y-8">
      <div>
        <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900 dark:text-white">
          계정 만들기
        </h2>
        <p class="mt-2 text-center text-sm text-gray-600 dark:text-gray-400">
          또는
          <router-link
            to="/login"
            class="font-semibold text-neutral-700 hover:text-neutral-900 dark:text-neutral-300 dark:hover:text-neutral-100 underline underline-offset-2"
          >
            기존 계정으로 로그인
          </router-link>
        </p>
      </div>
      <form class="mt-8 space-y-6" @submit.prevent="handleRegister">
        <div class="rounded-md shadow-sm space-y-3">
          <div>
            <label for="username" class="sr-only">사용자명</label>
            <input
              id="username"
              v-model="form.username"
              name="username"
              type="text"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
              placeholder="사용자명"
            />
          </div>
          <div>
            <label for="email" class="sr-only">이메일 주소</label>
            <input
              id="email"
              v-model="form.email"
              name="email"
              type="email"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white rounded-md"
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
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white rounded-md"
              placeholder="비밀번호"
            />
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading"
            class="w-full inline-flex items-center justify-center px-6 py-3 text-sm font-medium text-white bg-neutral-900 hover:bg-neutral-800 dark:bg-neutral-700 dark:hover:bg-neutral-600 rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-neutral-500 focus:ring-offset-2 dark:focus:ring-offset-neutral-900 disabled:opacity-60 disabled:cursor-not-allowed"
          >
            <span v-if="!loading">계정 만들기</span>
            <span v-else>계정 생성 중...</span>
          </button>
        </div>
        
        <div class="text-center">
          <router-link
            to="/help"
            class="text-xs text-neutral-700 hover:text-neutral-900 dark:text-neutral-300 dark:hover:text-neutral-100 underline underline-offset-2"
          >
            📚 사용 가이드 보기
          </router-link>
        </div>
      </form>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchWithCSRF } from '@/utils/csrf'

export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const error = ref('')
    
    const form = ref({
      username: '',
      email: '',
      password: ''
    })

    const handleRegister = async () => {
      loading.value = true
      error.value = ''

      try {
        const response = await fetchWithCSRF('/api/auth/register/', {
          method: 'POST',
          body: JSON.stringify(form.value)
        })

        const data = await response.json()

        if (response.ok) {
          router.push('/login?message=회원가입이 완료되었습니다. 로그인해주세요.')
        } else {
          error.value = data.error || '회원가입에 실패했습니다. 다시 시도해주세요.'
        }
      } catch (err) {
        error.value = '네트워크 오류가 발생했습니다. 다시 시도해주세요.'
      } finally {
        loading.value = false
      }
    }

    return {
      form,
      loading,
      error,
      handleRegister
    }
  }
}
</script>
