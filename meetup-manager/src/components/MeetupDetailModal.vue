<template>
  <div v-if="selectedMeetup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click="$emit('close')">
    <div class="bg-white dark:bg-gray-800 rounded-xl shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden" @click.stop>
      <!-- Header with Image Background -->
      <div class="relative">
        <div v-if="selectedMeetup.image_display_url" class="h-48 bg-gradient-to-br from-indigo-500 to-purple-600 overflow-hidden">
          <img 
            :src="selectedMeetup.image_display_url" 
            :alt="selectedMeetup.name"
            class="w-full h-full object-cover"
            @error="handleImageError"
          />
          <div class="absolute inset-0 bg-black bg-opacity-30"></div>
        </div>
        <div v-else class="h-32 bg-gradient-to-br from-indigo-500 to-purple-600"></div>
        
        <!-- Close Button -->
        <button @click="$emit('close')" class="absolute top-4 right-4 bg-white bg-opacity-20 hover:bg-opacity-30 backdrop-blur-sm rounded-full p-2 text-white transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
        
        <!-- Title Overlay -->
        <div class="absolute bottom-0 left-0 right-0 p-6 text-white">
          <h3 class="text-2xl font-bold mb-2 drop-shadow-lg">{{ selectedMeetup.name }}</h3>
        </div>
      </div>
      
      <!-- Content -->
      <div class="p-6 overflow-y-auto max-h-[calc(90vh-12rem)]">
        <div class="space-y-6">
          <!-- Time and Location Row -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-start space-x-3">
              <div class="bg-indigo-100 dark:bg-indigo-900 rounded-full p-2 flex-shrink-0">
                <svg class="w-5 h-5 text-indigo-600 dark:text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">시간</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  {{ formatDateTime(selectedMeetup.date_time) }}
                  <span v-if="selectedMeetup.end_time" class="block"> - {{ formatTime(selectedMeetup.end_time) }}</span>
                </p>
              </div>
            </div>
            
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-start space-x-3">
              <div class="bg-green-100 dark:bg-green-900 rounded-full p-2 flex-shrink-0">
                <svg class="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">장소</p>
                <p class="text-sm text-gray-600 dark:text-gray-400">{{ selectedMeetup.location }}</p>
              </div>
            </div>
          </div>
          
          <!-- Participants and Creator Row -->
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-start space-x-3">
              <div class="bg-blue-100 dark:bg-blue-900 rounded-full p-2 flex-shrink-0">
                <svg class="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">참가 인원</p>
                <div class="flex items-center space-x-2">
                  <span class="text-sm font-semibold text-gray-900 dark:text-white">
                    {{ currentMeetupData.current_participants || selectedMeetup.current_participants }}/{{ currentMeetupData.max_participants || selectedMeetup.max_participants }}명
                  </span>
                  <span v-if="currentMeetupData.is_full" class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                    마감
                  </span>
                </div>
              </div>
            </div>
            
            <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 flex items-start space-x-3">
              <div class="bg-purple-100 dark:bg-purple-900 rounded-full p-2 flex-shrink-0">
                <svg class="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white mb-1">생성자</p>
                <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ selectedMeetup.creator_name }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ selectedMeetup.creator_email }}</p>
              </div>
            </div>
          </div>
          
          <!-- Description -->
          <div class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div class="flex items-start space-x-3">
              <div class="bg-orange-100 dark:bg-orange-900 rounded-full p-2 flex-shrink-0">
                <svg class="w-5 h-5 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white mb-2">상세 정보</p>
                <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed whitespace-pre-line">{{ selectedMeetup.description }}</p>
              </div>
            </div>
          </div>
          
          <!-- Hashtags -->
          <div v-if="selectedMeetup.hashtags_list && selectedMeetup.hashtags_list.length > 0" class="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
            <div class="flex items-start space-x-3">
              <div class="bg-pink-100 dark:bg-pink-900 rounded-full p-2 flex-shrink-0">
                <svg class="w-5 h-5 text-pink-600 dark:text-pink-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"></path>
                </svg>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-sm font-medium text-gray-900 dark:text-white mb-3">태그</p>
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="hashtag in selectedMeetup.hashtags_list" 
                    :key="hashtag"
                    class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900 dark:to-indigo-900 text-blue-700 dark:text-blue-300 border border-blue-200 dark:border-blue-700"
                  >
                    #{{ hashtag }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="border-t border-gray-200 dark:border-gray-600 pt-6 mt-6">
          <div class="flex flex-col sm:flex-row gap-3 sm:justify-end">
            <button
              v-if="authStore.isLoggedIn && !authStore.isGuest && !isRegistered"
              @click="registerForMeetup"
              :disabled="currentMeetupData.is_full || registering"
              :class="[
                'flex items-center justify-center px-6 py-3 rounded-lg text-sm font-medium shadow-sm transition-all duration-200',
                currentMeetupData.is_full || registering
                  ? 'bg-gray-200 dark:bg-gray-700 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                  : 'bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white transform hover:scale-105'
              ]"
            >
              <svg v-if="registering" class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6"></path>
              </svg>
              {{ registering ? '등록 중...' : (currentMeetupData.is_full ? '마감' : '참가 신청') }}
            </button>
            
            <button
              v-if="authStore.isLoggedIn && !authStore.isGuest && isRegistered"
              @click="unregisterFromMeetup"
              :disabled="registering"
              class="flex items-center justify-center bg-gradient-to-r from-red-600 to-pink-600 hover:from-red-700 hover:to-pink-700 text-white px-6 py-3 rounded-lg text-sm font-medium shadow-sm transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:transform-none"
            >
              <svg v-if="registering" class="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <svg v-else class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
              {{ registering ? '취소 중...' : '참가 취소' }}
            </button>
            
            <button
              @click="$emit('close')"
              class="flex items-center justify-center bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-300 px-6 py-3 rounded-lg text-sm font-medium shadow-sm transition-all duration-200"
            >
              닫기
            </button>
          </div>
        </div>
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
    const registering = ref(false)
    
    // Get current meetup data from store (for real-time updates)
    const currentMeetupData = computed(() => {
      if (!props.selectedMeetup) return {}
      const storeMeetup = meetupsStore.meetups.find(m => m.id === props.selectedMeetup.id)
      return storeMeetup || props.selectedMeetup
    })
    
    // Check if current user is registered (will be updated by parent component)
    const isRegistered = ref(false)

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('ko-KR')
    }

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Check registration status for current meetup
    const checkRegistrationStatus = async () => {
      if (!props.selectedMeetup || !authStore.isLoggedIn || authStore.isGuest) {
        isRegistered.value = false
        return
      }
      
      try {
        const response = await fetchWithCSRF(`/api/meetups/${props.selectedMeetup.id}/status/`)
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
      if (registering.value || !props.selectedMeetup) return
      
      registering.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${props.selectedMeetup.id}/register/`, {
          method: 'POST'
        })
        
        if (response.ok) {
          isRegistered.value = true
          await meetupsStore.fetchMeetups()
          emit('meetupUpdated')
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
          isRegistered.value = false
          await meetupsStore.fetchMeetups()
          emit('meetupUpdated')
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

    // Watch for selectedMeetup changes to check registration status
    watch(() => props.selectedMeetup, (newMeetup) => {
      if (newMeetup) {
        checkRegistrationStatus()
      } else {
        isRegistered.value = false
      }
    }, { immediate: true })

    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }

    return {
      meetupsStore,
      authStore,
      registering,
      currentMeetupData,
      isRegistered,
      formatDateTime,
      formatTime,
      registerForMeetup,
      unregisterFromMeetup,
      handleImageError
    }
  }
}
</script>