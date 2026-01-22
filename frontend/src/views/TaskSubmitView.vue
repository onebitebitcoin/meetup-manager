<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-900 py-8">
    <div class="max-w-2xl mx-auto px-4">
      <!-- Header with Back Button -->
      <div class="mb-6">
        <button
          class="flex items-center text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100 transition-colors mb-4"
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
        <h1 class="text-2xl font-bold text-neutral-900 dark:text-neutral-100">
          과제 제출
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
        <button class="mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700" @click="goBack">
          뒤로 가기
        </button>
      </div>

      <!-- Already Submitted State -->
      <div v-else-if="task?.user_submission" class="bg-white dark:bg-neutral-800 rounded-xl shadow-sm p-6 border border-neutral-200 dark:border-neutral-700">
        <div class="text-center py-8">
          <svg
            class="mx-auto h-16 w-16 text-green-500 mb-4"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              stroke-linecap="round"
              stroke-linejoin="round"
              stroke-width="2"
              d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-2">
            이미 제출되었습니다
          </h2>
          <p class="text-neutral-600 dark:text-neutral-400 mb-4">
            현재 상태:
            <span :class="getSubmissionStatusClass(task.user_submission.status)" class="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium">
              {{ getSubmissionStatusText(task.user_submission.status) }}
            </span>
          </p>
          <button class="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700" @click="goBack">
            과제 목록으로
          </button>
        </div>
      </div>

      <!-- Submit Form -->
      <div v-else class="bg-white dark:bg-neutral-800 rounded-xl shadow-sm p-6 border border-neutral-200 dark:border-neutral-700">
        <!-- Task Info -->
        <div class="mb-6 pb-6 border-b border-neutral-200 dark:border-neutral-700">
          <div class="flex items-center flex-wrap gap-2 mb-2">
            <h2 class="text-xl font-semibold text-neutral-900 dark:text-neutral-100">
              {{ task?.title }}
            </h2>
            <span
              v-if="task?.is_deadline_soon && !task?.is_past_deadline"
              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200"
            >
              마감 임박
            </span>
            <span
              v-if="task?.is_past_deadline"
              class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200"
            >
              마감됨
            </span>
          </div>
          <p v-if="task?.description" class="text-neutral-600 dark:text-neutral-400 text-sm mb-3 whitespace-pre-line">
            {{ task.description }}
          </p>
          <p class="text-sm text-neutral-500 dark:text-neutral-500">
            마감일: {{ formatDateTime(task?.deadline) }}
          </p>
        </div>

        <!-- Past Deadline Warning -->
        <div v-if="task?.is_past_deadline" class="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
          <p class="text-red-800 dark:text-red-200 text-center">
            마감일이 지나 제출할 수 없습니다.
          </p>
        </div>

        <!-- Form -->
        <form v-else @submit.prevent="submitTaskCompletion">
          <!-- Message -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              메시지 <span class="text-red-500">*</span>
            </label>
            <textarea
              v-model="submitForm.message"
              rows="4"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="과제에 대한 설명이나 메시지를 입력하세요"
              required
            />
          </div>

          <!-- Link -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              링크 (선택)
            </label>
            <input
              v-model="submitForm.link"
              type="url"
              class="w-full px-4 py-3 rounded-lg border border-neutral-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              placeholder="https://example.com"
            >
          </div>

          <!-- File Upload -->
          <div class="mb-6">
            <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              파일 첨부 (선택)
            </label>
            <div class="relative">
              <input
                ref="fileInput"
                type="file"
                accept=".jpg,.jpeg,.png,.gif,.pdf,.doc,.docx"
                class="hidden"
                @change="handleFileChange"
              >
              <button
                type="button"
                class="w-full px-4 py-3 border-2 border-dashed border-neutral-300 dark:border-neutral-600 rounded-lg text-neutral-600 dark:text-neutral-400 hover:border-primary-500 hover:text-primary-500 transition-colors"
                @click="$refs.fileInput.click()"
              >
                <span v-if="!submitForm.file">파일 선택 (이미지, PDF, 문서)</span>
                <span v-else class="flex items-center justify-center gap-2">
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
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  {{ submitForm.file.name }}
                  <button
                    type="button"
                    class="ml-2 text-red-500 hover:text-red-700"
                    @click.stop="clearFile"
                  >
                    <svg
                      class="w-4 h-4"
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
                </span>
              </button>
            </div>
            <p class="mt-1 text-xs text-neutral-500">
              최대 5MB, jpg, png, gif, pdf, doc, docx
            </p>
          </div>

          <p v-if="!submitForm.link && !submitForm.file" class="mb-4 text-sm text-amber-600 dark:text-amber-400">
            링크 또는 파일 중 하나는 반드시 첨부해야 합니다.
          </p>

          <!-- Error Message -->
          <p v-if="submitError" class="mb-4 text-sm text-red-600 dark:text-red-400">
            {{ submitError }}
          </p>

          <!-- Actions -->
          <div class="flex gap-3">
            <button
              type="button"
              class="flex-1 px-4 py-3 border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
              @click="goBack"
            >
              취소
            </button>
            <button
              type="submit"
              :disabled="submitting || !canSubmit"
              class="flex-1 px-4 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {{ submitting ? '제출 중...' : '제출하기' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTasksStore } from '@/stores/tasks'
