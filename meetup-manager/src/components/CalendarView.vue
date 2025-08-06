<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow p-3 sm:p-6">
    <div class="flex items-center justify-between mb-3 sm:mb-6">
      <h2 class="text-lg sm:text-xl font-semibold text-gray-900 dark:text-white">모임 달력</h2>
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

    <div class="grid grid-cols-7 gap-px sm:gap-1 mb-2 sm:mb-4">
      <div v-for="day in weekDays" :key="day" class="p-1 sm:p-2 text-center text-xs sm:text-sm font-medium text-gray-700 dark:text-gray-300">
        {{ day }}
      </div>
    </div>

    <div class="grid grid-cols-7 gap-px sm:gap-1">
      <div
        v-for="date in calendarDates"
        :key="date.date"
        class="relative p-1 sm:p-2 h-14 sm:min-h-[80px] border border-gray-200 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700"
        :class="{
          'bg-gray-100 dark:bg-gray-700': !date.isCurrentMonth,
          'bg-blue-50 dark:bg-blue-900': date.isToday
        }"
      >
        <div class="text-xs sm:text-sm font-medium" :class="{ 'text-gray-400 dark:text-gray-500': !date.isCurrentMonth, 'text-gray-900 dark:text-white': date.isCurrentMonth }">
          {{ date.date.getDate() }}
        </div>
        
        <div v-if="date.meetups.length > 0" class="mt-0.5 sm:mt-1 space-y-0.5 sm:space-y-1">
          <div
            v-for="meetup in date.meetups.slice(0, 1)"
            :key="meetup.id"
            @click="selectedMeetup = meetup"
            class="text-xs bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 px-1 sm:px-2 py-0.5 sm:py-1 rounded cursor-pointer hover:bg-indigo-200 dark:hover:bg-indigo-800 truncate block sm:hidden"
          >
            {{ meetup.name.length > 6 ? meetup.name.substring(0, 6) + '...' : meetup.name }}
          </div>
          <div
            v-for="meetup in date.meetups.slice(0, 2)"
            :key="meetup.id"
            @click="selectedMeetup = meetup"
            class="text-xs bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 px-1 sm:px-2 py-0.5 sm:py-1 rounded cursor-pointer hover:bg-indigo-200 dark:hover:bg-indigo-800 truncate hidden sm:block"
          >
            {{ meetup.name }}
          </div>
          <div 
            v-if="date.meetups.length > 1" 
            @click="showDateMeetups(date)"
            class="text-xs text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300 px-1 sm:px-2 py-0.5 sm:py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 sm:hidden"
          >
            +{{ date.meetups.length - 1 }}개
          </div>
          <div 
            v-if="date.meetups.length > 2" 
            @click="showDateMeetups(date)"
            class="text-xs text-gray-500 dark:text-gray-400 cursor-pointer hover:text-gray-700 dark:hover:text-gray-300 px-1 sm:px-2 py-0.5 sm:py-1 rounded hover:bg-gray-100 dark:hover:bg-gray-700 hidden sm:block"
          >
            +{{ date.meetups.length - 2 }}개 더
          </div>
        </div>
      </div>
    </div>

    <!-- 날짜별 모임 목록 모달 -->
    <div v-if="selectedDateMeetups" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click="selectedDateMeetups = null">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-lg w-full max-h-[90vh] overflow-y-auto" @click.stop>
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">
            {{ selectedDateMeetups.date.toLocaleDateString('ko-KR', { month: 'long', day: 'numeric' }) }} 모임 목록
          </h3>
          <button @click="selectedDateMeetups = null" class="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="space-y-3">
          <div 
            v-for="meetup in selectedDateMeetups.meetups" 
            :key="meetup.id"
            @click="selectMeetupFromDate(meetup)"
            class="p-4 border border-gray-200 dark:border-gray-600 rounded-lg cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            <div class="flex justify-between items-start mb-2">
              <h4 class="font-medium text-gray-900 dark:text-white">{{ meetup.name }}</h4>
              <span 
                class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                :class="getStatusClass(meetup.date_time)"
              >
                {{ getStatus(meetup.date_time) }}
              </span>
            </div>
            <div class="text-sm text-gray-600 dark:text-gray-400 space-y-1">
              <div>
                <span class="font-medium">시간:</span> 
                {{ formatTime(meetup.date_time) }}
                <span v-if="meetup.end_time"> - {{ formatTime(meetup.end_time) }}</span>
              </div>
              <div><span class="font-medium">장소:</span> {{ meetup.location }}</div>
              <div><span class="font-medium">참여:</span> {{ meetup.current_participants }} / {{ meetup.max_participants }}명</div>
              <div class="text-xs text-gray-500 dark:text-gray-400 truncate">{{ meetup.description }}</div>
            </div>
          </div>
        </div>
        <div class="mt-6 flex justify-end">
          <button
            @click="selectedDateMeetups = null"
            class="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-md text-sm font-medium"
          >
            닫기
          </button>
        </div>
      </div>
    </div>

    <!-- 모임 상세 모달 -->
    <div v-if="selectedMeetup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click="selectedMeetup = null">
      <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full max-h-[90vh] overflow-y-auto" @click.stop>
        <div class="flex justify-between items-start mb-4">
          <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ selectedMeetup.name }}</h3>
          <button @click="selectedMeetup = null" class="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
            </svg>
          </button>
        </div>
        <div class="space-y-3">
          <div>
            <span class="font-medium text-gray-700 dark:text-gray-300">시간:</span>
            <span class="ml-2 text-gray-600 dark:text-gray-400">
              {{ formatDateTime(selectedMeetup.date_time) }}
              <span v-if="selectedMeetup.end_time"> - {{ formatTime(selectedMeetup.end_time) }}</span>
            </span>
          </div>
          <div>
            <span class="font-medium text-gray-700 dark:text-gray-300">장소:</span>
            <span class="ml-2 text-gray-600 dark:text-gray-400">{{ selectedMeetup.location }}</span>
          </div>
          <div>
            <div class="flex items-center justify-between">
              <span class="font-medium text-gray-700 dark:text-gray-300">참여 현황:</span>
              <button
                @click="refreshMeetupData"
                :disabled="refreshing"
                class="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50"
                title="참여 현황 새로고침"
              >
                <svg 
                  :class="['w-4 h-4', { 'animate-spin': refreshing }]" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"></path>
                </svg>
              </button>
            </div>
          </div>
          <div>
            <span class="font-medium text-gray-700 dark:text-gray-300">생성자:</span>
            <span class="ml-2 text-gray-600 dark:text-gray-400">{{ selectedMeetup.creator_name }}</span>
          </div>
          <div>
            <span class="font-medium text-gray-700 dark:text-gray-300">상세 정보:</span>
            <p class="mt-1 text-gray-600 dark:text-gray-400">{{ selectedMeetup.description }}</p>
          </div>
          
          <!-- 빈 자리 표시 -->
          <div v-if="!currentMeetupData.is_full" class="border-t pt-3">
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-gray-700 dark:text-gray-300">남은 자리</span>
              <span class="text-xs bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded-full">
                {{ currentMeetupData.available_spots }}석 남음
              </span>
            </div>
            <div class="grid grid-cols-5 gap-1">
              <div 
                v-for="n in currentMeetupData.available_spots" 
                :key="'empty-' + n"
                class="w-8 h-8 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded flex items-center justify-center"
              >
                <svg class="w-4 h-4 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
            </div>
          </div>
          
          <!-- 등록된 참가자 목록 -->
          <div v-if="registrations.length > 0" class="border-t pt-3">
            <div class="flex items-center justify-between mb-2">
              <span class="font-medium text-gray-700 dark:text-gray-300">등록된 참가자</span>
              <span class="text-xs bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 px-2 py-1 rounded-full">
                {{ registrations.length }}명
              </span>
            </div>
            <div class="max-h-32 overflow-y-auto">
              <div class="space-y-2">
                <div 
                  v-for="(registration, index) in registrations" 
                  :key="registration.id"
                  class="flex items-center justify-between bg-gray-50 dark:bg-gray-700 p-2 rounded-lg"
                >
                  <div class="flex items-center space-x-2">
                    <div class="w-6 h-6 bg-indigo-100 dark:bg-indigo-900 text-indigo-600 dark:text-indigo-300 rounded-full flex items-center justify-center text-xs font-semibold">
                      {{ index + 1 }}
                    </div>
                    <div>
                      <span class="text-sm text-gray-700 dark:text-gray-300 font-medium">{{ maskUserName(registration.user_name) }}</span>
                      <div class="text-xs text-gray-500 dark:text-gray-400">{{ registration.user_email }}</div>
                    </div>
                  </div>
                  <span class="text-xs text-gray-500 dark:text-gray-400">
                    {{ formatRegistrationDate(registration.registered_at) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 등록/취소 버튼 -->
        <div class="mt-6 flex justify-end space-x-3">
          <button
            v-if="authStore.isLoggedIn && !isRegistered"
            @click="registerForMeetup"
            :disabled="currentMeetupData.is_full || registering"
            :class="[
              'px-4 py-2 rounded-md text-sm font-medium',
              currentMeetupData.is_full || registering
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-indigo-600 hover:bg-indigo-700 text-white'
            ]"
          >
            <svg v-if="registering" class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ registering ? '등록 중...' : (currentMeetupData.is_full ? '마감' : '참가 신청') }}
          </button>
          
          <button
            v-if="authStore.isLoggedIn && isRegistered"
            @click="unregisterFromMeetup"
            :disabled="registering"
            class="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-md text-sm font-medium disabled:opacity-50"
          >
            <svg v-if="registering" class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ registering ? '취소 중...' : '참가 취소' }}
          </button>
          
          <button
            @click="selectedMeetup = null"
            class="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-md text-sm font-medium"
          >
            닫기
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useMeetupsStore } from '@/stores/meetups'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'

