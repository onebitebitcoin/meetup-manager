<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-900 py-8">
    <div class="max-w-4xl mx-auto px-4">
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
          과제 관리: {{ meetupName }}
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

      <template v-else>
        <!-- Create/Edit Task Form -->
        <div class="mb-6 p-6 bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700">
          <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
            {{ isEditing ? '과제 수정' : '새 과제 추가' }}
          </h2>
          <form class="space-y-4" @submit.prevent="submitForm">
            <div>
              <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">제목 *</label>
              <input
                v-model="taskForm.title"
                type="text"
                required
                class="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500"
                placeholder="과제 제목을 입력하세요"
              >
            </div>
            <div>
              <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">설명</label>
              <textarea
                v-model="taskForm.description"
                rows="3"
                class="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500"
                placeholder="과제에 대한 상세 설명 (선택)"
              />
            </div>
            <div>
              <label class="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">마감일 *</label>
              <input
                v-model="taskForm.deadline"
                type="datetime-local"
                required
                class="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-700 text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500"
              >
            </div>
            <div class="flex justify-end gap-3">
              <button
                v-if="isEditing"
                type="button"
                class="px-4 py-2 text-neutral-700 dark:text-neutral-300 bg-neutral-100 dark:bg-neutral-700 rounded-lg hover:bg-neutral-200 dark:hover:bg-neutral-600 transition-colors"
                @click="cancelEdit"
              >
                취소
              </button>
              <button
                type="submit"
                :disabled="submitting"
                class="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium transition-colors"
              >
                {{ submitButtonText }}
              </button>
            </div>
          </form>
        </div>

        <!-- Task List -->
        <div class="bg-white dark:bg-neutral-800 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 p-6">
          <h2 class="text-lg font-semibold text-neutral-900 dark:text-neutral-100 mb-4">
            과제 목록
          </h2>

          <!-- Loading Tasks -->
          <div v-if="loadingTasks" class="text-center py-8">
            <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600 mx-auto" />
          </div>

          <!-- Empty State -->
          <div v-else-if="tasks.length === 0" class="text-center py-12">
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
                d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"
              />
            </svg>
            <p class="mt-4 text-neutral-600 dark:text-neutral-400">
              등록된 과제가 없습니다.
            </p>
          </div>

          <!-- Task Items -->
          <div v-else class="space-y-4">
            <div
              v-for="task in tasks"
              :key="task.id"
              class="p-4 bg-beige-50 dark:bg-neutral-700 rounded-lg border border-neutral-200 dark:border-neutral-600"
            >
              <div class="flex items-start justify-between gap-4">
                <div class="flex-1 min-w-0">
                  <div class="flex items-center gap-2 mb-1 flex-wrap">
                    <h3 class="font-semibold text-neutral-900 dark:text-neutral-100">
                      {{ task.title }}
                    </h3>
                    <span
                      v-if="task.is_deadline_soon && !task.is_past_deadline"
                      class="px-2 py-0.5 text-xs font-medium bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200 rounded"
                    >
                      마감 임박
                    </span>
                    <span
                      v-if="task.is_past_deadline"
                      class="px-2 py-0.5 text-xs font-medium bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200 rounded"
                    >
                      마감됨
                    </span>
                  </div>
                  <p v-if="task.description" class="text-sm text-neutral-600 dark:text-neutral-400 mb-2 whitespace-pre-line">
                    {{ task.description }}
                  </p>
                  <div class="flex items-center gap-4 text-xs text-neutral-500">
                    <span>마감: {{ formatDateTime(task.deadline) }}</span>
                    <span>제출: {{ task.submission_count || 0 }}건</span>
                  </div>
                </div>
                <div class="flex items-stretch gap-2 flex-shrink-0">
                  <router-link
                    :to="`/meetup/${meetupId}/tasks/${task.id}/submissions`"
                    class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300 transition-colors"
                  >
                    제출 확인
                  </router-link>
                  <button
                    class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md bg-neutral-100 text-neutral-700 hover:bg-neutral-200 dark:bg-neutral-600 dark:text-neutral-300 transition-colors"
                    @click="startEdit(task)"
                  >
                    수정
                  </button>
                  <button
                    class="inline-flex items-center px-3 py-1.5 text-xs font-medium rounded-md bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 transition-colors"
                    @click="deleteTask(task.id)"
                  >
                    삭제
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </template>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useTasksStore } from '@/stores/tasks'
import { fetchWithCSRF } from '@/utils/csrf'

