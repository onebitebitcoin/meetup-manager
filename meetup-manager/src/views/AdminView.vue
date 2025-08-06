<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <nav class="bg-white dark:bg-gray-800 shadow">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <h1 class="text-xl font-semibold text-gray-900 dark:text-white">관리자 대시보드</h1>
          </div>
          <div class="flex items-center space-x-4">
            <ThemeToggle />
            <span class="text-gray-700 dark:text-gray-300">{{ authStore.user?.name }}</span>
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

    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <!-- Tab Navigation -->
      <div class="mb-6">
        <div class="border-b border-gray-200 dark:border-gray-700">
          <nav class="-mb-px flex space-x-8" aria-label="Tabs">
            <button
              @click="activeTab = 'users'"
              :class="[
                activeTab === 'users'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400',
                'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
              ]"
            >
              사용자 관리
            </button>
            <button
              @click="activeTab = 'meetups'"
              :class="[
                activeTab === 'meetups'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400',
                'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
              ]"
            >
              전체 모임
            </button>
            <button
              @click="activeTab = 'stats'"
              :class="[
                activeTab === 'stats'
                  ? 'border-indigo-500 text-indigo-600 dark:text-indigo-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 dark:text-gray-400',
                'whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm'
              ]"
            >
              통계
            </button>
          </nav>
        </div>
      </div>

      <!-- Users Tab -->
      <div v-if="activeTab === 'users'" class="px-4 py-6 sm:px-0">
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">사용자 관리</h2>
          
          <div v-if="loadingUsers" class="text-center py-8">
            <div class="text-gray-600 dark:text-gray-400">사용자 정보를 불러오는 중...</div>
          </div>
          
          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    사용자
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    연락처
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    권한
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    생성한 모임
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    가입일
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    액션
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="user in users" :key="user.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">{{ user.name }}</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">@{{ user.username }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900 dark:text-white">{{ user.email }}</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">{{ user.phone || '전화번호 없음' }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <span :class="[
                      user.is_admin
                        ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200'
                        : 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
                      'px-2 inline-flex text-xs leading-5 font-semibold rounded-full'
                    ]">
                      {{ user.is_admin ? '관리자' : '일반사용자' }}
                    </span>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {{ user.created_meetups_count || 0 }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                    {{ formatDate(user.created_at) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex justify-end space-x-2">
                      <button
                        @click="toggleUserAdmin(user.id)"
                        :class="[
                          user.is_admin 
                            ? 'text-orange-600 hover:text-orange-900 dark:text-orange-400'
                            : 'text-indigo-600 hover:text-indigo-900 dark:text-indigo-400'
                        ]"
                      >
                        {{ user.is_admin ? '관리자 해제' : '관리자 지정' }}
                      </button>
                      <button
                        @click="deleteUserAsAdmin(user.id)"
                        :disabled="user.is_admin"
                        :class="[
                          user.is_admin
                            ? 'text-gray-400 cursor-not-allowed'
                            : 'text-red-600 hover:text-red-900 dark:text-red-400'
                        ]"
                      >
                        삭제
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Meetups Tab -->
      <div v-if="activeTab === 'meetups'" class="px-4 py-6 sm:px-0">
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <div class="mb-6">
            <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">전체 모임</h2>
          </div>

          <div v-if="loadingMeetups" class="text-center py-8">
            <div class="text-gray-600 dark:text-gray-400">모임 정보를 불러오는 중...</div>
          </div>

          <div v-else class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
              <thead class="bg-gray-50 dark:bg-gray-700">
                <tr>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    모임
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    생성자
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    일시
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    장소
                  </th>
                  <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    참여자
                  </th>
                  <th class="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                    액션
                  </th>
                </tr>
              </thead>
              <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                <tr v-for="meetup in allMeetups" :key="meetup.id">
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm font-medium text-gray-900 dark:text-white">{{ meetup.name }}</div>
                    <div class="text-sm text-gray-500 dark:text-gray-400">{{ meetup.description }}</div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {{ meetup.creator_name || '생성자 없음' }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {{ formatDateTime(meetup.date_time) }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                    {{ meetup.location }}
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap">
                    <div class="text-sm text-gray-900 dark:text-white">
                      {{ meetup.current_participants }} / {{ meetup.max_participants }}
                    </div>
                    <div class="text-xs text-gray-500 dark:text-gray-400">
                      {{ meetup.available_spots }}석 남음
                    </div>
                  </td>
                  <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                    <div class="flex justify-end space-x-2">
                      <button
                        @click="deleteMeetupAsAdmin(meetup.id)"
                        class="text-red-600 hover:text-red-900 dark:text-red-400"
                      >
                        삭제
                      </button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Statistics Tab -->
      <div v-if="activeTab === 'stats'" class="px-4 py-6 sm:px-0">
        <div class="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white mb-6">플랫폼 통계</h2>
          
          <div v-if="loadingStats" class="text-center py-8">
            <div class="text-gray-600 dark:text-gray-400">통계를 불러오는 중...</div>
          </div>
          
          <div v-else class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Total Users -->
            <div class="bg-blue-50 dark:bg-blue-900 rounded-lg p-6">
              <div class="flex items-center">
                <div class="p-2 bg-blue-100 dark:bg-blue-800 rounded-lg">
                  <svg class="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"></path>
                  </svg>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600 dark:text-gray-400">총 사용자</p>
                  <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.total_users }}</p>
                </div>
              </div>
              <div class="mt-4">
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  이번 달 +{{ stats.recent_users }}명
                </div>
              </div>
            </div>

            <!-- Total Meetups -->
            <div class="bg-green-50 dark:bg-green-900 rounded-lg p-6">
              <div class="flex items-center">
                <div class="p-2 bg-green-100 dark:bg-green-800 rounded-lg">
                  <svg class="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600 dark:text-gray-400">총 모임</p>
                  <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.total_meetups }}</p>
                </div>
              </div>
              <div class="mt-4">
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  이번 달 +{{ stats.recent_meetups }}개
                </div>
              </div>
            </div>

            <!-- Total Registrations -->
            <div class="bg-purple-50 dark:bg-purple-900 rounded-lg p-6">
              <div class="flex items-center">
                <div class="p-2 bg-purple-100 dark:bg-purple-800 rounded-lg">
                  <svg class="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                  </svg>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600 dark:text-gray-400">총 참가 신청</p>
                  <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.total_registrations }}</p>
                </div>
              </div>
              <div class="mt-4">
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  이번 달 +{{ stats.recent_registrations }}건
                </div>
              </div>
            </div>

            <!-- Admin Users -->
            <div class="bg-orange-50 dark:bg-orange-900 rounded-lg p-6">
              <div class="flex items-center">
                <div class="p-2 bg-orange-100 dark:bg-orange-800 rounded-lg">
                  <svg class="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path>
                  </svg>
                </div>
                <div class="ml-4">
                  <p class="text-sm font-medium text-gray-600 dark:text-gray-400">관리자</p>
                  <p class="text-2xl font-semibold text-gray-900 dark:text-white">{{ stats.admin_users }}</p>
                </div>
              </div>
              <div class="mt-4">
                <div class="text-sm text-gray-600 dark:text-gray-400">
                  전체 사용자의 {{ Math.round((stats.admin_users / stats.total_users) * 100) }}%
                </div>
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
        const response = await fetch('/api/admin/users/', {
          credentials: 'include'
        })
        if (response.ok) {
          users.value = await response.json()
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
        const response = await fetch('/api/admin/meetups/', {
          credentials: 'include'
        })
        if (response.ok) {
          allMeetups.value = await response.json()
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
        const response = await fetch('/api/admin/statistics/', {
          credentials: 'include'
        })
        if (response.ok) {
          stats.value = await response.json()
        }
      } catch (error) {
        console.error('Failed to load statistics:', error)
      } finally {
        loadingStats.value = false
      }
    }

    const logout = async () => {
      try {
        await fetch('/api/auth/logout/', {
          method: 'POST',
          credentials: 'include'
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
          const response = await fetch(`/api/admin/meetups/${meetupId}/delete/`, {
            method: 'DELETE',
            credentials: 'include'
          })

          if (response.ok) {
            await loadAllMeetups()
          }
        } catch (error) {
          console.error('Failed to delete meetup:', error)
        }
      }
    }

    const deleteUserAsAdmin = async (userId) => {
      if (confirm('정말로 이 사용자를 삭제하시겠습니까?')) {
        try {
          const response = await fetch(`/api/admin/users/${userId}/delete/`, {
            method: 'DELETE',
            credentials: 'include'
          })

          if (response.ok) {
            await loadUsers()
          }
        } catch (error) {
          console.error('Failed to delete user:', error)
        }
      }
    }

    const toggleUserAdmin = async (userId) => {
      try {
        const response = await fetch(`/api/admin/users/${userId}/toggle-admin/`, {
          method: 'POST',
          credentials: 'include'
        })

        if (response.ok) {
          await loadUsers()
        }
      } catch (error) {
        console.error('Failed to toggle admin status:', error)
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