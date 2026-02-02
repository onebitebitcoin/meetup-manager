<template>
  <div
    :class="[
      'py-1.5 px-2 bg-white dark:bg-neutral-800 rounded border border-neutral-200 dark:border-neutral-700 transition-colors',
      isLongContent ? 'cursor-pointer hover:bg-neutral-50 dark:hover:bg-neutral-700/50' : ''
    ]"
    @click="isLongContent && toggle()"
  >
    <!-- Header Row: Rating + Meetup Name + Expand Icon -->
    <div class="flex items-center gap-2 mb-1">
      <!-- Rating -->
      <div class="flex items-center gap-px flex-shrink-0">
        <template v-for="n in 5" :key="n">
          <svg
            :class="[
              'w-2.5 h-2.5',
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
      <!-- Meetup Name -->
      <span class="text-[10px] text-neutral-500 dark:text-neutral-400 truncate flex-1 min-w-0">
        {{ review.meetup_name }}
      </span>
      <!-- Expand/Collapse indicator (only for long content) -->
      <svg
        v-if="isLongContent"
        :class="[
          'w-3 h-3 transition-transform flex-shrink-0',
          expanded ? 'rotate-180' : ''
        ]"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M19 9l-7 7-7-7"
        />
      </svg>
    </div>

    <!-- Content Row -->
    <p
      :class="[
        'text-xs text-neutral-700 dark:text-neutral-300 mb-1 break-words',
        expanded ? 'whitespace-pre-line' : 'line-clamp-2'
      ]"
    >
      {{ review.content }}
    </p>

    <!-- Meta Row -->
    <div class="flex items-center gap-1 text-[10px] text-neutral-400 dark:text-neutral-500">
      <span class="truncate">{{ review.user_name_masked }}</span>
      <span>·</span>
      <span class="flex-shrink-0">{{ review.time_ago }}</span>
    </div>
  </div>
</template>

<script>
import { ref, computed } from 'vue'

export default {
  name: 'ReviewCard',
  props: {
    review: {
      type: Object,
      required: true,
    },
  },
  setup(props) {
    const expanded = ref(false)

    // 내용이 길면 펼치기 가능 (30자 이상)
    const isLongContent = computed(() => {
      return props.review.content && props.review.content.length > 30
    })

    const toggle = () => {
      expanded.value = !expanded.value
    }

    return {
      expanded,
      isLongContent,
      toggle,
    }
  },
}
</script>
