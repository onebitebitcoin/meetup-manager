<template>
  <div class="min-h-screen bg-neutral-50 dark:bg-neutral-950 transition-colors duration-200">
    <!-- Header -->
    <header class="bg-beige-200 dark:bg-neutral-900 border-b border-beige-300 dark:border-neutral-800 transition-colors duration-200">
      <div class="container mx-auto px-4 py-3">
        <div class="flex justify-between items-center">
          <!-- Left side -->
          <div class="flex items-center space-x-2 sm:space-x-4">
            <button
              @click="$router.push('/')"
              class="p-2 text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 hover:bg-blue-50 dark:hover:bg-blue-900/20 rounded-lg transition-colors duration-200"
              title="홈으로 돌아가기"
            >
              <span class="text-lg sm:text-xl">←</span>
            </button>
            <div class="flex items-center space-x-2">
              <img
                src="/icons/logo-transparent.svg"
                alt="한입 모임 로고"
                class="h-8 w-8"
              />
              <h1 class="text-lg sm:text-2xl font-bold text-neutral-800 dark:text-neutral-100">
                <span class="hidden sm:inline">관리자 패널</span>
                <span class="sm:hidden">관리자</span>
              </h1>
            </div>
          </div>
          
          <!-- Right side -->
          <div class="flex items-center space-x-2">
            <ThemeToggle />
            
            <!-- User info - responsive -->
            <div class="flex items-center space-x-1 sm:space-x-2">
              <span class="text-sm sm:text-base text-gray-600 dark:text-gray-300">
                <span class="hidden sm:inline">{{ authStore.user?.name }}님</span>
                <span class="sm:hidden">{{ authStore.user?.name }}</span>
              </span>
            </div>
            
            <button
              @click="logout"
              class="bg-red-600 hover:bg-red-700 text-white px-2 py-2 sm:px-4 rounded-md text-sm font-medium transition-colors"
            >
              <span class="hidden sm:inline">로그아웃</span>
              <span class="sm:hidden">↪</span>
            </button>
          </div>
        </div>
      </div>
    </header>

    <div class="container mx-auto px-4 py-4 md:py-8 max-w-7xl">
      
      <!-- Statistics Cards -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow transition-colors duration-200">
          <div class="flex items-center">
            <div class="p-2 bg-blue-100 dark:bg-blue-900 rounded-lg">
              <svg class="w-4 h-4 sm:w-6 sm:h-6 text-blue-600 dark:text-blue-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
              </svg>
            </div>
            <div class="ml-2 sm:ml-4">
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400">총 사용자</p>
              <p class="text-lg sm:text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total_users || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow transition-colors duration-200">
          <div class="flex items-center">
            <div class="p-2 bg-green-100 dark:bg-green-900 rounded-lg">
              <svg class="w-4 h-4 sm:w-6 sm:h-6 text-green-600 dark:text-green-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
              </svg>
            </div>
            <div class="ml-2 sm:ml-4">
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400">총 모임</p>
              <p class="text-lg sm:text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total_meetups || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow transition-colors duration-200">
          <div class="flex items-center">
            <div class="p-2 bg-purple-100 dark:bg-purple-900 rounded-lg">
              <svg class="w-4 h-4 sm:w-6 sm:h-6 text-purple-600 dark:text-purple-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"></path>
              </svg>
            </div>
            <div class="ml-2 sm:ml-4">
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400">총 신청</p>
              <p class="text-lg sm:text-2xl font-bold text-gray-900 dark:text-white">{{ stats.total_registrations || 0 }}</p>
            </div>
          </div>
        </div>

        <div class="bg-white dark:bg-gray-800 rounded-xl p-4 shadow transition-colors duration-200">
          <div class="flex items-center">
            <div class="p-2 bg-red-100 dark:bg-red-900 rounded-lg">
              <svg class="w-4 h-4 sm:w-6 sm:h-6 text-red-600 dark:text-red-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path>
              </svg>
            </div>
            <div class="ml-2 sm:ml-4">
              <p class="text-xs sm:text-sm text-gray-600 dark:text-gray-400">관리자</p>
              <p class="text-lg sm:text-2xl font-bold text-gray-900 dark:text-white">{{ stats.admin_users || 0 }}</p>
            </div>
          </div>
        </div>
      </div>
      
      <!-- Tab Navigation -->
      <div class="mb-6">
        <div class="border-b border-gray-200 dark:border-gray-700">
          <nav class="-mb-px flex space-x-4 sm:space-x-8" aria-label="Tabs">
            <button
              @click="activeTab = 'users'"
              :class="[
                activeTab === 'users'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400',
                'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm sm:text-base'
              ]"
            >
              <span class="hidden sm:inline">사용자 관리</span>
              <span class="sm:hidden">사용자</span>
            </button>
            <button
              @click="activeTab = 'meetups'"
              :class="[
                activeTab === 'meetups'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400',
                'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm sm:text-base'
              ]"
            >
              <span class="hidden sm:inline">전체 모임</span>
              <span class="sm:hidden">모임</span>
            </button>
          </nav>
        </div>
      </div>

      <!-- Users Tab -->
      <div v-if="activeTab === 'users'" class="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden transition-colors duration-200">
        <div class="p-4 md:p-6 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h2 class="text-lg md:text-xl font-semibold text-gray-800 dark:text-white">
              사용자 목록
            </h2>
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                총 {{ users.length }}명
              </span>
              <button
                @click="loadUsers"
                :disabled="loadingUsers"
                class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 p-1.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                title="새로고침"
              >
                🔄
              </button>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loadingUsers" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-2"></div>
          <p class="text-gray-500 dark:text-gray-400">사용자 목록을 불러오는 중...</p>
        </div>

        <!-- Users Cards -->
        <div v-else class="p-4 space-y-4">
          <div
            v-for="user in users"
            :key="user.id"
            class="bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 p-4 hover:shadow-md transition-all duration-200"
          >
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <!-- User Info -->
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ user.name }}
                  </h3>
                  <span v-if="user.is_admin" class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-300">
                    관리자
                  </span>
                </div>
                
                <div class="space-y-1 text-sm text-gray-600 dark:text-gray-300">
                  <div class="flex items-start gap-2">
                    <span class="font-medium min-w-0 flex-shrink-0">사용자명:</span>
                    <span>{{ user.username }}</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="font-medium min-w-0 flex-shrink-0">이메일:</span>
                    <span class="break-all">{{ user.email }}</span>
                  </div>
                  <div v-if="user.phone" class="flex items-start gap-2">
                    <span class="font-medium min-w-0 flex-shrink-0">전화:</span>
                    <span>{{ user.phone }}</span>
                  </div>
                  
                  <div class="flex items-center gap-4 mt-2">
                    <div class="flex items-center gap-2">
                      <span class="font-medium">생성한 모임:</span>
                      <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                        {{ user.created_meetups_count || 0 }}개
                      </span>
                    </div>
                    <div class="flex items-center gap-2">
                      <span class="font-medium">가입:</span>
                      <span>{{ formatDate(user.created_at) }}</span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Action Buttons -->
              <div class="flex items-center gap-2 sm:flex-col sm:gap-1">
                <button
                  @click="toggleUserAdmin(user.id)"
                  class="flex items-center justify-center px-3 py-2 text-sm font-medium rounded-lg transition-colors"
                  :class="[
                    user.is_admin 
                      ? 'text-orange-600 dark:text-orange-400 bg-orange-50 dark:bg-orange-900/20 hover:bg-orange-100 dark:hover:bg-orange-900/40'
                      : 'text-indigo-600 dark:text-indigo-400 bg-indigo-50 dark:bg-indigo-900/20 hover:bg-indigo-100 dark:hover:bg-indigo-900/40'
                  ]"
                >
                  <span class="mr-1">{{ user.is_admin ? '⬇️' : '⬆️' }}</span>
                  <span class="hidden sm:inline">{{ user.is_admin ? '일반화' : '관리자화' }}</span>
                </button>
                <button
                  @click="deleteUserAsAdmin(user.id)"
                  :disabled="user.is_admin"
                  class="flex items-center justify-center px-3 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <span class="mr-1">🗑️</span>
                  <span class="hidden sm:inline">삭제</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Meetups Tab -->
      <div v-if="activeTab === 'meetups'" class="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden transition-colors duration-200">
        <div class="p-4 md:p-6 border-b border-gray-200 dark:border-gray-700">
          <div class="flex items-center justify-between">
            <h2 class="text-lg md:text-xl font-semibold text-gray-800 dark:text-white">
              모임 목록
            </h2>
            <div class="flex items-center space-x-4">
              <span class="text-sm text-gray-600 dark:text-gray-400">
                총 {{ allMeetups.length }}개
              </span>
              <button
                @click="loadAllMeetups"
                :disabled="loadingMeetups"
                class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 p-1.5 rounded-lg hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
                title="새로고침"
              >
                🔄
              </button>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loadingMeetups" class="p-8 text-center">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-2"></div>
          <p class="text-gray-500 dark:text-gray-400">모임 목록을 불러오는 중...</p>
        </div>

        <!-- Meetups Cards -->
        <div v-else class="p-4 space-y-4">
          <div
            v-for="meetup in allMeetups"
            :key="meetup.id"
            class="bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 p-4 hover:shadow-md transition-all duration-200"
          >
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <!-- Meetup Info -->
              <div class="flex-1">
                <div class="flex items-center gap-2 mb-2">
                  <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
                    {{ meetup.name }}
                  </h3>
                  <span :class="[
                    'inline-flex items-center px-2 py-1 rounded-full text-xs',
                    meetup.is_full
                      ? 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300'
                      : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300'
                  ]">
                    {{ meetup.is_full ? '마감' : '모집중' }}
                  </span>
                </div>
                
                <div class="space-y-1 text-sm text-gray-600 dark:text-gray-300 mb-3">
                  <div class="flex items-start gap-2">
                    <span class="font-medium min-w-0 flex-shrink-0">생성자:</span>
                    <span>{{ meetup.creator_name || '생성자 없음' }}</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="font-medium min-w-0 flex-shrink-0">일시:</span>
                    <span>{{ formatDateTime(meetup.date_time) }}</span>
                  </div>
                  <div class="flex items-start gap-2">
                    <span class="font-medium min-w-0 flex-shrink-0">장소:</span>
                    <span>{{ meetup.location }}</span>
                  </div>
                  <div class="flex items-center gap-2">
                    <span class="font-medium">참가자:</span>
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300">
                      {{ meetup.current_participants }}/{{ meetup.max_participants }}명
                    </span>
                  </div>
                </div>
                
                <div v-if="meetup.description" class="text-sm text-gray-600 dark:text-gray-300 line-clamp-2">
                  {{ meetup.description }}
                </div>
              </div>

              <!-- Action Button -->
              <div class="sm:flex-shrink-0">
                <button
                  @click="deleteMeetupAsAdmin(meetup.id)"
                  class="w-full sm:w-auto px-4 py-2 text-sm font-medium text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 hover:bg-red-100 dark:hover:bg-red-900/40 rounded-lg transition-colors"
                >
                  🗑️ <span class="ml-1">삭제</span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'
