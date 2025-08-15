<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-3 sm:p-6">
      <div class="flex items-center justify-between mb-3 sm:mb-6">
        <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">목록</h2>
      </div>
      
      <!-- Centered year/month navigation -->
      <div class="flex items-center justify-center mb-3 sm:mb-6">
        <div class="flex items-center space-x-3 sm:space-x-6">
          <button
            @click="previousMonth"
            class="p-1 sm:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full text-gray-900 dark:text-white transition-colors"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
          </button>
          <h3 class="text-lg sm:text-xl font-bold text-gray-900 dark:text-white min-w-[140px] sm:min-w-[200px] text-center">
            {{ currentMonth.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' }) }}
          </h3>
          <button
            @click="nextMonth"
            class="p-1 sm:p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full text-gray-900 dark:text-white transition-colors"
          >
            <svg class="w-4 h-4 sm:w-5 sm:h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path>
            </svg>
          </button>
        </div>
      </div>
    
    <!-- Desktop table view -->
    <div class="hidden sm:block overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700">
          <tr>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              이미지
            </th>
            <th class="px-4 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              모임명
            </th>
            <th class="px-3 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
              생성자
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
          <tr v-for="meetup in filteredMeetups" :key="meetup.id" class="hover:bg-gray-50 dark:hover:bg-gray-700">
            <!-- 이미지 컬럼 -->
            <td class="px-4 py-4">
              <div class="relative w-16 h-12 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 flex-shrink-0">
                <img 
                  v-if="meetup.image_display_url" 
                  :src="meetup.image_display_url" 
                  :alt="meetup.name"
                  class="w-full h-full object-cover"
                  @error="handleImageError"
                />
                <div v-else class="w-full h-full flex items-center justify-center">
                  <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
                  </svg>
                </div>
              </div>
            </td>
            <!-- 모임명 컬럼 -->
            <td class="px-4 py-4">
              <div class="text-sm font-medium text-gray-900 dark:text-white">
                {{ meetup.name }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400 truncate max-w-[200px]" :title="meetup.description">
                {{ meetup.description }}
              </div>
              <div v-if="meetup.hashtags_list && meetup.hashtags_list.length > 0" class="flex flex-wrap gap-1 mt-1">
                <span v-for="hashtag in meetup.hashtags_list.slice(0, 2)" :key="hashtag" 
                      class="inline-flex px-1.5 py-0.5 text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded">
                  {{ hashtag }}
                </span>
                <span v-if="meetup.hashtags_list.length > 2" class="text-xs text-gray-400">+{{ meetup.hashtags_list.length - 2 }}</span>
              </div>
            </td>
            <td class="px-3 py-4">
              <div class="text-sm text-gray-900 dark:text-white">
                {{ meetup.creator_name }}
              </div>
              <div class="text-xs text-gray-500 dark:text-gray-400">
                {{ meetup.creator_email }}
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
                  v-if="!authStore.isGuest && !isRegistered(meetup.id) && canRegister(meetup)"
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

    <!-- Mobile list view -->
    <div class="sm:hidden space-y-3">
      <div
        v-for="meetup in filteredMeetups"
        :key="meetup.id"
        class="p-3 space-y-3 hover:bg-gray-50 dark:hover:bg-gray-700"
      >
        <div class="flex gap-3">
          <!-- 이미지 섹션 -->
          <div class="relative w-20 h-16 rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700 flex-shrink-0">
            <img 
              v-if="meetup.image_display_url" 
              :src="meetup.image_display_url" 
              :alt="meetup.name"
              class="w-full h-full object-cover"
              @error="handleImageError"
            />
            <div v-else class="w-full h-full flex items-center justify-center">
              <svg class="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
            </div>
          </div>
          
          <!-- 컨텐츠 섹션 -->
          <div class="flex-1 min-w-0 flex justify-between items-start">
            <div class="flex-1 min-w-0">
              <h3 class="text-sm font-medium text-gray-900 dark:text-white truncate">
                {{ meetup.name }}
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
                {{ meetup.description }}
              </p>
              <div v-if="meetup.hashtags_list && meetup.hashtags_list.length > 0" class="flex flex-wrap gap-1 mt-2">
                <span v-for="hashtag in meetup.hashtags_list.slice(0, 2)" :key="hashtag" 
                      class="inline-flex px-1.5 py-0.5 text-xs font-medium bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded">
                  {{ hashtag }}
                </span>
                <span v-if="meetup.hashtags_list.length > 2" class="text-xs text-gray-400">+{{ meetup.hashtags_list.length - 2 }}</span>
              </div>
            </div>
            <span 
              class="ml-2 inline-flex px-2 py-1 text-xs font-semibold rounded-full flex-shrink-0"
              :class="getStatusClass(meetup.date_time)"
            >
              {{ getStatus(meetup.date_time) }}
            </span>
          </div>
        </div>
        
        <div class="grid grid-cols-2 gap-3 text-xs">
          <div>
            <div class="text-gray-500 dark:text-gray-400">생성자</div>
            <div class="text-gray-900 dark:text-white font-medium">
              {{ meetup.creator_name }}
            </div>
            <div class="text-gray-500 dark:text-gray-400 text-xs truncate" :title="meetup.creator_email">
              {{ meetup.creator_email }}
            </div>
          </div>
          
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
          
          <div class="col-span-2">
            <div class="text-gray-500 dark:text-gray-400">날짜</div>
            <div class="text-gray-900 dark:text-white font-medium">
              {{ formatDate(meetup.date_time) }}
            </div>
          </div>
        </div>
        
        <div class="pt-2">
          <div class="flex space-x-2">
            <button
              @click="showMeetupDetail(meetup)"
              class="bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-xs flex-1"
            >
              상세보기
            </button>
            <button
              v-if="!authStore.isGuest && !isRegistered(meetup.id) && canRegister(meetup)"
              @click="registerForMeetup(meetup.id)"
              :disabled="registering"
              class="bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-xs disabled:opacity-50 flex-1"
            >
              참가 신청
            </button>
            <button
              v-if="!authStore.isGuest && isRegistered(meetup.id)"
              @click="unregisterFromMeetup(meetup.id)"
              :disabled="registering"
              class="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs disabled:opacity-50 flex-1"
            >
              참가 취소
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Empty state - only show when no data -->
    <div v-if="filteredMeetups.length === 0" class="text-center py-12">
      <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
      </svg>
      <h3 class="mt-2 text-sm font-medium text-gray-900 dark:text-white">{{ currentMonth.toLocaleDateString('ko-KR', { year: 'numeric', month: 'long' }) }}에 등록된 모임이 없습니다</h3>
      <p class="mt-1 text-sm text-gray-500 dark:text-gray-400">다른 월을 선택하거나 관리자에게 문의하여 새로운 모임을 등록해 보세요.</p>
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
import { computed, ref, onMounted } from 'vue'
import { useMeetupsStore } from '@/stores/meetups'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'
import MeetupDetailModal from './MeetupDetailModal.vue'

export default {
  name: 'MeetupTable',
  components: {
    MeetupDetailModal
  },
  props: {
    meetups: {
      type: Array,
      default: () => []
    }
  },
  setup(props) {
    const meetupsStore = useMeetupsStore()
    const authStore = useAuthStore()
    const selectedMeetup = ref(null)
    const registering = ref(false)
    const userRegistrations = ref(new Set())
    const currentMonth = ref(new Date())

    const sortedMeetups = computed(() => {
      return [...props.meetups].sort((a, b) => new Date(a.date_time) - new Date(b.date_time))
    })

    // Filter meetups by current selected month
    const filteredMeetups = computed(() => {
      const year = currentMonth.value.getFullYear()
      const month = currentMonth.value.getMonth()
      
      return sortedMeetups.value.filter(meetup => {
        const meetupDate = new Date(meetup.date_time)
        return meetupDate.getFullYear() === year && meetupDate.getMonth() === month
      })
    })

    const previousMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1)
    }

    const nextMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1)
    }

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

    const handleImageError = (event) => {
      // Hide broken image and show placeholder
      event.target.style.display = 'none'
    }

    const showMeetupDetail = (meetup) => {
      selectedMeetup.value = meetup
    }

    const canRegister = (meetup) => {
      const now = new Date()
      const meetupDate = new Date(meetup.date_time)
      // 오늘 날짜 이전(과거) 또는 오늘 23:59:59까지는 비활성화
      const end = meetup.end_time ? new Date(meetup.end_time) : meetupDate
      // 오늘 날짜의 23:59:59까지는 신청 가능, 그 이후는 불가
      const today = new Date(now.getFullYear(), now.getMonth(), now.getDate(), 23, 59, 59, 999)
      if (end <= today) return false
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
      
      for (const meetup of props.meetups) {
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


    // Check registration status on mount (first load)
    onMounted(() => {
      checkRegistrationStatus()
    })

    // Also check when meetups are loaded/refreshed
    computed(() => {
      if (props.meetups.length > 0) {
        checkRegistrationStatus()
      }
      return props.meetups
    })

    // Handle meetup updates from modal
    const onMeetupUpdated = async () => {
      // Update selected meetup with latest data
      if (selectedMeetup.value) {
        const updatedMeetup = props.meetups.find(m => m.id === selectedMeetup.value.id)
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
      filteredMeetups,
      currentMonth,
      previousMonth,
      nextMonth,
      registering,
      formatDate,
      formatTime,
      formatDateTime,
      handleImageError,
      getStatus,
      getStatusClass,
      showMeetupDetail,
      canRegister,
      isRegistered,
      registerForMeetup,
      unregisterFromMeetup,
      onMeetupUpdated,
      meetups: props.meetups
    }
  }
}
</script>