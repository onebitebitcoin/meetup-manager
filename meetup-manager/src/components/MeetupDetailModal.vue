<template>
  <div v-if="selectedMeetup" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4" @click="$emit('close')">
    <div class="bg-white dark:bg-neutral-800 rounded-2xl shadow-xl max-w-lg w-full max-h-[90vh] overflow-hidden" @click.stop>
      <!-- Simple Header -->
      <div class="relative p-6 border-b border-neutral-200 dark:border-neutral-700">
        <!-- Close Button -->
        <button @click="$emit('close')" class="absolute top-4 right-4 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 transition-colors">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
        
        <!-- Title -->
        <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 pr-8">{{ selectedMeetup.name }}</h3>
      </div>
      
      <!-- Image (if available) -->
      <div v-if="selectedMeetup.image_display_url" class="w-full bg-neutral-100 dark:bg-neutral-900">
        <img
          :src="selectedMeetup.image_display_url"
          :alt="selectedMeetup.name"
          class="w-full h-48 object-cover"
          @error="handleImageError"
        />
      </div>

      <!-- Content -->
      <div class="px-6 py-4 overflow-y-auto max-h-[calc(90vh-12rem)]">
        <div class="space-y-4">
          <!-- Basic Info -->
          <div class="space-y-3">
            <div class="flex items-center text-sm text-neutral-600 dark:text-neutral-400">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
              </svg>
              {{ formatDateTime(selectedMeetup.date_time) }}
              <span v-if="selectedMeetup.end_time"> - {{ formatTime(selectedMeetup.end_time) }}</span>
            </div>
            
            <div class="flex items-center text-sm text-neutral-600 dark:text-neutral-400">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
              </svg>
              {{ selectedMeetup.location }}
            </div>
            
            <div class="flex items-center text-sm text-neutral-600 dark:text-neutral-400">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
              </svg>
              {{ currentMeetupData.current_participants || selectedMeetup.current_participants }}/{{ currentMeetupData.max_participants || selectedMeetup.max_participants }}명
              <span v-if="currentMeetupData.is_full" class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                마감
              </span>
              <span v-if="isWaitlisted" class="ml-2 inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                대기열 {{ waitlistPosition }}번째
              </span>
            </div>
            
            <div class="flex items-center text-sm text-neutral-600 dark:text-neutral-400">
              <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
              </svg>
              {{ selectedMeetup.creator_name }}
            </div>
          </div>
          
          <!-- Description -->
          <div v-if="selectedMeetup.description" class="pt-4 border-t border-neutral-200 dark:border-neutral-700">
            <h4 class="text-sm font-medium text-neutral-900 dark:text-neutral-100 mb-2">상세 정보</h4>
            <p class="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed whitespace-pre-line">{{ selectedMeetup.description }}</p>
          </div>
          
          <!-- Hashtags -->
          <div v-if="selectedMeetup.hashtags_list && selectedMeetup.hashtags_list.length > 0" class="pt-4 border-t border-neutral-200 dark:border-neutral-700">
            <h4 class="text-sm font-medium text-neutral-900 dark:text-neutral-100 mb-2">태그</h4>
            <div class="flex flex-wrap gap-2">
              <span 
                v-for="hashtag in selectedMeetup.hashtags_list" 
                :key="hashtag"
                class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300"
              >
                {{ hashtag }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- Action Buttons -->
        <div class="border-t border-neutral-200 dark:border-neutral-700 pt-4 mt-6">
          <div class="flex flex-col gap-2">
            <!-- Primary Action Button -->
            <button
              v-if="authStore.isLoggedIn && !authStore.isGuest && !isRegistered && !isWaitlisted"
              @click="registerForMeetup"
              :disabled="registering"
              :class="[
                'w-full py-3 px-4 rounded-lg text-sm font-medium transition-colors duration-200',
                registering
                  ? 'bg-neutral-200 dark:bg-neutral-700 text-neutral-500 dark:text-neutral-400 cursor-not-allowed'
                  : currentMeetupData.is_full
                    ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                    : 'bg-primary-600 hover:bg-primary-700 text-white'
              ]"
            >
              {{ registering ? '등록 중...' : (currentMeetupData.is_full ? '대기열 등록' : '참가 신청') }}
            </button>

            <!-- Waitlist Cancel Button -->
            <button
              v-if="authStore.isLoggedIn && !authStore.isGuest && isWaitlisted"
              @click="leaveWaitlist"
              :disabled="registering"
              class="w-full py-3 px-4 rounded-lg text-sm font-medium bg-orange-600 hover:bg-orange-700 text-white transition-colors duration-200 disabled:opacity-50"
            >
              {{ registering ? '취소 중...' : '대기열 취소' }}
            </button>
            
            <!-- Unregister Button -->
            <button
              v-if="authStore.isLoggedIn && !authStore.isGuest && isRegistered"
              @click="unregisterFromMeetup"
              :disabled="registering"
              class="w-full py-3 px-4 rounded-lg text-sm font-medium bg-red-600 hover:bg-red-700 text-white transition-colors duration-200 disabled:opacity-50"
            >
              {{ registering ? '취소 중...' : '참가 취소' }}
            </button>
            
            <!-- Close Button -->
            <button
              @click="$emit('close')"
              class="w-full py-3 px-4 rounded-lg text-sm font-medium bg-neutral-100 dark:bg-neutral-700 hover:bg-neutral-200 dark:hover:bg-neutral-600 text-neutral-700 dark:text-neutral-300 transition-colors duration-200"
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
    const isWaitlisted = ref(false)
    const waitlistPosition = ref(0)

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('ko-KR')
    }

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    // Check registration and waitlist status for current meetup
    const checkRegistrationStatus = async () => {
      if (!props.selectedMeetup || !authStore.isLoggedIn || authStore.isGuest) {
        isRegistered.value = false
        isWaitlisted.value = false
        return
      }
      
      try {
        // Check registration status
        const response = await fetchWithCSRF(`/api/meetups/${props.selectedMeetup.id}/status/`)
        if (response.ok) {
          const data = await response.json()
          isRegistered.value = data.is_registered
        }
        
        // Check waitlist status
        const waitlistData = await meetupsStore.checkWaitlistStatus(props.selectedMeetup.id)
        isWaitlisted.value = waitlistData.is_waitlisted
        waitlistPosition.value = waitlistData.position || 0
      } catch (error) {
        console.error('Failed to check status:', error)
        isRegistered.value = false
        isWaitlisted.value = false
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
          
          // If meetup is full and can join waitlist, ask user
          if (data.can_waitlist) {
            const joinWaitlist = confirm(`${data.error}\n\n${data.message}`)
            if (joinWaitlist) {
              try {
                const waitlistData = await meetupsStore.addToWaitlist(props.selectedMeetup.id)
                isWaitlisted.value = true
                waitlistPosition.value = waitlistData.position
                await meetupsStore.fetchMeetups()
                emit('meetupUpdated')
                alert(`대기열 ${waitlistData.position}번째로 등록되었습니다!`)
              } catch (waitlistError) {
                alert(waitlistError.message)
              }
            }
          } else {
            alert(data.error || '신청에 실패했습니다.')
          }
        }
      } catch (error) {
        alert('네트워크 오류가 발생했습니다.')
      } finally {
        registering.value = false
      }
    }

    const joinWaitlist = async () => {
      if (registering.value || !props.selectedMeetup) return
      
      registering.value = true
      try {
        const waitlistData = await meetupsStore.addToWaitlist(props.selectedMeetup.id)
        isWaitlisted.value = true
        waitlistPosition.value = waitlistData.position
        await meetupsStore.fetchMeetups()
        emit('meetupUpdated')
        alert(`대기열 ${waitlistData.position}번째로 등록되었습니다!`)
      } catch (error) {
        alert(error.message)
      } finally {
        registering.value = false
      }
    }

    const leaveWaitlist = async () => {
      if (registering.value || !props.selectedMeetup) return
      
      registering.value = true
      try {
        await meetupsStore.removeFromWaitlist(props.selectedMeetup.id)
        isWaitlisted.value = false
        waitlistPosition.value = 0
        await meetupsStore.fetchMeetups()
        emit('meetupUpdated')
        alert('대기열에서 제거되었습니다.')
      } catch (error) {
        alert(error.message)
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
        isWaitlisted.value = false
        waitlistPosition.value = 0
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
      isWaitlisted,
      waitlistPosition,
      formatDateTime,
      formatTime,
      registerForMeetup,
      unregisterFromMeetup,
      joinWaitlist,
      leaveWaitlist,
      handleImageError
    }
  }
}
</script>
