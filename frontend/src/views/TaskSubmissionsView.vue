<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-900 py-4 sm:py-8">
    <div class="mx-auto w-full max-w-4xl px-2 sm:px-4 md:px-6">
      <!-- Header with Back Button -->
      <div class="mb-4 sm:mb-6">
        <button
          class="mb-3 inline-flex min-h-[44px] items-center text-neutral-600 transition-colors hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100"
          @click="goBack"
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
        <h1 class="text-xl font-bold text-neutral-900 sm:text-2xl dark:text-neutral-100">
          제출물 검토: {{ task?.title }}
        </h1>
        <p v-if="task" class="mt-1 text-sm text-neutral-500 dark:text-neutral-400">
          마감일: {{ formatDateTime(task.deadline) }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600" />
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="rounded-lg border border-red-200 bg-red-50 p-4 text-center sm:p-6 dark:border-red-800 dark:bg-red-900/20">
        <p class="text-red-800 dark:text-red-200">
          {{ error }}
        </p>
        <button class="mt-4 min-h-[44px] rounded-lg bg-primary-600 px-4 py-2 text-white hover:bg-primary-700" @click="goBack">
          뒤로 가기
        </button>
      </div>

      <!-- Content -->
      <div v-else>
        <div
          v-if="resultMessage"
          :class="getResultMessageClass(resultType)"
          class="mb-3 rounded-lg border px-3 py-2 text-sm"
        >
          {{ resultMessage }}
        </div>

        <!-- Loading Submissions -->
        <div v-if="loadingSubmissions" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" />
        </div>

        <!-- Empty State -->
        <div v-else-if="submissions.length === 0" class="rounded-xl border border-neutral-200 bg-white py-10 text-center dark:border-neutral-700 dark:bg-neutral-800">
          <svg
            class="mx-auto h-12 w-12 text-neutral-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <p class="mt-4 text-neutral-600 dark:text-neutral-400">
            제출된 과제가 없습니다.
          </p>
        </div>

        <!-- Submissions List -->
        <div v-else class="space-y-4">
          <div
            v-for="submission in submissions"
            :key="submission.id"
            class="rounded-xl border border-neutral-200 bg-white p-3 sm:p-4 dark:border-neutral-700 dark:bg-neutral-800"
          >
            <!-- Header -->
            <div class="mb-3 flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
              <div class="min-w-0">
                <div class="font-semibold text-neutral-900 dark:text-neutral-100">
                  {{ submission.user_name }}
                </div>
                <div class="break-words text-sm text-neutral-500">
                  {{ submission.user_email }}
                </div>
                <div class="mt-1 text-xs text-neutral-400">
                  {{ formatDateTime(submission.submitted_at) }}
                </div>
              </div>
              <span
                :class="getStatusClass(submission.status)"
                class="inline-flex w-fit rounded px-2 py-1 text-xs font-medium"
              >
                {{ getStatusText(submission.status) }}
              </span>
            </div>

            <!-- Message -->
            <div class="mb-3 rounded-md bg-neutral-50 p-3 dark:bg-neutral-700/50">
              <p class="break-words whitespace-pre-line text-sm leading-6 text-neutral-700 dark:text-neutral-300">
                {{ submission.message }}
              </p>
            </div>

            <!-- Link -->
            <div v-if="submission.link" class="mb-3">
              <a
                :href="submission.link"
                target="_blank"
                rel="noopener noreferrer"
                :title="submission.link"
                class="inline-flex max-w-full items-center gap-1 text-sm text-blue-600 hover:underline dark:text-blue-400"
              >
                <svg
                  class="h-4 w-4 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
                  />
                </svg>
                <span class="min-w-0 truncate">
                  {{ getCompactLinkText(submission.link) }}
                </span>
              </a>
            </div>

            <!-- File -->
            <div v-if="submission.file_url" class="mb-3">
              <a
                :href="submission.file_url"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex max-w-full items-center gap-1 text-sm text-blue-600 hover:underline dark:text-blue-400"
              >
                <svg
                  class="h-4 w-4 flex-shrink-0"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
                <span class="min-w-0 truncate">{{ submission.file_name || '첨부 파일' }}</span>
              </a>
            </div>

            <!-- Actions -->
            <div v-if="submission.status === 'pending'" class="grid grid-cols-2 gap-2 border-t border-neutral-200 pt-3 dark:border-neutral-700">
              <button
                :disabled="reviewingSubmission"
                class="min-h-[44px] rounded-lg bg-green-100 px-4 py-2 text-sm font-medium text-green-700 transition-colors hover:bg-green-200 disabled:opacity-50 dark:bg-green-900 dark:text-green-300"
                @click="reviewSubmission(submission.id, 'approved')"
              >
                승인
              </button>
              <button
                :disabled="reviewingSubmission"
                class="min-h-[44px] rounded-lg bg-red-100 px-4 py-2 text-sm font-medium text-red-700 transition-colors hover:bg-red-200 disabled:opacity-50 dark:bg-red-900 dark:text-red-300"
                @click="reviewSubmission(submission.id, 'rejected')"
              >
                반려
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTasksStore } from '@/stores/tasks'
import { formatDateTime } from '@/utils/datetime'

