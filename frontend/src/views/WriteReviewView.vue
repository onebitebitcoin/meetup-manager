<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-950">
    <!-- Header -->
    <nav class="bg-beige-200 dark:bg-neutral-900 border-b border-beige-300 dark:border-neutral-800 safe-area-top">
      <div class="max-w-3xl mx-auto px-4 sm:px-6">
        <div class="flex items-center justify-between h-14">
          <button
            class="flex items-center gap-2 text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100"
            @click="goBack"
          >
            <svg
              class="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M15 19l-7-7 7-7"
              />
            </svg>
            <span class="text-sm font-medium">뒤로</span>
          </button>
          <h1 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            후기 작성
          </h1>
          <div class="w-16" />
        </div>
      </div>
    </nav>

    <div class="max-w-3xl mx-auto px-4 sm:px-6 py-6">
      <!-- Loading State -->
      <div
        v-if="loading"
        class="flex items-center justify-center py-12"
      >
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>

      <!-- No Meetup Selected - Show List -->
      <div
        v-else-if="!selectedMeetup"
        class="space-y-6"
      >
        <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-4 sm:p-6">
          <h2 class="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-4">
            후기를 작성할 모임을 선택하세요
          </h2>

          <!-- No Attended Meetups -->
          <div
            v-if="availableMeetups.length === 0"
            class="text-center py-8"
          >
            <svg
              class="mx-auto h-12 w-12 text-neutral-400"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                stroke-linecap="round"
                stroke-linejoin="round"
                stroke-width="2"
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <p class="mt-4 text-neutral-600 dark:text-neutral-400">
              후기를 작성할 수 있는 모임이 없습니다.
            </p>
            <p class="text-sm text-neutral-500 dark:text-neutral-500 mt-1">
              종료된 모임에만 후기를 작성할 수 있습니다.
            </p>
          </div>

          <!-- Meetup List -->
          <div
            v-else
            class="space-y-3"
          >
            <button
              v-for="meetup in availableMeetups"
              :key="meetup.id"
              class="w-full flex items-center gap-3 p-3 rounded-lg border border-neutral-200 dark:border-neutral-700 hover:bg-neutral-50 dark:hover:bg-neutral-700/50 transition-colors text-left"
              @click="selectMeetup(meetup)"
            >
              <!-- Meetup Image -->
              <div
                v-if="meetup.image_display_url"
                class="flex-shrink-0 w-14 h-14 rounded-lg overflow-hidden bg-neutral-100 dark:bg-neutral-700"
              >
                <img
                  :src="meetup.image_display_url"
                  :alt="meetup.name"
                  class="w-full h-full object-cover"
                >
              </div>
              <div
                v-else
                class="flex-shrink-0 w-14 h-14 rounded-lg bg-neutral-100 dark:bg-neutral-700 flex items-center justify-center"
              >
                <svg
                  class="w-6 h-6 text-neutral-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                  />
                </svg>
              </div>

              <!-- Meetup Info -->
              <div class="flex-1 min-w-0">
                <p class="font-medium text-neutral-900 dark:text-neutral-100 truncate">
                  {{ meetup.name }}
                </p>
                <p class="text-sm text-neutral-500 dark:text-neutral-400">
                  {{ formatDate(meetup.date_time) }}
                </p>
                <p class="text-xs text-neutral-400 dark:text-neutral-500">
                  {{ meetup.location }}
                </p>
              </div>

              <!-- Arrow -->
              <svg
                class="w-5 h-5 text-neutral-400 flex-shrink-0"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M9 5l7 7-7 7"
                />
              </svg>
            </button>
          </div>
        </div>
      </div>

      <!-- Review Form -->
      <div
        v-else
        class="space-y-6"
      >
        <!-- Selected Meetup Info -->
        <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-4">
          <div class="flex items-center gap-3">
            <div
              v-if="selectedMeetup.image_display_url"
              class="flex-shrink-0 w-16 h-16 rounded-lg overflow-hidden bg-neutral-100 dark:bg-neutral-700"
            >
              <img
                :src="selectedMeetup.image_display_url"
                :alt="selectedMeetup.name"
                class="w-full h-full object-cover"
              >
            </div>
            <div
              v-else
              class="flex-shrink-0 w-16 h-16 rounded-lg bg-neutral-100 dark:bg-neutral-700 flex items-center justify-center"
            >
              <svg
                class="w-7 h-7 text-neutral-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"
                />
              </svg>
            </div>
            <div class="min-w-0 flex-1">
              <p class="font-medium text-neutral-900 dark:text-neutral-100">
                {{ selectedMeetup.name }}
              </p>
              <p class="text-sm text-neutral-500 dark:text-neutral-400">
                {{ formatDate(selectedMeetup.date_time) }}
              </p>
              <p class="text-xs text-neutral-400 dark:text-neutral-500">
                {{ selectedMeetup.location }}
              </p>
            </div>
            <button
              class="text-sm text-primary-600 dark:text-primary-400 hover:underline"
              @click="selectedMeetup = null"
            >
              변경
            </button>
          </div>
        </div>

        <!-- Review Form -->
        <div class="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 p-4 sm:p-6 space-y-6">
          <!-- Rating -->
          <div>
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
              별점
            </label>
            <div class="flex items-center gap-1">
              <button
                v-for="n in 5"
                :key="n"
                type="button"
                class="p-1 focus:outline-none"
                @click="rating = n"
              >
                <svg
                  :class="[
                    'w-10 h-10 transition-colors',
                    n <= rating
                      ? 'text-yellow-400'
                      : 'text-neutral-300 dark:text-neutral-600 hover:text-yellow-300'
                  ]"
                  fill="currentColor"
                  viewBox="0 0 20 20"
                >
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
              </button>
              <span class="ml-3 text-lg font-medium text-neutral-700 dark:text-neutral-300">
                {{ rating }}점
              </span>
            </div>
          </div>

          <!-- Content -->
          <div>
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              후기 내용
            </label>
            <textarea
              v-model="content"
              rows="6"
              maxlength="500"
              placeholder="모임에 대한 후기를 작성해주세요."
              class="w-full px-4 py-3 border border-neutral-300 dark:border-neutral-600 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:text-neutral-100 dark:placeholder-neutral-400 resize-none"
            />
            <div class="mt-1 text-right text-sm text-neutral-500 dark:text-neutral-400">
              {{ content.length }}/500자
            </div>
          </div>

          <!-- Error Message -->
          <div
            v-if="errorMessage"
            class="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg"
          >
            <p class="text-sm text-red-600 dark:text-red-400">
              {{ errorMessage }}
            </p>
          </div>

          <!-- Submit Button -->
          <button
            :disabled="!isValid || saving"
            class="w-full py-3 px-4 text-white font-medium bg-primary-600 hover:bg-primary-700 disabled:bg-neutral-400 disabled:cursor-not-allowed rounded-lg transition-colors"
            @click="handleSubmit"
          >
            {{ saving ? '저장 중...' : '후기 저장하기' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useReviewsStore } from '@/stores/reviews'

export default {
  name: 'WriteReviewView',
  setup() {
    const router = useRouter()
    const route = useRoute()
    const reviewsStore = useReviewsStore()

    const loading = ref(true)
    const saving = ref(false)
    const errorMessage = ref('')
    const selectedMeetup = ref(null)
    const rating = ref(5)
    const content = ref('')

    const isValid = computed(() => {
      return rating.value >= 1 && rating.value <= 5 && content.value.trim().length > 0
    })

    // 후기 미작성 밋업만 필터링
    const availableMeetups = computed(() => {
      return reviewsStore.attendedMeetups.filter(m => !m.has_review)
    })

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    }

    const goBack = () => {
      // URL에 meetupId가 있는 경우(직접 링크로 접근)에는 바로 이전 페이지로
      if (route.params.meetupId) {
        router.back()
      } else if (selectedMeetup.value) {
        // /write-review에서 밋업을 선택한 경우에는 선택 해제
        selectedMeetup.value = null
      } else {
        router.back()
      }
    }

    const selectMeetup = (meetup) => {
      selectedMeetup.value = meetup
      rating.value = 5
      content.value = ''
      errorMessage.value = ''
    }

    const loadMeetupById = async (meetupId) => {
      try {
        const response = await fetch(`/api/meetups/${meetupId}/`, {
          credentials: 'include',
        })
        if (response.ok) {
          const meetup = await response.json()
          selectedMeetup.value = {
            id: meetup.id,
            name: meetup.name,
            date_time: meetup.date_time,
            location: meetup.location,
            image_display_url: meetup.image_display_url,
          }
        }
      } catch (err) {
        console.error('Failed to load meetup:', err)
      }
    }

    const handleSubmit = async () => {
      if (!isValid.value || saving.value || !selectedMeetup.value) return

      saving.value = true
      errorMessage.value = ''

      const reviewData = {
        rating: rating.value,
        content: content.value.trim(),
      }

      const result = await reviewsStore.createReview(selectedMeetup.value.id, reviewData)

      saving.value = false

      if (result.success) {
        // 성공 시 후기 피드로 이동
        router.push('/reviews')
      } else {
        errorMessage.value = result.error
      }
    }

    onMounted(async () => {
      loading.value = true

      // 참석한 밋업 목록 로드
      await reviewsStore.fetchAttendedMeetups()

      // URL에서 meetupId가 있으면 해당 밋업 선택
      const meetupId = route.params.meetupId
      if (meetupId) {
        const foundMeetup = reviewsStore.attendedMeetups.find(
          m => m.id === parseInt(meetupId),
        )
        if (foundMeetup) {
          selectedMeetup.value = foundMeetup
        } else {
          // 밋업 목록에 없으면 직접 조회 (관리자 등)
          await loadMeetupById(meetupId)
        }
      }

      loading.value = false
    })

    // Route 변경 감지
    watch(() => route.params.meetupId, async (newId) => {
      if (newId) {
        const foundMeetup = reviewsStore.attendedMeetups.find(
          m => m.id === parseInt(newId),
        )
        if (foundMeetup) {
          selectedMeetup.value = foundMeetup
        } else {
          await loadMeetupById(newId)
        }
      } else {
        selectedMeetup.value = null
      }
    })

    return {
      loading,
      saving,
      errorMessage,
      selectedMeetup,
      rating,
      content,
      isValid,
      availableMeetups,
      formatDate,
      goBack,
      selectMeetup,
      handleSubmit,
    }
  },
}
</script>