import { fetchWithCSRF } from '@/utils/csrf'

export default {
  name: 'TaskSubmitView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const tasksStore = useTasksStore()

    const meetupId = computed(() => parseInt(route.params.id))
    const taskId = computed(() => parseInt(route.params.taskId))
    const loading = ref(true)
    const error = ref('')
    const task = ref(null)

    // Submit form state
    const submitting = ref(false)
    const submitError = ref('')
    const submitForm = ref({
      message: '',
      link: '',
      file: null,
    })
    const fileInput = ref(null)

    const canSubmit = computed(() => {
      return submitForm.value.message && (submitForm.value.link || submitForm.value.file)
    })

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

    const loadTask = async () => {
      loading.value = true
      error.value = ''
      try {
        const tasks = await tasksStore.fetchTasks(meetupId.value)
        task.value = tasks.find(t => t.id === taskId.value)
        if (!task.value) {
          error.value = '과제를 찾을 수 없습니다'
        }
      } catch (err) {
        error.value = err.message || '과제를 불러오는데 실패했습니다'
      } finally {
        loading.value = false
      }
    }

    const goBack = () => {
      router.push(`/meetup/${meetupId.value}/tasks`)
    }

    const handleFileChange = (event) => {
      const file = event.target.files[0]
      if (file) {
        if (file.size > 5 * 1024 * 1024) {
          submitError.value = '파일 크기는 5MB를 초과할 수 없습니다'
          return
        }
        submitForm.value.file = file
        submitError.value = ''
      }
    }

    const clearFile = () => {
      submitForm.value.file = null
      if (fileInput.value) {
        fileInput.value.value = ''
      }
    }

    const submitTaskCompletion = async () => {
      if (!canSubmit.value) return

      submitting.value = true
      submitError.value = ''

      try {
        const formData = new FormData()
        formData.append('message', submitForm.value.message)
        if (submitForm.value.link) {
          formData.append('link', submitForm.value.link)
        }
        if (submitForm.value.file) {
          formData.append('file', submitForm.value.file)
        }

        await tasksStore.submitTask(taskId.value, formData)

        // Navigate back to task list
        router.push(`/meetup/${meetupId.value}/tasks`)
      } catch (err) {
        submitError.value = err.message || '제출에 실패했습니다'
      } finally {
        submitting.value = false
      }
    }

    onMounted(async () => {
      await loadTask()
    })

    return {
      loading,
      error,
      task,
      submitting,
      submitError,
      submitForm,
      fileInput,
      canSubmit,
      formatDateTime,
      getSubmissionStatusText,
      getSubmissionStatusClass,
      goBack,
      handleFileChange,
      clearFile,
      submitTaskCompletion,
    }
  },
}
</script>
