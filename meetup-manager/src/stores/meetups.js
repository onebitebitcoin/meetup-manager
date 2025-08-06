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
        method: 'GET'
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
          is_full: meetup.is_full,
          available_spots: meetup.available_spots
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

  const maskEmail = (email) => {
    const [username, domain] = email.split('@')
    const maskedUsername = username.length > 3 
      ? username.substring(0, 3) + '***'
      : username.substring(0, 1) + '***'
    return `${maskedUsername}@${domain}`
  }

  const registerForMeetup = async (meetupId, userEmail) => {
    // This would need to make an API call to register the user
    // For now, return false as registration is not implemented
    return false
  }

  const unregisterFromMeetup = async (meetupId, userEmail) => {
    // This would need to make an API call to unregister the user
    // For now, return false as unregistration is not implemented
    return false
  }

  const isUserRegistered = (meetupId, userEmail) => {
    // Since we don't have registration data from API, return false for now
    // This would need to be implemented with a separate API call
    return false
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
    isMeetupFull
  }
})