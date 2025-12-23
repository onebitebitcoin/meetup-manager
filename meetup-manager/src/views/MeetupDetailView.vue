<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-900 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <p class="text-red-800 dark:text-red-200">{{ error }}</p>
        <button @click="$router.push('/dashboard')" class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
          대시보드로 돌아가기
        </button>
      </div>

      <!-- Meetup Detail -->
      <div v-else-if="meetup" class="bg-beige-50 dark:bg-neutral-800 rounded-2xl shadow-xl overflow-hidden">
        <!-- Header with Back Button -->
        <div class="relative p-6 border-b border-neutral-200 dark:border-neutral-600 bg-beige-200 dark:bg-neutral-700">
          <button @click="$router.back()" class="absolute top-6 left-6 text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100 transition-colors flex items-center">
            <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            뒤로
          </button>

          <h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-100 text-center select-text cursor-text">
            {{ meetup.name }}
          </h1>
        </div>

        <!-- Image (if available) -->
        <div v-if="meetup.image_display_url" class="w-full bg-beige-100 dark:bg-neutral-900 aspect-video">
          <img
            :src="meetup.image_display_url"
            :alt="meetup.name"
            class="w-full h-full object-cover"
            @error="handleImageError"
          />
        </div>

        <!-- Content -->
        <div class="px-6 py-8">
          <div class="space-y-6">
            <!-- Basic Info -->
            <div class="space-y-4">
              <div class="flex items-center text-base text-neutral-600 dark:text-neutral-400">
                <svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/>
                </svg>
                <span class="select-text cursor-text">{{ formatDateTime(meetup.date_time) }}</span>
                <span v-if="meetup.end_time" class="select-text cursor-text"> - {{ formatTime(meetup.end_time) }}</span>
              </div>

              <div class="flex items-center text-base text-neutral-600 dark:text-neutral-400">
                <svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"/>
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"/>
                </svg>
                <span class="select-text cursor-text">{{ meetup.location }}</span>
              </div>

              <div class="flex items-center text-base text-neutral-600 dark:text-neutral-400">
                <svg class="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"/>
                </svg>
                {{ meetup.current_participants }}/{{ meetup.max_participants }}명
                <span v-if="meetup.is_full" class="ml-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200">
                  마감
                </span>
                <span v-if="isWaitlisted" class="ml-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200">
                  대기열 {{ waitlistPosition }}번째
                </span>
              </div>

              <div class="flex items-center text-base text-neutral-600 dark:text-neutral-400">
                <svg class="w-5 h-5 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                </svg>
                <span class="select-text cursor-text">{{ meetup.creator_name }}</span>
              </div>
            </div>

            <!-- Description -->
            <div v-if="meetup.description" class="pt-6 border-t border-neutral-200 dark:border-neutral-700">
              <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-3">상세 정보</h2>
              <div
                class="text-base text-neutral-600 dark:text-neutral-400 leading-relaxed whitespace-pre-line select-text cursor-text"
                v-html="formatDescription(meetup.description)"
              ></div>
            </div>

            <!-- Hashtags -->
            <div v-if="meetup.hashtags_list && meetup.hashtags_list.length > 0" class="pt-6 border-t border-neutral-200 dark:border-neutral-700">
              <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-3">태그</h2>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="hashtag in meetup.hashtags_list"
                  :key="hashtag"
                  class="inline-flex items-center px-3 py-1.5 rounded-md text-sm font-medium bg-beige-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 select-text cursor-text"
                >
                  {{ hashtag }}
                </span>
              </div>
            </div>

            <!-- Participants -->
            <div class="pt-6 border-t border-neutral-200 dark:border-neutral-700">
              <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">참가자 목록</h2>

              <!-- Loading state -->
              <div v-if="loadingParticipants" class="flex justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
              </div>

              <!-- Participants list -->
              <div v-else-if="participants.length > 0" class="space-y-3 max-h-96 overflow-y-auto">
                <div
                  v-for="(participant, index) in participants"
                  :key="participant.id"
                  class="flex items-center gap-4 p-3 bg-beige-50 dark:bg-neutral-800 rounded-lg"
                >
                  <div class="flex items-center space-x-4 flex-1 min-w-0">
                    <div class="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-primary-900 rounded-full flex items-center justify-center">
                      <span class="text-sm font-medium text-primary-700 dark:text-primary-300">{{ index + 1 }}</span>
                    </div>
                    <div class="min-w-0 flex-1">
                      <p class="text-base font-medium text-neutral-900 dark:text-neutral-100 truncate select-text cursor-text" :title="maskEmail(participant.user_email)">
                        {{ maskEmail(participant.user_email) }}
                      </p>
                    </div>
                  </div>
                  <div class="flex-shrink-0 ml-auto">
                    <span class="text-sm text-neutral-500 dark:text-neutral-400 whitespace-nowrap select-text cursor-text">
                      {{ formatDateTime(participant.registered_at) }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- Empty state -->
              <div v-else class="text-center py-8">
                <p class="text-base text-neutral-500 dark:text-neutral-400">아직 참가자가 없습니다.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Action Buttons - Sticky at Bottom -->
        <div class="sticky bottom-0 border-t border-neutral-200 dark:border-neutral-700 p-6 bg-beige-50 dark:bg-neutral-800">
          <div class="flex flex-col gap-3">
            <!-- Primary Action Button -->
            <button
              v-if="authStore.isLoggedIn && !authStore.isGuest && !isRegistered && !isWaitlisted"
              @click="registerForMeetup"
              :disabled="registering || isMeetupPassed"
              :class="[
                'w-full py-4 px-6 rounded-lg text-base font-semibold transition-colors duration-200',
                (registering || isMeetupPassed)
                  ? 'bg-beige-200 dark:bg-neutral-700 text-neutral-500 dark:text-neutral-400 cursor-not-allowed'
                  : 'text-primary-700 bg-primary-100 hover:bg-primary-200 dark:bg-primary-900 dark:text-primary-300 dark:hover:bg-primary-800'
              ]"
            >
              {{
                registering ? '등록 중...' :
                isMeetupPassed ? '모임이 종료되었습니다' :
                (meetup.is_full ? '대기열 등록' : '참가 신청')
              }}
            </button>

            <!-- Waitlist Cancel Button -->
            <button
              v-if="authStore.isLoggedIn && !authStore.isGuest && isWaitlisted"
              @click="leaveWaitlist"
              :disabled="registering || isMeetupPassed"
              class="w-full py-4 px-6 rounded-lg text-base font-semibold text-orange-700 bg-orange-100 hover:bg-orange-200 dark:bg-orange-900 dark:text-orange-300 dark:hover:bg-orange-800 transition-colors duration-200 disabled:opacity-50"
            >
              {{ registering ? '취소 중...' : '대기열 취소' }}
            </button>

            <!-- Unregister Button -->
            <button
              v-if="authStore.isLoggedIn && !authStore.isGuest && isRegistered"
              @click="unregisterFromMeetup"
              :disabled="registering || isMeetupPassed"
              class="w-full py-4 px-6 rounded-lg text-base font-semibold text-red-700 bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800 transition-colors duration-200 disabled:opacity-50"
            >
              {{ registering ? '취소 중...' : '참가 취소' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useMeetupsStore } from '@/stores/meetups'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'

export default {
  name: 'MeetupDetailView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const meetupsStore = useMeetupsStore()
    const authStore = useAuthStore()

    const meetup = ref(null)
    const loading = ref(true)
    const error = ref('')
    const registering = ref(false)
    const participants = ref([])
    const loadingParticipants = ref(false)
    const isRegistered = ref(false)
    const isWaitlisted = ref(false)
    const waitlistPosition = ref(0)

    const meetupId = computed(() => parseInt(route.params.id))

    const formatDateTime = (dateString) => {
      return new Date(dateString).toLocaleString('ko-KR')
    }

    const formatTime = (dateString) => {
      return new Date(dateString).toLocaleTimeString('ko-KR', {
        hour: '2-digit',
        minute: '2-digit'
      })
    }

    const maskEmail = (email) => {
      if (!email) return ''
      const [localPart, domain] = email.split('@')
      if (!domain) return email

      const maskedLocal = localPart.length <= 2
        ? localPart
        : localPart.substring(0, 2) + '*'.repeat(localPart.length - 2)

      return `${maskedLocal}@${domain}`
    }

    const isMeetupPassed = computed(() => {
      if (!meetup.value?.date_time) return false
      const meetupDate = new Date(meetup.value.date_time)
      const now = new Date()
      return meetupDate < now
    })

    const formatDescription = (text) => {
      if (!text) return ''

      const urlRegex = /((?:https?:\/\/)?(?:www\.)?[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*(?:\/[^\s<>"{}|\\^`[\]]*)?)/gi

      return text.replace(urlRegex, (url) => {
        const cleanUrl = url.replace(/[.!?,;:]$/, '')
        const trailingPunc = url.slice(cleanUrl.length)
        const href = cleanUrl.startsWith('http') ? cleanUrl : `https://${cleanUrl}`

        if (!cleanUrl.includes('.') || cleanUrl.length < 4) {
          return url
        }

        return `<a href="${href}" target="_blank" rel="noopener noreferrer" class="text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300 underline break-words select-text cursor-pointer">${cleanUrl}</a>${trailingPunc}`
      })
    }

    const updateMetaTags = (meetupData) => {
      // Update page title
      document.title = `${meetupData.name} - 한입 모임`

      // Update OG meta tags
      const setMetaTag = (property, content) => {
        let meta = document.querySelector(`meta[property="${property}"]`)
        if (!meta) {
          meta = document.createElement('meta')
          meta.setAttribute('property', property)
          document.head.appendChild(meta)
        }
        meta.setAttribute('content', content)
      }

      const setNameMetaTag = (name, content) => {
        let meta = document.querySelector(`meta[name="${name}"]`)
        if (!meta) {
          meta = document.createElement('meta')
          meta.setAttribute('name', name)
          document.head.appendChild(meta)
        }
        meta.setAttribute('content', content)
      }

      // Open Graph tags
      setMetaTag('og:type', 'article')
      setMetaTag('og:title', `${meetupData.name} - 한입 모임`)
      setMetaTag('og:description', meetupData.description || '한입 모임에서 함께해요!')
      setMetaTag('og:url', `https://meet.onebitebitcoin.com/meetup/${meetupData.id}`)

      // Set meetup image if available
      if (meetupData.image_display_url) {
        setMetaTag('og:image', meetupData.image_display_url)
        setMetaTag('og:image:alt', meetupData.name)
      }

      // Twitter card tags
      setMetaTag('twitter:card', 'summary_large_image')
      setMetaTag('twitter:title', `${meetupData.name} - 한입 모임`)
      setMetaTag('twitter:description', meetupData.description || '한입 모임에서 함께해요!')
      if (meetupData.image_display_url) {
        setMetaTag('twitter:image', meetupData.image_display_url)
        setMetaTag('twitter:image:alt', meetupData.name)
      }

      // General description
      setNameMetaTag('description', meetupData.description || '한입 모임에서 함께해요!')
    }

    const fetchMeetup = async () => {
      loading.value = true
      error.value = ''

      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId.value}/`)

        if (response.ok) {
          const data = await response.json()
          meetup.value = data

          // Update page title and meta tags
          updateMetaTags(data)
        } else if (response.status === 404) {
          error.value = '모임을 찾을 수 없습니다.'
        } else {
          error.value = '모임 정보를 불러오는데 실패했습니다.'
        }
      } catch (err) {
        error.value = '네트워크 오류가 발생했습니다.'
        console.error('Failed to fetch meetup:', err)
      } finally {
        loading.value = false
      }
    }

    const fetchParticipants = async () => {
      loadingParticipants.value = true
      try {
        const response = await fetch(`/api/meetups/${meetupId.value}/registrations/`, {
          credentials: 'include'
        })
        if (response.ok) {
          const data = await response.json()
          participants.value = data.registrations || []
        }
      } catch (error) {
        console.error('Failed to fetch participants:', error)
        participants.value = []
      } finally {
        loadingParticipants.value = false
      }
    }

    const checkRegistrationStatus = async () => {
      if (!authStore.isLoggedIn || authStore.isGuest) {
        isRegistered.value = false
        isWaitlisted.value = false
        return
      }

      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId.value}/status/`)
        if (response.ok) {
          const data = await response.json()
          isRegistered.value = data.is_registered
        }

        const waitlistData = await meetupsStore.checkWaitlistStatus(meetupId.value)
        isWaitlisted.value = waitlistData.is_waitlisted
        waitlistPosition.value = waitlistData.position || 0
      } catch (error) {
        console.error('Failed to check status:', error)
        isRegistered.value = false
        isWaitlisted.value = false
      }
    }

    const registerForMeetup = async () => {
      if (registering.value) return

      registering.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId.value}/register/`, {
          method: 'POST'
        })

        if (response.ok) {
          isRegistered.value = true
          await fetchMeetup()
          await fetchParticipants()
          alert('모임 신청이 완료되었습니다!')
        } else {
          const data = await response.json()

          if (data.can_waitlist) {
            const joinWaitlist = confirm(`${data.error}\n\n${data.message}`)
            if (joinWaitlist) {
              try {
                const waitlistData = await meetupsStore.addToWaitlist(meetupId.value)
                isWaitlisted.value = true
                waitlistPosition.value = waitlistData.position
                await fetchMeetup()
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

    const leaveWaitlist = async () => {
      if (registering.value) return

      registering.value = true
      try {
        await meetupsStore.removeFromWaitlist(meetupId.value)
        isWaitlisted.value = false
        waitlistPosition.value = 0
        await fetchMeetup()
        alert('대기열에서 제거되었습니다.')
      } catch (error) {
        alert(error.message)
      } finally {
        registering.value = false
      }
    }

    const unregisterFromMeetup = async () => {
      if (registering.value) return

      registering.value = true
      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId.value}/unregister/`, {
          method: 'DELETE'
        })

        if (response.ok) {
          isRegistered.value = false
          await fetchMeetup()
          await fetchParticipants()
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

    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }

    onMounted(async () => {
      await fetchMeetup()
      if (meetup.value) {
        fetchParticipants()
        checkRegistrationStatus()
      }
    })

    return {
      meetup,
      loading,
      error,
      authStore,
      registering,
      participants,
      loadingParticipants,
      isRegistered,
      isWaitlisted,
      waitlistPosition,
      isMeetupPassed,
      formatDateTime,
      formatTime,
      maskEmail,
      formatDescription,
      registerForMeetup,
      unregisterFromMeetup,
      leaveWaitlist,
      handleImageError
    }
  }
}
</script>

<style scoped>
.whitespace-pre-line :deep(a) {
  color: rgb(37 99 235);
  text-decoration: underline;
  word-break: break-all;
  transition: color 0.2s;
}

.whitespace-pre-line :deep(a:hover) {
  color: rgb(30 64 175);
}

.dark .whitespace-pre-line :deep(a) {
  color: rgb(96 165 250);
}

.dark .whitespace-pre-line :deep(a:hover) {
  color: rgb(147 197 253);
}
</style>
