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
import ReviewCard from '@/components/ReviewCard.vue'

export default {
  name: 'ReviewFeedView',
  components: {
    ReviewCard,
  },
  setup() {
    const reviewsStore = useReviewsStore()

    const reviews = computed(() => reviewsStore.reviews)
    const loading = computed(() => reviewsStore.loading)
    const hasMore = computed(() => reviewsStore.hasMore)
    const total = computed(() => reviewsStore.total)

    const loadMore = async () => {
      await reviewsStore.loadMore()
    }

    onMounted(async () => {
      reviewsStore.reset()
      await reviewsStore.fetchReviews(1)
    })

    return {
      reviews,
      loading,
      hasMore,
      total,
      loadMore,
    }
  },
}
</script>
