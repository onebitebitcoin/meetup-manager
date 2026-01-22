<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-900 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <!-- Header with Back Button -->
      <div class="mb-6">
        <button
          class="flex items-center text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100 transition-colors mb-4"
          @click="$router.push(`/meetup/${meetupId}`)"
        >
          <svg
            class="w-5 h-5 mr-1"
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
          뒤로
        </button>
        <h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
          {{ meetupName }} - 과제 목록
        </h1>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <p class="text-red-800 dark:text-red-200">
          {{ error }}
        </p>
        <button class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700" @click="$router.push('/dashboard')">
          대시보드로 돌아가기
        </button>
      </div>

      <!-- Empty State -->
      <div v-else-if="tasks.length === 0" class="text-center py-20">
        <svg
          class="mx-auto h-16 w-16 text-neutral-400"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
          />
        </svg>
        <p class="mt-4 text-neutral-600 dark:text-neutral-400">
          등록된 과제가 없습니다.
        </p>
      </div>

      <!-- Task List -->
      <div v-else class="space-y-4">
        <div
          v-for="task in tasks"
          :key="task.id"
          class="bg-white dark:bg-neutral-800 rounded-xl shadow-sm p-6 border border-neutral-200 dark:border-neutral-700"
        >
          <div class="flex items-start justify-between gap-4">
            <div class="flex-1 min-w-0">
              <div class="flex items-center flex-wrap gap-2 mb-2">
                <h3 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                  {{ task.title }}
                </h3>
                <!-- Deadline Soon Badge -->
                <span
                  v-if="task.is_deadline_soon && !task.is_past_deadline"
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200"
                >
                  마감 임박
                </span>
                <!-- Past Deadline Badge -->
                <span
                  v-if="task.is_past_deadline"
                  class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
                >
                  마감됨
                </span>
              </div>
              <p v-if="task.description" class="text-neutral-600 dark:text-neutral-400 text-sm mb-3 whitespace-pre-line">
                {{ task.description }}
              </p>
              <p class="text-sm text-neutral-500 dark:text-neutral-500">
                마감일: {{ formatDateTime(task.deadline) }}
              </p>
            </div>

            <!-- Submission Status / Action -->
            <div class="flex-shrink-0">
              <template v-if="task.user_submission">
                <span
                  :class="getSubmissionStatusClass(task.user_submission.status)"
                  class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium"
                >
                  {{ getSubmissionStatusText(task.user_submission.status) }}
                </span>
              </template>
              <template v-else>
                <router-link
                  :to="`/meetup/${meetupId}/tasks/${task.id}/submit`"
                  :class="[
                    'px-4 py-2 rounded-lg text-sm font-medium transition-colors inline-block',
                    task.is_past_deadline
                      ? 'bg-neutral-300 text-neutral-500 cursor-not-allowed pointer-events-none'
                      : 'bg-primary-600 text-white hover:bg-primary-700'
                  ]"
                >
                  완료하기
                </router-link>
              </template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useTasksStore } from '@/stores/tasks'
import { fetchWithCSRF } from '@/utils/csrf'

export default {
  name: 'TaskListView',
  setup() {
    const route = useRoute()
    const tasksStore = useTasksStore()

    const meetupId = computed(() => parseInt(route.params.id))
    const meetupName = ref('')
    const loading = ref(true)
    const error = ref('')
    const tasks = ref([])

    const formatDateTime = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ko-KR')
    }

    const getSubmissionStatusText = (status) => {
      const statusMap = {
        pending: '검토 대기',
        approved: '승인됨',
        rejected: '반려됨',
      }
      return statusMap[status] || status
    }

    const getSubmissionStatusClass = (status) => {
      const classMap = {
        pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      }
      return classMap[status] || ''
    }

    const fetchMeetupInfo = async () => {
      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId.value}/`)
        if (response.ok) {
          const data = await response.json()
          meetupName.value = data.name
        }
      } catch (err) {
        console.error('Failed to fetch meetup info:', err)
      }
    }

    const loadTasks = async () => {
      loading.value = true
      error.value = ''
      try {
        const result = await tasksStore.fetchTasks(meetupId.value)
        tasks.value = result
        if (tasksStore.error) {
          error.value = tasksStore.error
        }
      } catch (err) {
        error.value = err.message || '과제를 불러오는데 실패했습니다'
      } finally {
        loading.value = false
      }
    }

    onMounted(async () => {
      await fetchMeetupInfo()
      await loadTasks()
    })

    return {
      meetupId,
      meetupName,
      loading,
      error,
      tasks,
      formatDateTime,
      getSubmissionStatusText,
      getSubmissionStatusClass,
    }
  },
}
</script>
