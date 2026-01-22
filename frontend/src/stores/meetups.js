import { defineStore } from 'pinia'
import { ref } from 'vue'
import { fetchWithCSRF } from '@/utils/csrf'

export const useMeetupsStore = defineStore('meetups', () => {
  const meetups = ref([])
  const loading = ref(false)
  const error = ref('')

  const fetchMeetups = async () => {
    loading.value = true
    error.value = ''
    
    try {
      const response = await fetchWithCSRF('/api/meetups/', {
        method: 'GET',
      })
      
      if (response.ok) {
        const data = await response.json()
        meetups.value = data.map(meetup => ({
          id: meetup.id,
          name: meetup.name,
          description: meetup.description,
          date_time: meetup.date_time,
          end_time: meetup.end_time,
          location: meetup.location,
          max_participants: meetup.max_participants,
          current_participants: meetup.current_participants,
          creator_name: meetup.creator_name,
          creator_email: meetup.creator_email,
          is_full: meetup.is_full,
          available_spots: meetup.available_spots,
          image: meetup.image,
          image_url: meetup.image_url,
          image_display_url: meetup.image_display_url,
          hashtags: meetup.hashtags,
          hashtags_list: meetup.hashtags_list,
        }))
      } else {
        error.value = '모임 데이터를 불러오는데 실패했습니다'
      }
    } catch (err) {
      error.value = '네트워크 오류가 발생했습니다'
    } finally {
      loading.value = false
    }
  }

  const addMeetup = (meetup) => {
    meetups.value.push(meetup)
  }

  const updateMeetup = (id, updatedMeetup) => {
    const index = meetups.value.findIndex(m => m.id === id)
    if (index !== -1) {
      meetups.value[index] = { ...meetups.value[index], ...updatedMeetup }
    }
  }

  const deleteMeetup = (id) => {
    meetups.value = meetups.value.filter(m => m.id !== id)
  }

  const registerForMeetup = async (_meetupId, _userEmail) => {
    // This would need to make an API call to register the user
    // For now, return false as registration is not implemented
    return false
  }

  const unregisterFromMeetup = async (_meetupId, _userEmail) => {
    // This would need to make an API call to unregister the user
    // For now, return false as unregistration is not implemented
    return false
  }

  const isUserRegistered = (_meetupId, _userEmail) => {
    // Since we don't have registration data from API, return false for now
    // This would need to be implemented with a separate API call
    return false
  }

  const addToWaitlist = async (meetupId) => {
    try {
      const response = await fetchWithCSRF(`/api/meetups/${meetupId}/waitlist/`, {
        method: 'POST',
      })
      
      if (response.ok) {
        const data = await response.json()
        await fetchMeetups() // Refresh meetups data
        return data
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to join waitlist')
      }
    } catch (err) {
      throw new Error(err.message || 'Network error occurred')
    }
  }

  const removeFromWaitlist = async (meetupId) => {
    try {
      const response = await fetchWithCSRF(`/api/meetups/${meetupId}/waitlist/remove/`, {
        method: 'DELETE',
      })
      
      if (response.ok) {
        const data = await response.json()
        await fetchMeetups() // Refresh meetups data
        return data
      } else {
        const error = await response.json()
        throw new Error(error.error || 'Failed to leave waitlist')
      }
    } catch (err) {
      throw new Error(err.message || 'Network error occurred')
    }
  }

  const checkWaitlistStatus = async (meetupId) => {
    try {
      const response = await fetchWithCSRF(`/api/meetups/${meetupId}/waitlist/status/`)
      
      if (response.ok) {
        const data = await response.json()
        return data
      } else {
        return { is_waitlisted: false }
      }
    } catch (err) {
      return { is_waitlisted: false }
    }
  }

  const getUserWaitlists = async () => {
    try {
      const response = await fetchWithCSRF('/api/my-waitlists/')
      
      if (response.ok) {
        const data = await response.json()
        return data
      } else {
        throw new Error('Failed to fetch waitlists')
      }
    } catch (err) {
      throw new Error(err.message || 'Network error occurred')
    }
  }

  const getRegistrationCount = (meetupId) => {
    const meetup = meetups.value.find(m => m.id === meetupId)
    return meetup ? meetup.current_participants : 0
  }

  const isMeetupFull = (meetupId) => {
    const meetup = meetups.value.find(m => m.id === meetupId)
    return meetup ? meetup.is_full : false
  }

  return {
    meetups,
    loading,
    error,
    fetchMeetups,
    addMeetup,
    updateMeetup,
    deleteMeetup,
    registerForMeetup,
    unregisterFromMeetup,
    isUserRegistered,
    getRegistrationCount,
    isMeetupFull,
    addToWaitlist,
    removeFromWaitlist,
    checkWaitlistStatus,
    getUserWaitlists,
  }
})