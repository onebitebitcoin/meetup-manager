<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow">
    <div class="px-4 sm:px-6 py-4 border-b border-gray-200 dark:border-gray-700">
      <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">모임 목록</h2>
    </div>
    
    <!-- Desktop table view -->
    <div class="hidden sm:block overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              모임명
            </th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              인원
            </th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              시간
            </th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              장소
            </th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              상태
            </th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              액션
            </th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-for="meetup in sortedMeetups" :key="meetup.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
            <td class="px-4 py-4">
              <div class="text-sm font-medium text-gray-900 dark:text-white">
                {{ meetup.name }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[200px]" :title="meetup.description">
                {{ meetup.description }}
              </div>
            </td>
            <td class="px-3 py-4">
              <div class="text-sm text-gray-900 dark:text-white">
                {{ meetup.current_participants }}/{{ meetup.max_participants }}
              </div>
              <div v-if="meetup.is_full" class="text-xs text-red-600 font-semibold">
                마감
              </div>
            </td>
            <td class="px-3 py-4">
              <div class="text-sm text-gray-900 dark:text-white">
                {{ formatDate(meetup.date_time) }}
              </div>
              <div class="text-xs text-gray-500">
                {{ formatTime(meetup.date_time) }}
              </div>
            </td>
            <td class="px-3 py-4">
              <div class="text-sm text-gray-900 dark:text-white truncate max-w-[120px]" :title="meetup.location">
                {{ meetup.location }}
              </div>
            </td>
            <td class="px-3 py-4">
              <span 
                class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                :class="getStatusClass(meetup.date_time)"
              >
                {{ getStatus(meetup.date_time) }}
              </span>
            </td>
            <td class="px-3 py-4">
              <div class="flex space-x-1">
                <button
                  @click="showMeetupDetail(meetup)"
                  class="bg-blue-600 hover:bg-blue-700 text-white px-2 py-1 rounded text-xs"
                >
                  상세
                </button>
                <button
                  v-if="!authStore.isGuest && canRegister(meetup)"
                  @click="registerForMeetup(meetup.id)"
                  :disabled="registering"
                  class="bg-green-600 hover:bg-green-700 text-white px-2 py-1 rounded text-xs disabled:opacity-50"
                >
                  신청
                </button>
                <button
                  v-if="!authStore.isGuest && isRegistered(meetup.id)"
                  @click="unregisterFromMeetup(meetup.id)"
                  :disabled="registering"
                  class="bg-red-600 hover:bg-red-700 text-white px-2 py-1 rounded text-xs disabled:opacity-50"
                >
                  취소
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Mobile card view -->
    <div class="sm:hidden space-y-3 p-4">
      <div
        v-for="meetup in sortedMeetups"
        :key="meetup.id"
        class="border border-gray-200 dark:border-gray-700 rounded-lg p-4 space-y-3 hover:bg-gray-50 dark:hover:bg-gray-700"
      >
        <div class="flex justify-between items-start">
          <div class="flex-1 min-w-0">
            <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
              {{ meetup.name }}
            </h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
              {{ meetup.description }}
            </p>
          </div>
          <span 
            class="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full flex-shrink-0"
            :class="getStatusClass(meetup.date_time)"
          >
            {{ getStatus(meetup.date_time) }}
          </span>
        </div>
        
        <div class="grid grid-cols-2 gap-3 text-xs">
          <div>
            <div class="text-gray-500 dark:text-gray-400">참여 인원</div>
            <div class="text-gray-900 dark:text-white font-medium">
              {{ meetup.current_participants }}/{{ meetup.max_participants }}명
              <span v-if="meetup.is_full" class="text-red-600 ml-1">(마감)</span>
            </div>
          </div>
          
          <div>
            <div class="text-gray-500 dark:text-gray-400">시간</div>
            <div class="text-gray-900 dark:text-white font-medium">
              {{ formatTime(meetup.date_time) }}
            </div>
          </div>
          
          <div>
            <div class="text-gray-500 dark:text-gray-400">장소</div>
            <div class="text-gray-900 dark:text-white font-medium truncate" :title="meetup.location">
              {{ meetup.location }}
            </div>
          </div>
          
          <div>
            <div class="text-gray-500 dark:text-gray-400">날짜</div>
            <div class="text-gray-900 dark:text-white font-medium">
              {{ formatDate(meetup.date_time) }}
            </div>
          </div>
        </div>
        
        <div class="pt-2 border-t border-gray-200 dark:border-gray-700">
          <div class="flex justify-between items-center mb-2">
            <span class="text-xs text-gray-500 dark:text-gray-400">
              생성자: {{ meetup.creator_name }}
            </span>
          </div>
          <div class="flex space-x-2">
            <button
              @click="showMeetupDetail(meetup)"
              class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs flex-1"
            >
              상세보기
            </button>
            <button
              v-if="!authStore.isGuest && canRegister(meetup)"
              @click="registerForMeetup(meetup.id)"
              :disabled="registering"
              class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs disabled:opacity-50 flex-1"
            >
              신청
            </button>
            <button
              v-if="!authStore.isGuest && isRegistered(meetup.id)"
              @click="unregisterFromMeetup(meetup.id)"
              :disabled="registering"
              class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs disabled:opacity-50 flex-1"
            >
              취소
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty state - only show when no data -->
    <div v-if="meetupsStore.meetups.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900">등록된 모임이 없습니다</h3>
      <p class="mt-1 text-sm text-gray-500">관리자에게 문의하여 새로운 모임을 등록해 보세요.</p>
    </div>

    <!-- 모임 상세 모달 -->
    <MeetupDetailModal 
      :selectedMeetup="selectedMeetup" 
      @close="selectedMeetup = null"
      @meetupUpdated="onMeetupUpdated"
    />
  </div>
</template>

<script>
import { computed, ref } from 'vue'
import { useMeetupsStore } from '@/stores/meetups'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'
import MeetupDetailModal from './MeetupDetailModal.vue'

export default {
  name: 'MeetupTable',
  components: {
    MeetupDetailModal
  },
  setup() {
    const meetupsStore = useMeetupsStore()
    const authStore = useAuthStore()
    const selectedMeetup = ref(null)
    const registering = ref(false)
    const userRegistrations = ref(new Set())

    const sortedMeetups = computed(() => {
      return [...meetupsStore.meetups].sort((a, b) => new Date(a.date_time) - new Date(b.date_time))
    })

    const formatDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        weekday: 'short'
      })
    }

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const getStatus = (dateString) => {
      const meetupDate = new Date(dateString)
      const now = new Date()
      const diffHours = (meetupDate - now) / (1000 * 60 * 60)

      if (diffHours < 0) {
        return '종료'
      } else if (diffHours < 24) {
        return '임박'
      } else if (diffHours < 72) {
        return '예정'
      } else {
        return '모집중'
      }
    }

    const getStatusClass = (dateString) => {
      const status = getStatus(dateString)
      const classes = {
        '종료': 'bg-gray-100 text-gray-800',
        '임박': 'bg-red-100 text-red-800',
        '예정': 'bg-yellow-100 text-yellow-800',
        '모집중': 'bg-green-100 text-green-800'
      }
      return classes[status] || 'bg-gray-100 text-gray-800'
    }

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('ko-KR')
    }

    const showMeetupDetail = (meetup) => {
      selectedMeetup.value = meetup
    }

    const canRegister = (meetup) => {
      const now = new Date()
      const meetupDate = new Date(meetup.date_time)
      return meetupDate > now && !meetup.is_full && !isRegistered(meetup.id)
    }

    const isRegistered = (meetupId) => {
      return userRegistrations.value.has(meetupId)
    }

    const registerForMeetup = async (meetupId) => {
      if (registering.value) return
      
      registering.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId}/register/`, {
          method: 'POST'
        })
        
        if (response.ok) {
          userRegistrations.value.add(meetupId)
          await meetupsStore.fetchMeetups() // Refresh meetups data
          alert('모임 신청이 완료되었습니다!')
        } else {
          const data = await response.json()
          alert(data.error || '신청에 실패했습니다.')
        }
      } catch (error) {
        alert('네트워크 오류가 발생했습니다.')
      } finally {
        registering.value = false
      }
    }

    const unregisterFromMeetup = async (meetupId) => {
      if (registering.value) return
      
      registering.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId}/unregister/`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          userRegistrations.value.delete(meetupId)
          await meetupsStore.fetchMeetups() // Refresh meetups data
          alert('모임 신청이 취소되었습니다.')
        } else {
          const data = await response.json()
          alert(data.error || '취소에 실패했습니다.')
        }
      } catch (error) {
        alert('네트워크 오류가 발생했습니다.')
      } finally {
        registering.value = false
      }
    }

    // Check registration status for all meetups on component mount
    const checkRegistrationStatus = async () => {
      if (!authStore.isLoggedIn || authStore.isGuest) return
      
      for (const meetup of meetupsStore.meetups) {
        try {
          const response = await fetchWithCSRF(`/api/meetups/${meetup.id}/status/`, {
            method: 'GET'
          })
          
          if (response.ok) {
            const data = await response.json()
            if (data.is_registered) {
              userRegistrations.value.add(meetup.id)
            }
          }
        } catch (error) {
          console.error('Failed to check registration status for meetup', meetup.id)
        }
      }
    }

    // Check registration status when meetups are loaded
    computed(() => {
      if (meetupsStore.meetups.length > 0) {
        checkRegistrationStatus()
      }
      return meetupsStore.meetups
    })

    // Handle meetup updates from modal
    const onMeetupUpdated = async () => {
      // Update selected meetup with latest data
      if (selectedMeetup.value) {
        const updatedMeetup = meetupsStore.meetups.find(m => m.id === selectedMeetup.value.id)
        if (updatedMeetup) {
          selectedMeetup.value = updatedMeetup
        }
      }
      
      // Refresh registration status to sync with backend changes
      await checkRegistrationStatus()
    }


    return {
      meetupsStore,
      authStore,
      selectedMeetup,
      sortedMeetups,
      registering,
      formatDate,
      formatTime,
      formatDateTime,
      getStatus,
      getStatusClass,
      showMeetupDetail,
      canRegister,
      isRegistered,
      registerForMeetup,
      unregisterFromMeetup,
      onMeetupUpdated
    }
  }
}
</script>