export default {
  name: 'TaskManageView',
  setup() {
    const route = useRoute()
    const router = useRouter()
    const tasksStore = useTasksStore()

    const meetupId = computed(() => parseInt(route.params.id))
    const meetupName = ref('')
    const loading = ref(true)
    const error = ref('')
    const tasks = ref([])
    const loadingTasks = ref(false)

    // Task form (used for both create and edit)
    const taskForm = ref({
      title: '',
      description: '',
      deadline: '',
    })
    const isEditing = ref(false)
    const editingTaskId = ref(null)
    const submitting = ref(false)

    const submitButtonText = computed(() => {
      if (submitting.value) {
        return isEditing.value ? '수정 중...' : '추가 중...'
      }
      return isEditing.value ? '수정' : '과제 추가'
    })

    const formatDateTime = (dateString) => {
      if (!dateString) return ''
      return new Date(dateString).toLocaleString('ko-KR')
    }

    const fetchMeetupInfo = async () => {
      try {
        const response = await fetchWithCSRF(`/api/meetups/${meetupId.value}/`)
        if (response.ok) {
          const data = await response.json()
          meetupName.value = data.name
        } else {
          error.value = '모임 정보를 불러올 수 없습니다'
        }
      } catch (err) {
        error.value = '모임 정보를 불러오는데 실패했습니다'
      }
    }

    const loadTasks = async () => {
      loadingTasks.value = true
      try {
        const result = await tasksStore.fetchTasks(meetupId.value)
        tasks.value = result
      } catch (err) {
        console.error('Failed to load tasks:', err)
      } finally {
        loadingTasks.value = false
      }
    }

    const formatDateTimeLocal = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      const year = date.getFullYear()
      const month = String(date.getMonth() + 1).padStart(2, '0')
      const day = String(date.getDate()).padStart(2, '0')
      const hours = String(date.getHours()).padStart(2, '0')
      const minutes = String(date.getMinutes()).padStart(2, '0')
      return `${year}-${month}-${day}T${hours}:${minutes}`
    }

    const resetForm = () => {
      taskForm.value = { title: '', description: '', deadline: '' }
      isEditing.value = false
      editingTaskId.value = null
    }

    const submitForm = async () => {
      if (!taskForm.value.title || !taskForm.value.deadline) return
      submitting.value = true
      try {
        if (isEditing.value) {
          await tasksStore.updateTask(editingTaskId.value, {
            title: taskForm.value.title,
            description: taskForm.value.description,
            deadline: taskForm.value.deadline,
          })
        } else {
          await tasksStore.createTask(meetupId.value, {
            title: taskForm.value.title,
            description: taskForm.value.description,
            deadline: taskForm.value.deadline,
          })
        }
        await loadTasks()
        resetForm()
      } catch (err) {
        alert(err.message || (isEditing.value ? '과제 수정에 실패했습니다' : '과제 생성에 실패했습니다'))
      } finally {
        submitting.value = false
      }
    }

    const startEdit = (task) => {
      editingTaskId.value = task.id
      taskForm.value = {
        title: task.title,
        description: task.description || '',
        deadline: formatDateTimeLocal(task.deadline),
      }
      isEditing.value = true
      window.scrollTo({ top: 0, behavior: 'smooth' })
    }

    const cancelEdit = () => {
      resetForm()
    }

    const deleteTask = async (taskId) => {
      if (!confirm('이 과제를 삭제하시겠습니까?')) return
      try {
        await tasksStore.deleteTask(taskId)
        tasks.value = tasks.value.filter(t => t.id !== taskId)
      } catch (err) {
        alert(err.message || '과제 삭제에 실패했습니다')
      }
    }

    const goBack = () => {
      router.push('/settings')
    }

    onMounted(async () => {
      await fetchMeetupInfo()
      await loadTasks()
      loading.value = false
    })

    return {
      meetupId,
      meetupName,
      loading,
      error,
      tasks,
      loadingTasks,
      taskForm,
      isEditing,
      submitting,
      submitButtonText,
      formatDateTime,
      submitForm,
      startEdit,
      cancelEdit,
      deleteTask,
      goBack,
    }
  },
}
</script>
