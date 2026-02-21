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
        class="mb-6 bg-red-50 dark:bg-red-900/20 rounded-xl border border-red-200 dark:border-red-800"
      >
        <div class="p-4">
          <div class="flex items-center justify-between mb-3">
            <div class="flex items-center gap-2">
              <svg
                class="w-5 h-5 text-red-600 dark:text-red-400"
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
          <div class="space-y-1 max-h-36 overflow-y-auto">
            <router-link
              v-for="meetup in pendingReviewMeetups"
              :key="meetup.id"
              :to="`/write-review/${meetup.id}`"
              class="flex items-center gap-2 py-1.5 px-2 bg-white/60 dark:bg-neutral-800/60 rounded hover:bg-white dark:hover:bg-neutral-800 transition-colors"
            >
              <div class="flex-1 min-w-0">
                <p class="font-medium text-neutral-900 dark:text-neutral-100 truncate text-xs">
                  {{ meetup.name }}
                </p>
              </div>
              <span class="text-[10px] text-neutral-500 dark:text-neutral-400 flex-shrink-0">
                {{ formatMeetupDate(meetup.date_time) }}
              </span>
              <svg
                class="w-3 h-3 text-red-400 flex-shrink-0"
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
            </router-link>
          </div>
        </div>
      </div>
      <!-- Reviews Container -->
      <div class="bg-green-50 dark:bg-green-900/20 rounded-xl border border-green-200 dark:border-green-800">
        <div class="p-4">
          <!-- Header -->
          <div class="flex items-center gap-2 mb-3">
            <svg
              class="w-5 h-5 text-green-600 dark:text-green-400"
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
            <h3 class="text-base font-medium text-neutral-900 dark:text-white">
              작성된 후기
            </h3>
            <span class="text-xs text-neutral-500 dark:text-neutral-400">
              ({{ total }}개)
            </span>
          </div>

          <!-- Loading State -->
          <div
            v-if="loading && reviews.length === 0"
            class="flex justify-center py-12"
          >
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600" />
          </div>

          <!-- Empty State -->
          <div
            v-else-if="reviews.length === 0"
            class="text-center py-12"
          >
            <p class="text-neutral-500 dark:text-neutral-400">
              아직 후기가 없습니다.
            </p>
          </div>

          <!-- Reviews List -->
          <div
            v-else
            class="space-y-1 max-h-64 md:max-h-[34rem] overflow-y-auto"
          >
            <ReviewCard
              v-for="review in reviews"
              :key="review.id"
              :review="review"
            />

            <!-- Load More Button -->
            <div
              v-if="hasMore"
              class="flex justify-center pt-2"
            >
              <button
                :disabled="loading"
                class="px-6 py-2 text-sm font-medium text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20 hover:bg-primary-100 dark:hover:bg-primary-900/30 rounded-lg disabled:opacity-50"
                @click="loadMore"
              >
                {{ loading ? '불러오는 중...' : '더 보기' }}
              </button>
            </div>
          </div>
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
