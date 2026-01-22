import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchWithCSRF } from '@/utils/csrf'

export const useTasksStore = defineStore('tasks', () => {
  const tasks = ref([])
  const loading = ref(false)
  const error = ref('')

  const fetchTasks = async (meetupId) => {
    loading.value = true
    error.value = ''
    try {
      const response = await fetchWithCSRF(`/api/meetups/${meetupId}/tasks/`)
      if (response.ok) {
        const data = await response.json()
        tasks.value = data.tasks || []
        return tasks.value
      } else {
        const errorData = await response.json()
        error.value = errorData.error || '과제를 불러오는데 실패했습니다'
        return []
      }
    } catch (err) {
      error.value = '네트워크 오류가 발생했습니다'
      return []
    } finally {
      loading.value = false
    }
  }

  const createTask = async (meetupId, taskData) => {
    try {
      const response = await fetchWithCSRF(`/api/meetups/${meetupId}/tasks/`, {
        method: 'POST',
        body: JSON.stringify(taskData)
      })
      if (response.ok) {
        const data = await response.json()
        tasks.value.unshift(data)
        return data
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || '과제 생성에 실패했습니다')
      }
    } catch (err) {
      throw new Error(err.message || '네트워크 오류가 발생했습니다')
    }
  }

  const updateTask = async (taskId, taskData) => {
    try {
      const response = await fetchWithCSRF(`/api/tasks/${taskId}/`, {
        method: 'PUT',
        body: JSON.stringify(taskData)
      })
      if (response.ok) {
        const data = await response.json()
        const index = tasks.value.findIndex(t => t.id === taskId)
        if (index !== -1) {
          tasks.value[index] = data
        }
        return data
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || '과제 수정에 실패했습니다')
      }
    } catch (err) {
      throw new Error(err.message || '네트워크 오류가 발생했습니다')
    }
  }

  const deleteTask = async (taskId) => {
    try {
      const response = await fetchWithCSRF(`/api/tasks/${taskId}/`, {
        method: 'DELETE'
      })
      if (response.ok) {
        tasks.value = tasks.value.filter(t => t.id !== taskId)
        return true
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || '과제 삭제에 실패했습니다')
      }
    } catch (err) {
      throw new Error(err.message || '네트워크 오류가 발생했습니다')
    }
  }

  const submitTask = async (taskId, formData) => {
    try {
      const response = await fetchWithCSRF(`/api/tasks/${taskId}/submit/`, {
        method: 'POST',
        body: formData
      })
      if (response.ok) {
        const data = await response.json()
        // Update task's user_submission in local state
        const taskIndex = tasks.value.findIndex(t => t.id === taskId)
        if (taskIndex !== -1) {
          tasks.value[taskIndex].user_submission = {
            id: data.id,
            status: data.status,
            submitted_at: data.submitted_at
          }
        }
        return data
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || '과제 제출에 실패했습니다')
      }
    } catch (err) {
      throw new Error(err.message || '네트워크 오류가 발생했습니다')
    }
  }

  const fetchSubmissions = async (taskId) => {
    try {
      const response = await fetchWithCSRF(`/api/tasks/${taskId}/submissions/`)
      if (response.ok) {
        const data = await response.json()
        return data.submissions || []
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || '제출물을 불러오는데 실패했습니다')
      }
    } catch (err) {
      throw new Error(err.message || '네트워크 오류가 발생했습니다')
    }
  }

  const reviewSubmission = async (submissionId, status) => {
    try {
      const response = await fetchWithCSRF(`/api/submissions/${submissionId}/review/`, {
        method: 'PUT',
        body: JSON.stringify({ status })
      })
      if (response.ok) {
        return await response.json()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.error || '검토에 실패했습니다')
      }
    } catch (err) {
      throw new Error(err.message || '네트워크 오류가 발생했습니다')
    }
  }

  const clearTasks = () => {
    tasks.value = []
    error.value = ''
  }

  return {
    tasks,
    loading,
    error,
    fetchTasks,
    createTask,
    updateTask,
    deleteTask,
    submitTask,
    fetchSubmissions,
    reviewSubmission,
    clearTasks
  }
})
