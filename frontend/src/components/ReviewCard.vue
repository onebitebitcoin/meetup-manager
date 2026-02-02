<template>
  <div class="bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 overflow-hidden">
    <div class="p-2.5 flex items-start gap-2.5">
      <!-- Meetup Image -->
      <div
        v-if="review.meetup_image_url"
        class="flex-shrink-0 w-9 h-9 rounded overflow-hidden bg-neutral-100 dark:bg-neutral-700"
      >
        <img
          :src="review.meetup_image_url"
          :alt="review.meetup_name"
          class="w-full h-full object-cover"
          @error="handleImageError"
        >
      </div>
      <div
        v-else
        class="flex-shrink-0 w-9 h-9 rounded bg-neutral-100 dark:bg-neutral-700 flex items-center justify-center"
      >
        <svg
          class="w-4 h-4 text-neutral-400"
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

      <!-- Info & Content -->
      <div class="flex-1 min-w-0">
        <!-- Header row -->
        <div class="flex items-center justify-between gap-2">
          <div class="flex items-center gap-1.5 text-xs min-w-0">
            <span class="font-medium text-neutral-900 dark:text-neutral-100 truncate">{{ review.user_name_masked }}</span>
            <span class="text-neutral-400">·</span>
            <span class="text-neutral-500 dark:text-neutral-400 truncate">{{ review.meetup_name }}</span>
          </div>
          <!-- Rating -->
          <div class="flex items-center gap-0.5 flex-shrink-0">
            <template v-for="n in 5" :key="n">
              <svg
                :class="[
                  'w-3 h-3',
                  n <= review.rating
                    ? 'text-yellow-400'
                    : 'text-neutral-300 dark:text-neutral-600'
                ]"
                fill="currentColor"
                viewBox="0 0 20 20"
              >
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            </template>
          </div>
        </div>
        <!-- Content -->
        <p class="text-xs text-neutral-700 dark:text-neutral-300 leading-relaxed mt-1 line-clamp-2">
          {{ review.content }}
        </p>
        <!-- Footer -->
        <p class="text-[10px] text-neutral-400 dark:text-neutral-500 mt-1">
          {{ review.time_ago }}
        </p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReviewCard',
  props: {
    review: {
      type: Object,
      required: true,
    },
  },
  setup() {
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    }

    const handleImageError = (event) => {
      event.target.style.display = 'none'
    }

    return {
      formatDate,
      handleImageError,
    }
  },
}
</script>