export default {
  name: 'CalendarView',
  setup() {
    const meetupsStore = useMeetupsStore()
    const authStore = useAuthStore()
    const currentMonth = ref(new Date())
    const selectedMeetup = ref(null)
    const selectedDateMeetups = ref(null)
    const registrations = ref([])
    const isRegistered = ref(false)
    const registering = ref(false)
    const refreshing = ref(false)
    const currentMeetupData = ref({})

    const weekDays = ['일', '월', '화', '수', '목', '금', '토']

    const calendarDates = computed(() => {
      const year = currentMonth.value.getFullYear()
      const month = currentMonth.value.getMonth()
      
      const firstDay = new Date(year, month, 1)
      const lastDay = new Date(year, month + 1, 0)
      const startDate = new Date(firstDay)
      startDate.setDate(startDate.getDate() - firstDay.getDay())
      
      const dates = []
      const current = new Date(startDate)
      
      for (let i = 0; i < 42; i++) {
        const dateObj = new Date(current)
        const isCurrentMonth = dateObj.getMonth() === month
        const isToday = dateObj.toDateString() === new Date().toDateString()
        
        const dayMeetups = meetupsStore.meetups.filter(meetup => {
          const meetupDate = new Date(meetup.date_time)
          return meetupDate.toDateString() === dateObj.toDateString()
        })

        dates.push({
          date: dateObj,
          isCurrentMonth,
          isToday,
          meetups: dayMeetups
        })
        
        current.setDate(current.getDate() + 1)
      }
      
      return dates
    })

    const previousMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() - 1, 1)
    }

    const nextMonth = () => {
      currentMonth.value = new Date(currentMonth.value.getFullYear(), currentMonth.value.getMonth() + 1, 1)
    }

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('ko-KR')
    }

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const formatRegistrationDate = (dateString) => {
      return new Date(dateString).toLocaleDateString('ko-KR', {
        month: 'short',
        day: 'numeric'
      })
    }

    const maskUserName = (name) => {
      if (!name || name.length === 0) return '***'
      if (name.length === 1) return '*'
      if (name.length === 2) return name[0] + '*'
      if (name.length === 3) return name[0] + '*' + name[2]
      // For names longer than 3 characters, show first and last character, mask the middle
      return name[0] + '*'.repeat(name.length - 2) + name[name.length - 1]
    }

    const fetchRegistrations = async (meetupId) => {
      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId}/registrations/`, {
          method: 'GET'
        })
        
        if (response.ok) {
          const data = await response.json()
          registrations.value = data.registrations
        }
      } catch (error) {
        console.error('Failed to fetch registrations:', error)
      }
    }

    const checkRegistrationStatus = async (meetupId) => {
      if (!authStore.isLoggedIn) {
        isRegistered.value = false
        return
      }
      
      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId}/status/`, {
          method: 'GET'
        })
        
        if (response.ok) {
          const data = await response.json()
          isRegistered.value = data.is_registered
        }
      } catch (error) {
        console.error('Failed to check registration status:', error)
        isRegistered.value = false
      }
    }

    const registerForMeetup = async () => {
      if (!selectedMeetup.value || registering.value) return
      
      registering.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${selectedMeetup.value.id}/register/`, {
          method: 'POST'
        })
        
        if (response.ok) {
          isRegistered.value = true
          await Promise.all([
            fetchRegistrations(selectedMeetup.value.id),
            refreshMeetupData()
          ])
        } else {
          const data = await response.json()
          alert(data.error || '등록에 실패했습니다')
        }
      } catch (error) {
        alert('네트워크 오류가 발생했습니다')
      } finally {
        registering.value = false
      }
    }

    const unregisterFromMeetup = async () => {
      if (!selectedMeetup.value || registering.value) return
      
      registering.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${selectedMeetup.value.id}/unregister/`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          isRegistered.value = false
          await Promise.all([
            fetchRegistrations(selectedMeetup.value.id),
            refreshMeetupData()
          ])
        } else {
          const data = await response.json()
          alert(data.error || '취소에 실패했습니다')
        }
      } catch (error) {
        alert('네트워크 오류가 발생했습니다')
      } finally {
        registering.value = false
      }
    }

    const refreshMeetupData = async () => {
      if (!selectedMeetup.value) return
      
      refreshing.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${selectedMeetup.value.id}/`, {
          method: 'GET'
        })
        
        if (response.ok) {
          const updatedMeetup = await response.json()
          // Update the current meetup data for real-time display
          currentMeetupData.value = {
            current_participants: updatedMeetup.current_participants,
            available_spots: updatedMeetup.available_spots,
            is_full: updatedMeetup.is_full,
            max_participants: updatedMeetup.max_participants
          }
          
          // Also update the selected meetup for consistency
          selectedMeetup.value = { ...selectedMeetup.value, ...updatedMeetup }
          
          // Update the store data
          await meetupsStore.fetchMeetups()
        }
      } catch (error) {
        console.error('Failed to refresh meetup data:', error)
      } finally {
        refreshing.value = false
      }
    }

    // Watch for selected meetup changes
    watch(selectedMeetup, async (newMeetup) => {
      if (newMeetup) {
        registrations.value = []
        isRegistered.value = false
        // Initialize current meetup data
        currentMeetupData.value = {
          current_participants: newMeetup.current_participants,
          available_spots: newMeetup.available_spots,
          is_full: newMeetup.is_full,
          max_participants: newMeetup.max_participants
        }
        await Promise.all([
          fetchRegistrations(newMeetup.id),
          checkRegistrationStatus(newMeetup.id)
        ])
      }
    })

    // Close date meetups modal when meetup detail modal is opened
    watch(selectedMeetup, (newMeetup) => {
      if (newMeetup && selectedDateMeetups.value) {
        selectedDateMeetups.value = null
      }
    })

    const showDateMeetups = (dateData) => {
      selectedDateMeetups.value = dateData
    }

    const selectMeetupFromDate = (meetup) => {
      selectedDateMeetups.value = null
      selectedMeetup.value = meetup
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
        '종료': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300',
        '임박': 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
        '예정': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        '모집중': 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
      }
      return classes[status] || 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    }

    return {
      meetupsStore,
      authStore,
      currentMonth,
      selectedMeetup,
      selectedDateMeetups,
      registrations,
      isRegistered,
      registering,
      refreshing,
      currentMeetupData,
      weekDays,
      calendarDates,
      previousMonth,
      nextMonth,
      formatDateTime,
      formatTime,
      formatRegistrationDate,
      maskUserName,
      registerForMeetup,
      unregisterFromMeetup,
      refreshMeetupData,
      showDateMeetups,
      selectMeetupFromDate,
      getStatus,
      getStatusClass
    }
  }
}
</script>