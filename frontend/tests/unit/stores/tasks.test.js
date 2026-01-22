/**
 * Unit tests for tasks store
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useTasksStore } from '@/stores/tasks'

// Mock fetchWithCSRF
const mockFetchWithCSRF = vi.fn()
vi.mock('@/utils/csrf', () => ({
  fetchWithCSRF: (...args) => mockFetchWithCSRF(...args)
}))

describe('Tasks Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useTasksStore()
    vi.clearAllMocks()
  })

  describe('initial state', () => {
    it('should have empty tasks array initially', () => {
      expect(store.tasks).toEqual([])
    })

    it('should have loading as false initially', () => {
      expect(store.loading).toBe(false)
    })

    it('should have empty error initially', () => {
      expect(store.error).toBe('')
    })
  })

  describe('fetchTasks', () => {
    it('should fetch tasks for a meetup', async () => {
      const mockTasks = [
        { id: 1, title: 'Task 1' },
        { id: 2, title: 'Task 2' }
      ]

      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ tasks: mockTasks })
      })

      const result = await store.fetchTasks(1)

      expect(result).toHaveLength(2)
      expect(store.tasks).toHaveLength(2)
      expect(mockFetchWithCSRF).toHaveBeenCalledWith('/api/meetups/1/tasks/')
    })

    it('should set loading state during fetch', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ tasks: [] })
      })

      const fetchPromise = store.fetchTasks(1)
      expect(store.loading).toBe(true)

      await fetchPromise
      expect(store.loading).toBe(false)
    })

    it('should set error on fetch failure', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: false,
        json: () => Promise.resolve({ error: 'Failed to fetch' })
      })

      await store.fetchTasks(1)

      expect(store.error).not.toBe('')
    })
  })

  describe('createTask', () => {
    it('should create a new task', async () => {
      const newTask = { id: 1, title: 'New Task' }

      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(newTask)
      })

      const result = await store.createTask(1, { title: 'New Task' })

      expect(result).toEqual(newTask)
      expect(store.tasks[0]).toEqual(newTask)
    })

    it('should throw error on create failure', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: false,
        json: () => Promise.resolve({ error: 'Creation failed' })
      })

      await expect(store.createTask(1, { title: 'Task' })).rejects.toThrow()
    })
  })

  describe('updateTask', () => {
    it('should update an existing task', async () => {
      store.tasks = [{ id: 1, title: 'Old Title' }]
      const updatedTask = { id: 1, title: 'New Title' }

      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(updatedTask)
      })

      const result = await store.updateTask(1, { title: 'New Title' })

      expect(result.title).toBe('New Title')
      expect(store.tasks[0].title).toBe('New Title')
    })
  })

  describe('deleteTask', () => {
    it('should delete a task', async () => {
      store.tasks = [
        { id: 1, title: 'Task 1' },
        { id: 2, title: 'Task 2' }
      ]

      mockFetchWithCSRF.mockResolvedValue({ ok: true })

      await store.deleteTask(1)

      expect(store.tasks).toHaveLength(1)
      expect(store.tasks[0].id).toBe(2)
    })
  })

  describe('submitTask', () => {
    it('should submit a task', async () => {
      store.tasks = [{ id: 1, title: 'Task' }]
      const submission = { id: 1, status: 'pending', submitted_at: '2024-01-01' }

      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(submission)
      })

      const formData = new FormData()
      formData.append('message', 'My submission')

      const result = await store.submitTask(1, formData)

      expect(result.status).toBe('pending')
      expect(store.tasks[0].user_submission).toBeDefined()
    })

    it('should throw error on submission failure', async () => {
      mockFetchWithCSRF.mockResolvedValue({
        ok: false,
        json: () => Promise.resolve({ error: 'Already submitted' })
      })

      await expect(store.submitTask(1, new FormData())).rejects.toThrow()
    })
  })

  describe('fetchSubmissions', () => {
    it('should fetch submissions for a task', async () => {
      const mockSubmissions = [
        { id: 1, user_name: 'User 1', status: 'pending' },
        { id: 2, user_name: 'User 2', status: 'approved' }
      ]

      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ submissions: mockSubmissions })
      })

      const result = await store.fetchSubmissions(1)

      expect(result).toHaveLength(2)
    })
  })

  describe('reviewSubmission', () => {
    it('should review and approve a submission', async () => {
      const reviewedSubmission = { id: 1, status: 'approved' }

      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(reviewedSubmission)
      })

      const result = await store.reviewSubmission(1, 'approved')

      expect(result.status).toBe('approved')
      expect(mockFetchWithCSRF).toHaveBeenCalledWith(
        '/api/submissions/1/review/',
        {
          method: 'PUT',
          body: JSON.stringify({ status: 'approved' })
        }
      )
    })

    it('should review and reject a submission', async () => {
      const reviewedSubmission = { id: 1, status: 'rejected' }

      mockFetchWithCSRF.mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(reviewedSubmission)
      })

      const result = await store.reviewSubmission(1, 'rejected')

      expect(result.status).toBe('rejected')
    })
  })

  describe('clearTasks', () => {
    it('should clear tasks and error', () => {
      store.tasks = [{ id: 1 }, { id: 2 }]
      store.error = 'Some error'

      store.clearTasks()

      expect(store.tasks).toEqual([])
      expect(store.error).toBe('')
    })
  })
})
