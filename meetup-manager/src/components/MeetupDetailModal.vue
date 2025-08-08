<template>
  <div v-if="selectedMeetup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-lg p-6 max-w-md w-full max-h-[90vh] overflow-y-auto" @click.stop>
      <div class="flex justify-between items-start mb-4">
        <h3 class="text-lg font-semibold text-gray-900 dark:text-white">{{ selectedMeetup.name }}</h3>
        <button @click="$emit('close')" class="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
      
      <!-- Meetup Image -->
      <div v-if="selectedMeetup.image_display_url" class="mb-4">
        <img 
          :src="selectedMeetup.image_display_url" 
          :alt="selectedMeetup.name"
          class="w-full h-48 object-cover rounded-lg border border-gray-200 dark:border-gray-600"
          @error="handleImageError"
        />
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
          v-if="authStore.isLoggedIn && !authStore.isGuest && !isRegistered"
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
          v-if="authStore.isLoggedIn && !authStore.isGuest && isRegistered"
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
          @click="$emit('close')"
          class="bg-gray-300 hover:bg-gray-400 text-gray-700 px-4 py-2 rounded-md text-sm font-medium"
        >
          닫기
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, watch } from 'vue'
import { useMeetupsStore } from '@/stores/meetups'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'

export default {
  name: 'MeetupDetailModal',
  props: {
    selectedMeetup: {
      type: Object,
      default: null
    }
  },
  emits: ['close', 'meetupUpdated'],
  setup(props, { emit }) {
    const meetupsStore = useMeetupsStore()
    const authStore = useAuthStore()
    const registrations = ref([])
    const registering = ref(false)
    const refreshing = ref(false)
    
    // Get current meetup data from store (for real-time updates)
    const currentMeetupData = computed(() => {
      if (!props.selectedMeetup) return {}
      const storeMeetup = meetupsStore.meetups.find(m => m.id === props.selectedMeetup.id)
      return storeMeetup || props.selectedMeetup
    })
    
    const isRegistered = computed(() => {
      return registrations.value.some(reg => 
        reg.user_email === authStore.user?.email
      )
    })

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
      if (!name || name.length <= 2) return name
      return name[0] + '*'.repeat(name.length - 2) + name[name.length - 1]
    }

    const fetchRegistrations = async () => {
      if (!props.selectedMeetup) return
      
      try {
        const response = await fetchWithCSRF(`/api/meetups/${props.selectedMeetup.id}/registrations/`)
        if (response.ok) {
          const data = await response.json()
          registrations.value = data.registrations || []
        }
      } catch (error) {
        console.error('Failed to fetch registrations:', error)
      }
    }

    const refreshMeetupData = async () => {
      refreshing.value = true
      try {
        await meetupsStore.fetchMeetups()
        await fetchRegistrations()
        emit('meetupUpdated')
      } catch (error) {
        console.error('Failed to refresh meetup data:', error)
      } finally {
        refreshing.value = false
      }
    }

    const registerForMeetup = async () => {
      if (registering.value || !props.selectedMeetup) return
      
      registering.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${props.selectedMeetup.id}/register/`, {
          method: 'POST'
        })
        
        if (response.ok) {
          await refreshMeetupData()
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

    const unregisterFromMeetup = async () => {
      if (registering.value || !props.selectedMeetup) return
      
      registering.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${props.selectedMeetup.id}/unregister/`, {
          method: 'DELETE'
        })
        
        if (response.ok) {
          await refreshMeetupData()
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

    // Watch for selectedMeetup changes to fetch registrations
    watch(() => props.selectedMeetup, (newMeetup) => {
      if (newMeetup) {
        fetchRegistrations()
      } else {
        registrations.value = []
      }
    }, { immediate: true })

    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }

    return {
      meetupsStore,
      authStore,
      registrations,
      registering,
      refreshing,
      currentMeetupData,
      isRegistered,
      formatDateTime,
      formatTime,
      formatRegistrationDate,
      maskUserName,
      refreshMeetupData,
      registerForMeetup,
      unregisterFromMeetup,
      handleImageError
    }
  }
}
</script>