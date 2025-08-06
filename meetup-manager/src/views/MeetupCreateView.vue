<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- Navigation -->
    <nav class="bg-white dark:bg-gray-800 shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900 dark:text-white">새 모임 만들기</h1>
          </div>
          <div class="flex items-center space-x-4">
            <router-link
              to="/dashboard"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"
            >
              대시보드
            </router-link>
            <router-link
              to="/settings"
              class="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"
            >
              내 모임
            </router-link>
            <ThemeToggle />
            <span class="text-gray-700 dark:text-gray-300">{{ authStore.user?.name }}님</span>
            <button
              @click="logout"
              class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium"
            >
              로그아웃
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Header Card -->
        <div class="bg-white dark:bg-gray-800 overflow-hidden shadow rounded-lg mb-6">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <svg class="h-8 w-8 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                </svg>
              </div>
              <div class="ml-5">
                <h3 class="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                  새로운 모임을 만들어보세요
                </h3>
                <p class="mt-1 max-w-2xl text-sm text-gray-500 dark:text-gray-400">
                  사람들과 함께할 멋진 모임을 계획하고 공유하세요.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Form Card -->
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg">
          <div class="px-4 py-5 sm:p-6">
            <form @submit.prevent="handleSubmit" class="space-y-6">
              <div class="grid grid-cols-1 gap-6">
                <div>
                  <label for="name" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    모임 이름 *
                  </label>
                  <input
                    type="text"
                    id="name"
                    v-model="form.name"
                    required
                    placeholder="예: JavaScript 스터디 모임"
                    class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 sm:text-base"
                  />
                </div>

                <div>
                  <label for="description" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    상세 설명
                  </label>
                  <textarea
                    id="description"
                    v-model="form.description"
                    rows="5"
                    placeholder="모임에 대한 자세한 설명을 작성해주세요..."
                    class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 sm:text-base resize-y"
                  ></textarea>
                  <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    모임의 목적, 진행 방식, 준비물 등을 포함해주세요.
                  </p>
                </div>

                <div>
                  <label for="date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    날짜 *
                  </label>
                  <input
                    type="date"
                    id="date"
                    v-model="form.date"
                    required
                    class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-base"
                  />
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <label for="time" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      시작 시간 *
                    </label>
                    <input
                      type="time"
                      id="time"
                      v-model="form.time"
                      required
                      class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-base"
                    />
                  </div>

                  <div>
                    <label for="duration" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      모임 진행 시간 (시간) *
                    </label>
                    <input
                      type="number"
                      id="duration"
                      v-model.number="form.duration"
                      min="0.5"
                      step="0.5"
                      placeholder="예: 2 (2시간)"
                      required
                      class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 sm:text-base"
                    />
                    <p class="mt-1 text-xs text-gray-500 dark:text-gray-400">
                      모임이 진행될 시간을 입력하세요
                    </p>
                  </div>
                </div>

                <div>
                  <label for="location" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    장소 *
                  </label>
                  <input
                    type="text"
                    id="location"
                    v-model="form.location"
                    required
                    placeholder="예: 강남역 스타벅스 2층"
                    class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white dark:placeholder-gray-400 sm:text-base"
                  />
                </div>

                <div>
                  <label for="max_participants" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
                    최대 참여 인원 *
                  </label>
                  <input
                    type="number"
                    id="max_participants"
                    v-model.number="form.max_participants"
                    min="1"
                    max="100"
                    required
                    class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 dark:bg-gray-700 dark:border-gray-600 dark:text-white sm:text-base"
                  />
                  <p class="mt-2 text-sm text-gray-500 dark:text-gray-400">
                    모임에 참여할 수 있는 최대 인원을 설정해주세요.
                  </p>
                </div>
              </div>

              <div v-if="error" class="rounded-md bg-red-50 dark:bg-red-900 p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <p class="text-sm text-red-700 dark:text-red-200">{{ error }}</p>
                  </div>
                </div>
              </div>

              <div class="flex justify-end space-x-3 pt-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  type="button"
                  @click="$router.go(-1)"
                  class="bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-4 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
                >
                  취소
                </button>
                <button
                  type="submit"
                  :disabled="loading"
                  class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ loading ? '생성 중...' : '모임 만들기' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'
import ThemeToggle from '@/components/ThemeToggle.vue'

export default {
  name: 'MeetupCreateView',
  components: {
    ThemeToggle
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const loading = ref(false)
    const error = ref('')

    const form = ref({
      name: '',
      description: '',
      date: '',
      time: '',
      duration: 2,
      location: '',
      max_participants: 10
    })

    const handleSubmit = async () => {
      loading.value = true
      error.value = ''

      try {
        // Check if user is authenticated
        if (!authStore.isLoggedIn) {
          error.value = '로그인이 필요합니다'
          return
        }

        const dateTime = `${form.value.date}T${form.value.time}:00`
        
        // Calculate end time from start time and duration
        const startDate = new Date(dateTime)
        const endDate = new Date(startDate.getTime() + (form.value.duration * 60 * 60 * 1000))
        const endDateTime = endDate.toISOString()
        
        const meetupData = {
          name: form.value.name,
          description: form.value.description,
          date_time: new Date(dateTime).toISOString(),
          end_time: endDateTime,
          location: form.value.location,
          max_participants: form.value.max_participants
        }

        console.log('Creating meetup with data:', meetupData)
        console.log('User auth status:', authStore.isLoggedIn)
        console.log('User data:', authStore.user)

        const response = await fetchWithCSRF('/api/meetups/', {
          method: 'POST',
          body: JSON.stringify(meetupData)
        })

        console.log('Response status:', response.status)
        console.log('Response headers:', response.headers)

        if (response.ok) {
          router.push('/settings?message=모임이 성공적으로 생성되었습니다')
        } else {
          const responseText = await response.text()
          console.error('Error response:', responseText)
          
          try {
            const data = JSON.parse(responseText)
            error.value = data.error || data.detail || '모임 생성에 실패했습니다'
          } catch {
            error.value = `서버 오류 (${response.status}): ${responseText || '모임 생성에 실패했습니다'}`
          }
        }
      } catch (err) {
        console.error('Network error:', err)
        error.value = '네트워크 오류가 발생했습니다. 다시 시도해주세요.'
      } finally {
        loading.value = false
      }
    }

    const logout = () => {
      authStore.logout()
      router.push('/login')
    }

    return {
      authStore,
      form,
      loading,
      error,
      handleSubmit,
      logout
    }
  }
}
</script>