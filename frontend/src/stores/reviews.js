import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchWithCSRF } from '@/utils/csrf'

export const useReviewsStore = defineStore('reviews', () => {
  const reviews = ref([])
  const recentReviews = ref([])
  const attendedMeetups = ref([])
  const loading = ref(false)
  const error = ref('')
  const currentPage = ref(1)
  const hasMore = ref(true)
  const total = ref(0)

  /**
   * 후기 피드 조회 (페이지네이션)
   */
  const fetchReviews = async (page = 1, pageSize = 10) => {
    loading.value = true
    error.value = ''

    try {
      const response = await fetch(`/api/reviews/?page=${page}&page_size=${pageSize}`, {
        credentials: 'include',
      })

      if (response.ok) {
        const data = await response.json()
        if (page === 1) {
          reviews.value = data.reviews
        } else {
          reviews.value = [...reviews.value, ...data.reviews]
        }
        currentPage.value = data.page
        hasMore.value = data.has_more
        total.value = data.total
      } else {
        error.value = '후기를 불러오는데 실패했습니다'
      }
    } catch (err) {
      error.value = '네트워크 오류가 발생했습니다'
      console.error('Failed to fetch reviews:', err)
    } finally {
      loading.value = false
    }
  }

  /**
   * 최근 후기 조회 (대시보드용)
   */
  const fetchRecentReviews = async () => {
    try {
      const response = await fetch('/api/reviews/recent/', {
        credentials: 'include',
      })

      if (response.ok) {
        const data = await response.json()
        recentReviews.value = data.reviews
      }
    } catch (err) {
      console.error('Failed to fetch recent reviews:', err)
    }
  }

  /**
   * 참석한 밋업 목록 조회 (종료된 밋업만)
   */
  const fetchAttendedMeetups = async () => {
    try {
      const response = await fetchWithCSRF('/api/my-attended-meetups/')

      if (response.ok) {
        const data = await response.json()
        attendedMeetups.value = data.meetups
        return { success: true, meetups: data.meetups }
      } else {
        return { success: false, error: '참석 밋업을 불러오는데 실패했습니다' }
      }
    } catch (err) {
      console.error('Failed to fetch attended meetups:', err)
      return { success: false, error: '네트워크 오류가 발생했습니다' }
    }
  }

  /**
   * 내 후기 조회
   */
  const getMyReview = async (meetupId) => {
    try {
      const response = await fetchWithCSRF(`/api/meetups/${meetupId}/review/`)

      if (response.ok) {
        return await response.json()
      }
      return null
    } catch (err) {
      console.error('Failed to get my review:', err)
      return null
    }
  }

  /**
   * 후기 작성
   */
  const createReview = async (meetupId, reviewData) => {
    try {
      const response = await fetchWithCSRF(`/api/meetups/${meetupId}/review/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reviewData),
      })

      if (response.ok) {
        const data = await response.json()
        // 최근 후기 목록 갱신
        await fetchRecentReviews()
        return { success: true, data }
      } else {
        const errorData = await response.json()
        return { success: false, error: errorData.error || '후기 작성에 실패했습니다' }
      }
    } catch (err) {
      console.error('Failed to create review:', err)
      return { success: false, error: '네트워크 오류가 발생했습니다' }
    }
  }

  /**
   * 후기 수정
   */
  const updateReview = async (meetupId, reviewData) => {
    try {
      const response = await fetchWithCSRF(`/api/meetups/${meetupId}/review/`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(reviewData),
      })

      if (response.ok) {
        const data = await response.json()
        // 최근 후기 목록 갱신
        await fetchRecentReviews()
        return { success: true, data }
      } else {
        const errorData = await response.json()
        return { success: false, error: errorData.error || '후기 수정에 실패했습니다' }
      }
    } catch (err) {
      console.error('Failed to update review:', err)
      return { success: false, error: '네트워크 오류가 발생했습니다' }
    }
  }

  /**
   * 후기 삭제
   */
  const deleteReview = async (meetupId) => {
    try {
      const response = await fetchWithCSRF(`/api/meetups/${meetupId}/review/`, {
        method: 'DELETE',
      })

      if (response.ok) {
        // 최근 후기 목록 갱신
        await fetchRecentReviews()
        return { success: true }
      } else {
        const errorData = await response.json()
        return { success: false, error: errorData.error || '후기 삭제에 실패했습니다' }
      }
    } catch (err) {
      console.error('Failed to delete review:', err)
      return { success: false, error: '네트워크 오류가 발생했습니다' }
    }
  }

  /**
   * 더 많은 후기 불러오기
   */
  const loadMore = async () => {
    if (!hasMore.value || loading.value) return
    await fetchReviews(currentPage.value + 1)
  }

  /**
   * 목록 초기화
   */
  const reset = () => {
    reviews.value = []
    currentPage.value = 1
    hasMore.value = true
    total.value = 0
  }

  return {
    reviews,
    recentReviews,
    attendedMeetups,
    loading,
    error,
    currentPage,
    hasMore,
    total,
    fetchReviews,
    fetchRecentReviews,
    fetchAttendedMeetups,
    getMyReview,
    createReview,
    updateReview,
    deleteReview,
    loadMore,
    reset,
  }
})