export default {
  name: 'TaskSubmissionsView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const tasksStore = useTasksStore()

    const meetupId = computed(() => parseInt(route.params.id))
    const taskId = computed(() => parseInt(route.params.taskId))
    const loading = ref(true)
    const error = ref('')
    const task = ref(null)
    const submissions = ref([])
    const loadingSubmissions = ref(false)
    const reviewingSubmission = ref(false)
    const resultMessage = ref('')
    const resultType = ref('success')
    let resultMessageTimeout = null

    // formatDateTime is imported from @/utils/datetime

    const getStatusText = (status) => {
      const statusMap = {
        pending: '검토 대기',
        approved: '승인됨',
        rejected: '반려됨',
      }
      return statusMap[status] || status
    }

    const getStatusClass = (status) => {
      const classMap = {
        pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
      }
      return classMap[status] || ''
    }

    const getResultMessageClass = (type) => {
      const classMap = {
        success: 'border-green-200 bg-green-50 text-green-800 dark:border-green-800 dark:bg-green-900/20 dark:text-green-200',
        error: 'border-red-200 bg-red-50 text-red-800 dark:border-red-800 dark:bg-red-900/20 dark:text-red-200',
      }
      return classMap[type] || classMap.success
    }

    const showResultMessage = (message, type = 'success') => {
      resultType.value = type
      resultMessage.value = message

      if (resultMessageTimeout) {
        clearTimeout(resultMessageTimeout)
      }

      resultMessageTimeout = setTimeout(() => {
        resultMessage.value = ''
      }, 3000)
    }

    const getCompactLinkText = (link) => {
      if (!link) return ''
      try {
        const parsed = new URL(link)
        return `${parsed.host}${parsed.pathname}`
      } catch (err) {
        return link
      }
    }

    const loadTask = async () => {
      try {
        const tasks = await tasksStore.fetchTasks(meetupId.value)
        task.value = tasks.find(t => t.id === taskId.value)
        if (!task.value) {
          error.value = '과제를 찾을 수 없습니다'
        }
      } catch (err) {
        error.value = '과제 정보를 불러오는데 실패했습니다'
      }
    }

    const loadSubmissions = async () => {
      loadingSubmissions.value = true
      try {
        submissions.value = await tasksStore.fetchSubmissions(taskId.value)
      } catch (err) {
        console.error('Failed to load submissions:', err)
      } finally {
        loadingSubmissions.value = false
      }
    }

    const reviewSubmission = async (submissionId, status) => {
      reviewingSubmission.value = true
      try {
        const updated = await tasksStore.reviewSubmission(submissionId, status)
        const index = submissions.value.findIndex(s => s.id === submissionId)
        if (index !== -1) {
          submissions.value[index] = updated
        }
        showResultMessage(status === 'approved' ? '제출물을 승인했습니다.' : '제출물을 반려했습니다.')
      } catch (err) {
        showResultMessage(err.message || '검토에 실패했습니다', 'error')
      } finally {
        reviewingSubmission.value = false
      }
    }

    const goBack = () => {
      router.push(`/meetup/${meetupId.value}/tasks/manage`)
    }

    onMounted(async () => {
      await loadTask()
      if (!error.value) {
        await loadSubmissions()
      }
      loading.value = false
    })

    return {
      task,
      loading,
      error,
      submissions,
      loadingSubmissions,
      reviewingSubmission,
      resultMessage,
      resultType,
      formatDateTime,
      getStatusText,
      getStatusClass,
      getResultMessageClass,
      getCompactLinkText,
      reviewSubmission,
      goBack,
    }
  },
}
</script>
