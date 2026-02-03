<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50"
      @click.self="$emit('close')"
    >
      <div class="bg-white dark:bg-neutral-800 rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-hidden flex flex-col">
        <!-- Header -->
        <div class="flex items-center justify-between p-4 border-b border-neutral-200 dark:border-neutral-700">
          <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
            {{ isEdit ? '후기 수정' : '후기 작성' }}
          </h2>
          <button
            class="p-1 text-neutral-500 hover:text-neutral-700 dark:text-neutral-400 dark:hover:text-neutral-200 rounded-md"
            @click="$emit('close')"
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
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        <!-- Meetup Info -->
        <div class="p-4 bg-neutral-50 dark:bg-neutral-900 border-b border-neutral-200 dark:border-neutral-700">
          <div class="flex items-center gap-3">
            <div
              v-if="meetup.image_display_url"
              class="flex-shrink-0 w-12 h-12 rounded-lg overflow-hidden bg-neutral-100 dark:bg-neutral-700"
            >
              <img
                :src="meetup.image_display_url"
                :alt="meetup.name"
                class="w-full h-full object-cover"
              >
            </div>
            <div
              v-else
              class="flex-shrink-0 w-12 h-12 rounded-lg bg-neutral-100 dark:bg-neutral-700 flex items-center justify-center"
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
            <div class="min-w-0">
              <p class="font-medium text-neutral-900 dark:text-neutral-100 truncate">
                {{ meetup.name }}
              </p>
              <p class="text-sm text-neutral-500 dark:text-neutral-400">
                {{ formatDate(meetup.date_time) }}
              </p>
            </div>
          </div>
        </div>

        <!-- Form -->
        <div class="p-4 flex-1 overflow-y-auto space-y-4">
          <!-- Rating -->
          <div>
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">별점</label>
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
                    'w-8 h-8 transition-colors',
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
            </div>
          </div>

          <!-- Content -->
          <div>
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">후기 내용</label>
            <textarea
              v-model="content"
              rows="5"
              maxlength="500"
              placeholder="모임에 대한 후기를 작성해주세요."
              class="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg shadow-sm focus:ring-2 focus:ring-primary-500 focus:border-primary-500 dark:bg-neutral-700 dark:text-neutral-100 dark:placeholder-neutral-400 resize-none"
            />
            <div class="mt-1 text-right text-xs text-neutral-500 dark:text-neutral-400">
              {{ content.length }}/500자
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="flex items-center justify-between gap-3 p-4 border-t border-neutral-200 dark:border-neutral-700 bg-neutral-50 dark:bg-neutral-900">
          <button
            v-if="isEdit"
            type="button"
            :disabled="saving"
            class="px-4 py-2 text-sm font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 disabled:opacity-50"
            @click="handleDelete"
          >
            삭제하기
          </button>
          <div v-else />

          <div class="flex gap-2">
            <button
              type="button"
              class="px-4 py-2 text-sm font-medium text-neutral-700 dark:text-neutral-300 bg-neutral-100 dark:bg-neutral-700 hover:bg-neutral-200 dark:hover:bg-neutral-600 rounded-lg"
              @click="$emit('close')"
            >
              취소
            </button>
            <button
              type="button"
              :disabled="!isValid || saving"
              class="px-4 py-2 text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 disabled:bg-neutral-400 disabled:cursor-not-allowed rounded-lg"
              @click="handleSubmit"
            >
              {{ saving ? '저장 중...' : '저장하기' }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useReviewsStore } from '@/stores/reviews'

export default {
  name: 'ReviewModal',
  props: {
    meetup: {
      type: Object,
      required: true,
    },
    existingReview: {
      type: Object,
      default: null,
    },
  },
  emits: ['close', 'saved'],
  setup(props, { emit }) {
    const reviewsStore = useReviewsStore()

    const rating = ref(props.existingReview?.rating || 5)
    const content = ref(props.existingReview?.content || '')
    const saving = ref(false)

    const isEdit = computed(() => !!props.existingReview)
    const isValid = computed(() => rating.value >= 1 && rating.value <= 5 && content.value.trim().length > 0)

    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      return date.toLocaleDateString('ko-KR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
      })
    }

    const handleSubmit = async () => {
      if (!isValid.value || saving.value) return

      saving.value = true

      const reviewData = {
        rating: rating.value,
        content: content.value.trim(),
      }

      let result
      if (isEdit.value) {
        result = await reviewsStore.updateReview(props.meetup.id, reviewData)
      } else {
        result = await reviewsStore.createReview(props.meetup.id, reviewData)
      }

      saving.value = false

      if (result.success) {
        emit('saved', result.data)
        emit('close')
      } else {
        alert(result.error)
      }
    }

    const handleDelete = async () => {
      if (!confirm('후기를 삭제하시겠습니까?')) return

      saving.value = true
      const result = await reviewsStore.deleteReview(props.meetup.id)
      saving.value = false

      if (result.success) {
        emit('saved', null)
        emit('close')
      } else {
        alert(result.error)
      }
    }

    // ESC key to close
    onMounted(() => {
      const handleKeydown = (e) => {
        if (e.key === 'Escape') {
          emit('close')
        }
      }
      document.addEventListener('keydown', handleKeydown)
      return () => {
        document.removeEventListener('keydown', handleKeydown)
      }
    })

    return {
      rating,
      content,
      saving,
      isEdit,
      isValid,
      formatDate,
      handleSubmit,
      handleDelete,
    }
  },
}
</script>
