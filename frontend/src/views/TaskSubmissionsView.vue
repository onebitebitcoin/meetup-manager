<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-900 py-8">
    <div class="max-w-4xl mx-auto px-4">
      <!-- Header with Back Button -->
      <div class="mb-6">
        <button
          @click="goBack"
          class="flex items-center text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100 transition-colors mb-4"
        >
          <svg class="w-5 h-5 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
          </svg>
          뒤로
        </button>
        <h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
          제출물 검토: {{ task?.title }}
        </h1>
        <p v-if="task" class="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
          마감일: {{ formatDateTime(task.deadline) }}
        </p>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="flex justify-center items-center py-20">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-6 text-center">
        <p class="text-red-800 dark:text-red-200">{{ error }}</p>
        <button @click="goBack" class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700">
          뒤로 가기
        </button>
      </div>

      <!-- Content -->
      <div v-else class="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
        <!-- Loading Submissions -->
        <div v-if="loadingSubmissions" class="text-center py-8">
          <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto"></div>
        </div>

        <!-- Empty State -->
        <div v-else-if="submissions.length === 0" class="text-center py-12">
          <svg class="mx-auto h-12 w-12 text-neutral-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-4 text-neutral-600 dark:text-neutral-400">제출된 과제가 없습니다.</p>
        </div>

        <!-- Submissions List -->
        <div v-else class="space-y-4">
          <div
            v-for="submission in submissions"
            :key="submission.id"
            class="p-4 bg-beige-50 dark:bg-neutral-700 rounded-lg border border-neutral-200 dark:border-neutral-600"
          >
            <!-- Header -->
            <div class="flex items-start justify-between gap-4 mb-3">
              <div>
                <div class="font-semibold text-neutral-900 dark:text-neutral-100">{{ submission.user_name }}</div>
                <div class="text-sm text-neutral-500">{{ submission.user_email }}</div>
                <div class="text-xs text-neutral-400 mt-1">{{ formatDateTime(submission.submitted_at) }}</div>
              </div>
              <span
                :class="getStatusClass(submission.status)"
                class="px-2 py-1 text-xs font-medium rounded flex-shrink-0"
              >
                {{ getStatusText(submission.status) }}
              </span>
            </div>

            <!-- Message -->
            <div class="mb-3 p-3 bg-white dark:bg-neutral-800 rounded">
              <p class="text-sm text-neutral-700 dark:text-neutral-300 whitespace-pre-line">{{ submission.message }}</p>
            </div>

            <!-- Link -->
            <div v-if="submission.link" class="mb-3">
              <a
                :href="submission.link"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center text-sm text-blue-600 dark:text-blue-400 hover:underline break-all"
              >
                <svg class="w-4 h-4 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                </svg>
                {{ submission.link }}
              </a>
            </div>

            <!-- File -->
            <div v-if="submission.file_url" class="mb-3">
              <a
                :href="submission.file_url"
                target="_blank"
                rel="noopener noreferrer"
                class="inline-flex items-center text-sm text-blue-600 dark:text-blue-400 hover:underline"
              >
                <svg class="w-4 h-4 mr-1 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                {{ submission.file_name || '첨부 파일' }}
              </a>
            </div>

            <!-- Actions -->
            <div v-if="submission.status === 'pending'" class="flex gap-2 pt-3 border-t border-neutral-200 dark:border-neutral-600">
              <button
                @click="reviewSubmission(submission.id, 'approved')"
                :disabled="reviewingSubmission"
                class="px-4 py-2 text-sm font-medium rounded-lg bg-green-100 text-green-700 hover:bg-green-200 dark:bg-green-900 dark:text-green-300 disabled:opacity-50 transition-colors"
              >
                승인
              </button>
              <button
                @click="reviewSubmission(submission.id, 'rejected')"
                :disabled="reviewingSubmission"
                class="px-4 py-2 text-sm font-medium rounded-lg bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 disabled:opacity-50 transition-colors"
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

    const formatDateTime = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ko-KR')
    }

    const getStatusText = (status) => {
      const statusMap = {
        pending: '검토 대기',
        approved: '승인됨',
        rejected: '반려됨'
      }
      return statusMap[status] || status
    }

    const getStatusClass = (status) => {
      const classMap = {
        pending: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
        approved: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
        rejected: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
      }
      return classMap[status] || ''
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
      } catch (err) {
        alert(err.message || '검토에 실패했습니다')
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
      formatDateTime,
      getStatusText,
      getStatusClass,
      reviewSubmission,
      goBack
    }
  }
}
</script>
