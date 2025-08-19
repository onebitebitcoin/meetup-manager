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
              :class="[
                'appearance-none relative block w-full px-3 py-2 border placeholder-gray-500 rounded-md focus:outline-none focus:z-10 sm:text-sm dark:bg-gray-800 dark:placeholder-gray-400',
                usernameError && form.username ? 
                  'border-red-500 text-red-900 focus:ring-red-500 focus:border-red-500' : 
                  usernameValid && form.username ?
                    'border-green-500 text-green-900 focus:ring-green-500 focus:border-green-500 dark:border-green-400 dark:text-white' :
                    'border-gray-300 text-gray-900 focus:ring-indigo-500 focus:border-indigo-500 dark:border-gray-600 dark:text-white'
              ]"
              placeholder="사용자명 (영문, 한글, 숫자, _, - 사용가능)"
            />
            <!-- Username validation message -->
            <div v-if="usernameError && form.username" class="mt-1 text-sm text-red-600 dark:text-red-400">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z" clip-rule="evenodd"/>
                </svg>
                {{ usernameError }}
              </div>
            </div>
            <!-- Username success message -->
            <div v-if="usernameValid && form.username && !usernameError" class="mt-1 text-sm text-green-600 dark:text-green-400">
              <div class="flex items-center">
                <svg class="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd"/>
                </svg>
                사용 가능한 사용자명입니다.
              </div>
            </div>
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
          <div>
            <label for="password-confirm" class="sr-only">비밀번호 확인</label>
            <input
              id="password-confirm"
              v-model="form.passwordConfirm"
              name="password-confirm"
              type="password"
              required
              class="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 focus:z-10 sm:text-sm dark:bg-gray-800 dark:border-gray-600 dark:placeholder-gray-400 dark:text-white"
              placeholder="비밀번호 확인"
            />
          </div>
        </div>

        <div v-if="error" class="text-red-600 text-sm text-center">
          {{ error }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="loading || usernameError || !usernameValid"
            :class="[
              'w-full inline-flex items-center justify-center px-6 py-3 text-sm font-medium rounded-lg transition-all duration-150 focus:outline-none focus:ring-2 focus:ring-offset-2 dark:focus:ring-offset-neutral-900',
              (loading || usernameError || !usernameValid) ? 
                'opacity-60 cursor-not-allowed bg-gray-400 dark:bg-gray-600 text-gray-200' :
                'text-white bg-neutral-900 hover:bg-neutral-800 dark:bg-neutral-700 dark:hover:bg-neutral-600 focus:ring-neutral-500'
            ]"
          >
            <span v-if="!loading">
              {{ usernameError ? '사용자명을 확인해주세요' : '계정 만들기' }}
            </span>
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
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { fetchWithCSRF } from '@/utils/csrf'
import { convertPasswordInput } from '@/utils/keyboardConverter'

export default {
  name: 'RegisterView',
  setup() {
    const router = useRouter()
    const loading = ref(false)
    const error = ref('')
    
    const form = ref({
      username: '',
      email: '',
      password: '',
      passwordConfirm: ''
    })

    const usernameError = ref('')
    const usernameValid = ref(false)

    // Username validation function
    const validateUsername = (username) => {
      if (!username) {
        usernameError.value = '사용자명을 입력해주세요.'
        usernameValid.value = false
        return false
      }

      if (username.length < 3) {
        usernameError.value = '사용자명은 최소 3자 이상이어야 합니다.'
        usernameValid.value = false
        return false
      }

      if (username.length > 150) {
        usernameError.value = '사용자명은 150자를 초과할 수 없습니다.'
        usernameValid.value = false
        return false
      }

      // Check for whitespace
      if (/\s/.test(username)) {
        usernameError.value = '사용자명에는 공백을 사용할 수 없습니다.'
        usernameValid.value = false
        return false
      }

      // Check for invalid characters
      if (!/^[a-zA-Z0-9가-힣ㄱ-ㅎㅏ-ㅣ_-]+$/.test(username)) {
        usernameError.value = '사용자명은 영문, 한글, 숫자, 밑줄(_), 하이픈(-)만 사용할 수 있습니다.'
        usernameValid.value = false
        return false
      }

      // Check if starts or ends with special characters
      if (/^[-_]|[-_]$/.test(username)) {
        usernameError.value = '사용자명은 밑줄(_)이나 하이픈(-)으로 시작하거나 끝날 수 없습니다.'
        usernameValid.value = false
        return false
      }

      // Check for consecutive special characters
      if (/--|__|_-|-_/.test(username)) {
        usernameError.value = '사용자명에는 연속된 특수문자를 사용할 수 없습니다.'
        usernameValid.value = false
        return false
      }

      usernameError.value = ''
      usernameValid.value = true
      return true
    }

    // Watch for username changes for real-time validation
    watch(() => form.value.username, (newUsername) => {
      if (newUsername) {
        validateUsername(newUsername)
      } else {
        usernameError.value = ''
        usernameValid.value = false
      }
    })

    const handleRegister = async () => {
      // Validate username before submitting
      if (!validateUsername(form.value.username)) {
        return
      }
      // Convert Korean passwords to English
      const convertedPassword = convertPasswordInput(form.value.password)
      const convertedPasswordConfirm = convertPasswordInput(form.value.passwordConfirm)
      
      if (convertedPassword !== convertedPasswordConfirm) {
        error.value = '비밀번호가 일치하지 않습니다.'
        return
      }

      loading.value = true
      error.value = ''

      try {
        const response = await fetchWithCSRF('/api/auth/register/', {
          method: 'POST',
          body: JSON.stringify({
            username: form.value.username,
            email: form.value.email,
            password: convertedPassword
          })
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
      usernameError,
      usernameValid,
      handleRegister
    }
  }
}
</script>
