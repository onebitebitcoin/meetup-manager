<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-900">
    <!-- Header -->
    <header class="sticky top-0 z-40 bg-beige-200 dark:bg-neutral-800 border-b border-beige-300 dark:border-neutral-700 safe-area-top">
      <div class="max-w-2xl mx-auto px-4 py-4 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button
            class="p-1 text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100"
            @click="$router.push('/dashboard')"
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
          </button>
          <h1 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            후기
          </h1>
        </div>
        <span class="text-sm text-neutral-500 dark:text-neutral-400">
          총 {{ total }}개
        </span>
      </div>
    </header>

    <!-- Content -->
    <main class="max-w-2xl mx-auto px-4 py-6">
      <!-- Write Review CTA Section (로그인 사용자 + 미작성 후기가 있을 때만) -->
      <div
        v-if="!authStore.isGuest && pendingReviewMeetups.length > 0"
        class="mb-6 bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700"
      >
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <svg
                class="w-5 h-5 text-primary-600 dark:text-primary-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
              <h3 class="text-base font-medium text-neutral-900 dark:text-white">
                후기 작성하기
              </h3>
              <span class="text-xs text-neutral-500 dark:text-neutral-400">
                ({{ pendingReviewMeetups.length }}개)
              </span>
            </div>
          </div>
          <div class="space-y-2 max-h-64 overflow-y-auto">
            <router-link
              v-for="meetup in pendingReviewMeetups"
              :key="meetup.id"
              :to="`/write-review/${meetup.id}`"
              class="flex items-center gap-3 p-3 bg-neutral-50 dark:bg-neutral-700/50 rounded-lg border border-neutral-200 dark:border-neutral-600 hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
            >
              <div
                v-if="meetup.image_display_url"
                class="flex-shrink-0 w-10 h-10 rounded-lg overflow-hidden bg-neutral-100 dark:bg-neutral-700"
              >
                <img
                  :src="meetup.image_display_url"
                  :alt="meetup.name"
                  class="w-full h-full object-cover"
                >
              </div>
              <div
                v-else
                class="flex-shrink-0 w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-700 flex items-center justify-center"
              >
                <svg
                  class="w-5 h-5 text-neutral-400"
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
              <div class="flex-1 min-w-0">
                <p class="font-medium text-neutral-900 dark:text-neutral-100 truncate text-sm">
                  {{ meetup.name }}
                </p>
                <p class="text-xs text-neutral-500 dark:text-neutral-400">
                  {{ formatMeetupDate(meetup.date_time) }}
                </p>
              </div>
              <span class="text-xs text-primary-600 dark:text-primary-400 font-medium">
                후기 작성
              </span>
            </router-link>
          </div>
        </div>
      </div>
      <!-- Loading State -->
      <div v-if="loading && reviews.length === 0" class="flex justify-center py-20">
        <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
      </div>

      <!-- Empty State -->
      <div v-else-if="reviews.length === 0" class="text-center py-20">
        <svg
          class="mx-auto w-12 h-12 text-neutral-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
          />
        </svg>
        <p class="mt-4 text-neutral-500 dark:text-neutral-400">
          아직 후기가 없습니다.
        </p>
      </div>

      <!-- Reviews List -->
      <div v-else class="space-y-4">
        <ReviewCard
          v-for="review in reviews"
          :key="review.id"
          :review="review"
        />

        <!-- Load More Button -->
        <div v-if="hasMore" class="flex justify-center pt-4">
          <button
            :disabled="loading"
            class="px-6 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20 hover:bg-primary-100 dark:hover:bg-primary-900/30 rounded-lg disabled:opacity-50"
            @click="loadMore"
          >
            {{ loading ? '불러오는 중...' : '더 보기' }}
          </button>
        </div>
      </div>
    </main>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useReviewsStore } from '@/stores/reviews'
import { useAuthStore } from '@/stores/auth'
import ReviewCard from '@/components/ReviewCard.vue'

export default {
  name: 'ReviewFeedView',
  components: {
    ReviewCard,
  },
  setup() {
    const reviewsStore = useReviewsStore()
    const authStore = useAuthStore()

    const reviews = computed(() => reviewsStore.reviews)
    const loading = computed(() => reviewsStore.loading)
    const hasMore = computed(() => reviewsStore.hasMore)
    const total = computed(() => reviewsStore.total)

    // 후기 미작성 밋업 (종료된 밋업 중)
    const pendingReviewMeetups = computed(() => {
      return reviewsStore.attendedMeetups.filter(m => !m.has_review)
    })

    // 밋업 날짜 포맷
    const formatMeetupDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    }

    const loadMore = async () => {
      await reviewsStore.loadMore()
    }

    onMounted(async () => {
      reviewsStore.reset()
      await reviewsStore.fetchReviews(1)
      // 로그인한 사용자라면 참석한 밋업 목록도 로드
      if (!authStore.isGuest) {
        await reviewsStore.fetchAttendedMeetups()
      }
    })

    return {
      authStore,
      reviews,
      loading,
      hasMore,
      total,
      loadMore,
      pendingReviewMeetups,
      formatMeetupDate,
    }
  },
}
</script>