import ThemeToggle from '@/components/ThemeToggle.vue'

export default {
  name: 'AdminView',
  components: {
    ThemeToggle
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    
    const activeTab = ref('users')
    const users = ref([])
    const allMeetups = ref([])
    const stats = ref({})
    const loadingUsers = ref(false)
    const loadingMeetups = ref(false)
    const loadingStats = ref(false)

    onMounted(() => {
      loadUsers()
      loadAllMeetups()
      loadStats()
    })

    const loadUsers = async () => {
      loadingUsers.value = true
      try {
        const response = await fetchWithCSRF('/api/admin/users/')
        if (response.ok) {
          users.value = await response.json()
        } else {
          console.error('Failed to load users')
        }
      } catch (error) {
        console.error('Failed to load users:', error)
      } finally {
        loadingUsers.value = false
      }
    }

    const loadAllMeetups = async () => {
      loadingMeetups.value = true
      try {
        const response = await fetchWithCSRF('/api/admin/meetups/')
        if (response.ok) {
          allMeetups.value = await response.json()
        } else {
          console.error('Failed to load meetups')
        }
      } catch (error) {
        console.error('Failed to load meetups:', error)
      } finally {
        loadingMeetups.value = false
      }
    }

    const loadStats = async () => {
      loadingStats.value = true
      try {
        const response = await fetchWithCSRF('/api/admin/statistics/')
        if (response.ok) {
          stats.value = await response.json()
        } else {
          console.error('Failed to load statistics')
        }
      } catch (error) {
        console.error('Failed to load statistics:', error)
      } finally {
        loadingStats.value = false
      }
    }

    const logout = async () => {
      try {
        await fetchWithCSRF('/api/auth/logout/', {
          method: 'POST'
        })
        authStore.logout()
        router.push('/login')
      } catch (error) {
        console.error('Logout failed:', error)
        authStore.logout()
        router.push('/login')
      }
    }

    const deleteMeetupAsAdmin = async (meetupId) => {
      if (confirm('정말로 이 모임을 삭제하시겠습니까?')) {
        try {
          const response = await fetchWithCSRF(`/api/admin/meetups/${meetupId}/delete/`, {
            method: 'DELETE'
          })

          if (response.ok) {
            const result = await response.json()
            alert(result.message || '모임이 삭제되었습니다')
            await loadAllMeetups()
            await loadStats()
          } else {
            const error = await response.json()
            alert(error.error || '삭제 실패')
          }
        } catch (error) {
          console.error('Failed to delete meetup:', error)
          alert('삭제 중 오류가 발생했습니다')
        }
      }
    }

    const deleteUserAsAdmin = async (userId) => {
      if (confirm('정말로 이 사용자를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
        try {
          const response = await fetchWithCSRF(`/api/admin/users/${userId}/delete/`, {
            method: 'DELETE'
          })

          if (response.ok) {
            const result = await response.json()
            alert(result.message || '사용자가 삭제되었습니다')
            await loadUsers()
            await loadStats()
          } else {
            const error = await response.json()
            alert(error.error || '삭제 실패')
          }
        } catch (error) {
          console.error('Failed to delete user:', error)
          alert('삭제 중 오류가 발생했습니다')
        }
      }
    }

    const toggleUserAdmin = async (userId) => {
      try {
        const response = await fetchWithCSRF(`/api/admin/users/${userId}/toggle-admin/`, {
          method: 'POST'
        })

        if (response.ok) {
          const result = await response.json()
          alert(result.message || '권한이 변경되었습니다')
          await loadUsers()
          await loadStats()
        } else {
          const error = await response.json()
          alert(error.error || '권한 변경 실패')
        }
      } catch (error) {
        console.error('Failed to toggle admin status:', error)
        alert('권한 변경 중 오류가 발생했습니다')
      }
    }

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString()
    }

    const formatDateTime = (dateTimeStr) => {
      const date = new Date(dateTimeStr)
      return date.toLocaleString()
    }

    return {
      authStore,
      activeTab,
      users,
      allMeetups,
      stats,
      loadingUsers,
      loadingMeetups,
      loadingStats,
      logout,
      deleteMeetupAsAdmin,
      deleteUserAsAdmin,
      toggleUserAdmin,
      formatDate,
      formatDateTime
    }
  }
}
</script>
