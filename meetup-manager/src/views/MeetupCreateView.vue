<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-950">
    <!-- Navigation -->
    <nav class="bg-beige-200 dark:bg-neutral-900 border-b border-beige-300 dark:border-neutral-800 safe-area-top">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <div class="flex items-center space-x-3">
              <img 
                src="/icons/logo.png" 
                alt="한입 모임 로고" 
                class="h-8 w-8 rounded-lg"
              />
              <div class="flex items-center space-x-2">
                <div class="p-1 bg-primary-200 dark:bg-primary-800 rounded-lg">
                  <svg class="w-5 h-5 text-primary-600 dark:text-primary-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
                <h1 class="text-lg sm:text-xl font-semibold text-neutral-900 dark:text-neutral-100">
                  새 모임 만들기
                </h1>
              </div>
            </div>
          </div>
          <div class="flex items-center space-x-1 sm:space-x-4">
            <!-- Desktop navigation -->
            <router-link
              to="/dashboard"
              class="hidden sm:block text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 px-3 py-2 rounded-md text-sm font-medium"
            >
              한입 모임
            </router-link>
            
            <!-- Mobile: Dashboard icon -->
            <router-link
              to="/dashboard"
              class="sm:hidden p-1 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300 rounded-md"
              title="한입 모임"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2V7z"></path>
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 5h8"></path>
              </svg>
            </router-link>
            
            <!-- Theme toggle - compact on mobile -->
            <div class="sm:hidden">
              <ThemeToggle />
            </div>
            <div class="hidden sm:block">
              <ThemeToggle />
            </div>
            
            <!-- User name - hidden on mobile -->
            <span class="hidden sm:inline text-slate-800 dark:text-slate-200">{{ authStore.user?.name }}님</span>
            
            <!-- Logout button - compact on mobile -->
            <button
              @click="logout"
              class="bg-red-600 hover:bg-red-700 text-white px-1 sm:px-4 py-1 sm:py-2 rounded-md text-sm font-medium"
            >
              <span class="hidden sm:inline">로그아웃</span>
              <svg class="w-4 h-4 sm:hidden" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <!-- Main Content -->
    <div class="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
      <div class="px-4 py-6 sm:px-0">
        <!-- Header Card -->
        <div class="bg-gradient-to-r from-slate-100 to-gray-100 dark:bg-gradient-to-r dark:from-slate-800 dark:to-gray-800 overflow-hidden shadow rounded-lg mb-6 border border-slate-200 dark:border-slate-600">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="p-3 bg-slate-200 dark:bg-slate-600 rounded-full">
                  <svg class="h-8 w-8 text-slate-600 dark:text-slate-300" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
                  </svg>
                </div>
              </div>
              <div class="ml-5">
                <h3 class="text-lg leading-6 font-medium text-slate-900 dark:text-slate-50">
                  새로운 모임을 만들어보세요
                </h3>
                <p class="mt-1 max-w-2xl text-sm text-slate-700 dark:text-slate-300">
                  사람들과 함께할 멋진 모임을 계획하고 공유하세요.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Form Card -->
        <div class="bg-gradient-to-br from-white to-slate-50 dark:bg-gradient-to-br dark:from-slate-800 dark:to-slate-900 shadow rounded-lg border border-slate-200 dark:border-slate-600">
          <div class="px-4 py-5 sm:p-6">
            <form @submit.prevent="handleSubmit" class="space-y-6">
              <div class="grid grid-cols-1 gap-6">
                <div>
                  <label for="name" class="block text-sm font-medium text-slate-800 dark:text-slate-200">
                    모임 이름 *
                  </label>
                  <input
                    type="text"
                    id="name"
                    v-model="form.name"
                    required
                    placeholder="예: 비트코인 독서 모임"
                    class="mt-1 block w-full px-3 py-3 border-slate-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 dark:placeholder-slate-400 sm:text-base"
                  />
                </div>

                <div>
                  <label for="description" class="block text-sm font-medium text-slate-800 dark:text-slate-200">
                    상세 설명
                  </label>
                  <textarea
                    id="description"
                    v-model="form.description"
                    rows="5"
                    placeholder="모임에 대한 자세한 설명을 작성해주세요..."
                    class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 dark:placeholder-slate-400 sm:text-base resize-y"
                  ></textarea>
                  <p class="mt-2 text-sm text-slate-600 dark:text-slate-300">
                    모임의 목적, 진행 방식, 준비물 등을 포함해주세요.
                  </p>
                </div>

                <!-- Image Upload Section -->
                <div>
                  <label class="block text-sm font-medium text-slate-800 dark:text-slate-200 mb-2">
                    모임 이미지
                  </label>
                  <div class="space-y-4">
                    <!-- Image Upload Options -->
                    <div class="flex flex-col sm:flex-row sm:space-x-4 space-y-3 sm:space-y-0">
                      <!-- File Upload -->
                      <div class="flex-1">
                        <label for="image-upload" class="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">
                          파일 업로드
                        </label>
                        <input
                          type="file"
                          id="image-upload"
                          ref="imageInput"
                          @change="handleImageUpload"
                          accept="image/*"
                          class="block w-full text-sm text-slate-600 dark:text-slate-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-slate-50 file:text-slate-700 hover:file:bg-slate-100 dark:file:bg-slate-600 dark:file:text-slate-300"
                        />
                      </div>
                      
                      <!-- URL Input -->
                      <div class="flex-1">
                        <label for="image-url" class="block text-xs font-medium text-slate-600 dark:text-slate-300 mb-1">
                          또는 이미지 URL
                        </label>
                        <input
                          type="url"
                          id="image-url"
                          v-model="form.imageUrl"
                          placeholder="https://example.com/image.jpg"
                          class="block w-full px-3 py-2 border-gray-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 dark:placeholder-slate-400 text-sm"
                        />
                      </div>
                    </div>

                    <!-- Image Preview -->
                    <div v-if="imagePreview" class="mt-4">
                      <p class="text-sm font-medium text-slate-800 dark:text-slate-200 mb-2">미리보기</p>
                      <div class="relative inline-block">
                        <img 
                          :src="imagePreview" 
                          alt="미리보기" 
                          class="h-32 w-48 object-cover rounded-lg border border-slate-300 dark:border-slate-600"
                          @error="handleImageError"
                        />
                        <button
                          type="button"
                          @click="removeImage"
                          class="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 shadow-md"
                        >
                          <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    </div>
                    
                    <p class="text-xs text-slate-600 dark:text-slate-300">
                      JPG, PNG, GIF 형식의 이미지를 업로드하거나 이미지 URL을 입력하세요. (최대 5MB)
                    </p>
                  </div>
                </div>

                <div>
                  <label for="date" class="block text-sm font-medium text-slate-800 dark:text-slate-200 mb-1">
                    날짜 *
                  </label>
                  <CustomDateInput
                    v-model="form.date"
                    :required="true"
                    :min-date="new Date().toISOString().split('T')[0]"
                  />
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-6">
                  <div>
                    <label for="time" class="block text-sm font-medium text-slate-800 dark:text-slate-200 mb-1">
                      시작 시간 *
                    </label>
                    <CustomTimeSelect
                      v-model="form.time"
                      :required="true"
                    />
                  </div>

                  <div>
                    <label for="duration" class="block text-sm font-medium text-slate-800 dark:text-slate-200">
                      모임 진행 시간 (시간) *
                    </label>
                    <CustomSelect
                      v-model="form.duration"
                      :options="durationOptions"
                      placeholder="진행 시간을 선택하세요"
                      :required="true"
                    />
                    <p class="mt-1 text-xs text-slate-600 dark:text-slate-300">
                      모임이 진행될 시간을 입력하세요
                    </p>
                  </div>
                </div>

                <div>
                  <label for="location" class="block text-sm font-medium text-slate-800 dark:text-slate-200">
                    장소 *
                  </label>
                  <input
                    type="text"
                    id="location"
                    v-model="form.location"
                    required
                    placeholder="예: 동탄 석우동 카페"
                    class="mt-1 block w-full px-3 py-3 border-slate-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 dark:placeholder-slate-400 sm:text-base"
                  />
                </div>

                <div>
                  <label for="max_participants" class="block text-sm font-medium text-slate-800 dark:text-slate-200">
                    최대 참여 인원 *
                  </label>
                  <input
                    type="number"
                    id="max_participants"
                    v-model.number="form.max_participants"
                    min="1"
                    max="100"
                    required
                    class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 sm:text-base"
                  />
                  <p class="mt-2 text-sm text-slate-600 dark:text-slate-300">
                    모임에 참여할 수 있는 최대 인원을 설정해주세요.
                  </p>
                </div>

                <div>
                  <label for="hashtags" class="block text-sm font-medium text-slate-800 dark:text-slate-200">
                    해시태그
                  </label>
                  <input
                    type="text"
                    id="hashtags"
                    v-model="form.hashtags"
                    placeholder="예: #개발,#네트워킹,#스타트업 (쉼표로 구분)"
                    class="mt-1 block w-full px-3 py-3 border-slate-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-slate-700 dark:border-slate-600 dark:text-slate-100 dark:placeholder-slate-400 sm:text-base"
                  />
                  <p class="mt-2 text-sm text-slate-600 dark:text-slate-300">
                    모임과 관련된 해시태그를 쉼표로 구분하여 입력하세요. # 기호는 자동으로 추가됩니다. 최대 5개까지 입력 가능합니다.
                  </p>
                </div>
              </div>

              <div v-if="error" class="rounded-md bg-red-50 dark:bg-red-900 p-4">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <svg class="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div class="ml-3">
                    <p class="text-sm text-red-700 dark:text-red-200">{{ error }}</p>
                  </div>
                </div>
              </div>

              <div class="flex justify-end space-x-3 pt-6 border-t border-slate-200 dark:border-slate-600">
                <button
                  type="button"
                  @click="$router.go(-1)"
                  class="bg-white dark:bg-slate-700 border border-slate-300 dark:border-slate-600 rounded-md shadow-sm py-2 px-4 text-sm font-medium text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500"
                >
                  취소
                </button>
                <button
                  type="submit"
                  :disabled="loading"
                  class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-slate-600 hover:bg-slate-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  {{ loading ? '생성 중...' : '모임 만들기' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'
import ThemeToggle from '@/components/ThemeToggle.vue'
import CustomDateInput from '@/components/CustomDateInput.vue'
import CustomTimeSelect from '@/components/CustomTimeSelect.vue'
import CustomSelect from '@/components/CustomSelect.vue'

export default {
  name: 'MeetupCreateView',
  components: {
    ThemeToggle,
    CustomDateInput,
    CustomTimeSelect,
    CustomSelect
  },
  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const loading = ref(false)
    const error = ref('')

    const form = ref({
      name: '',
      description: '',
      date: '',
      time: '',
      duration: 2,
      location: '',
      max_participants: 10,
      imageUrl: '',
      imageFile: null,
      hashtags: ''
    })

    // Duration options for CustomSelect
    const durationOptions = computed(() => [
      { value: 0.5, label: '30분' },
      { value: 1, label: '1시간' },
      { value: 1.5, label: '1시간 30분' },
      { value: 2, label: '2시간' },
      { value: 2.5, label: '2시간 30분' },
      { value: 3, label: '3시간' },
      { value: 3.5, label: '3시간 30분' },
      { value: 4, label: '4시간' },
      { value: 5, label: '5시간' },
      { value: 6, label: '6시간' },
      { value: 8, label: '8시간' }
    ])

    const imageInput = ref(null)
    const imagePreview = ref('')

    // Image handling functions
    const handleImageUpload = (event) => {
      const file = event.target.files[0]
      if (file) {
        // Check file size (5MB limit)
        if (file.size > 5 * 1024 * 1024) {
          error.value = '이미지 파일 크기가 너무 큽니다. 5MB 이하의 파일을 선택해주세요.'
          return
        }
        
        // Check file type
        if (!file.type.startsWith('image/')) {
          error.value = '이미지 파일만 업로드 가능합니다.'
          return
        }
        
        form.value.imageFile = file
        form.value.imageUrl = '' // Clear URL when file is selected
        
        // Create preview
        const reader = new FileReader()
        reader.onload = (e) => {
          imagePreview.value = e.target.result
        }
        reader.readAsDataURL(file)
        error.value = ''
      }
    }

    // Watch for URL changes to show preview
    const updateImagePreview = () => {
      if (form.value.imageUrl && !form.value.imageFile) {
        imagePreview.value = form.value.imageUrl
      }
    }

    // Watch imageUrl changes
    const unwatchImageUrl = ref(null)
    const watchImageUrl = () => {
      if (unwatchImageUrl.value) unwatchImageUrl.value()
      unwatchImageUrl.value = watch(() => form.value.imageUrl, updateImagePreview)
    }
    
    watchImageUrl()

    const handleImageError = () => {
      imagePreview.value = ''
      if (!form.value.imageFile) {
        error.value = '이미지를 불러올 수 없습니다. URL을 확인해주세요.'
      }
    }

    const removeImage = () => {
      form.value.imageFile = null
      form.value.imageUrl = ''
      imagePreview.value = ''
      if (imageInput.value) {
        imageInput.value.value = ''
      }
    }

    const handleSubmit = async () => {
      loading.value = true
      error.value = ''

      try {
        // Check if user is authenticated
        if (!authStore.isLoggedIn) {
          error.value = '로그인이 필요합니다'
          return
        }

        const dateTime = `${form.value.date}T${form.value.time}:00`
        
        // Calculate end time from start time and duration
        const startDate = new Date(dateTime)
        const endDate = new Date(startDate.getTime() + (form.value.duration * 60 * 60 * 1000))
        const endDateTime = endDate.toISOString()
        
        // Process hashtags - ensure they start with # and are comma-separated
        let processedHashtags = ''
        if (form.value.hashtags.trim()) {
          const hashtags = form.value.hashtags.split(',')
            .map(tag => tag.trim())
            .filter(tag => tag.length > 0)
            .map(tag => tag.startsWith('#') ? tag : '#' + tag)
          if (hashtags.length > 5) {
            error.value = '해시태그는 최대 5개까지 입력할 수 있습니다.'
            loading.value = false
            return
          }
          processedHashtags = hashtags.join(',')
        }

        // Prepare meetup data
        const meetupData = {
          name: form.value.name,
          description: form.value.description,
          date_time: new Date(dateTime).toISOString(),
          end_time: endDateTime,
          location: form.value.location,
          max_participants: form.value.max_participants,
          hashtags: processedHashtags
        }

        // Add image URL if provided and no file is selected
        if (form.value.imageUrl && !form.value.imageFile) {
          meetupData.image_url = form.value.imageUrl
        }

        console.log('Creating meetup with data:', meetupData)
        console.log('User auth status:', authStore.isLoggedIn)
        console.log('User data:', authStore.user)

        // Use FormData if there's an image file, otherwise JSON
        let response
        if (form.value.imageFile) {
          const formData = new FormData()
          
          // Add all meetup data to FormData
          Object.keys(meetupData).forEach(key => {
            formData.append(key, meetupData[key])
          })
          
          // Add image file
          formData.append('image', form.value.imageFile)
          
          response = await fetchWithCSRF('/api/meetups/', {
            method: 'POST',
            body: formData
          })
        } else {
          response = await fetchWithCSRF('/api/meetups/', {
            method: 'POST',
            body: JSON.stringify(meetupData)
          })
        }

        console.log('Response status:', response.status)
        console.log('Response headers:', response.headers)

        if (response.ok) {
          router.push('/settings?message=모임이 성공적으로 생성되었습니다')
        } else {
          const responseText = await response.text()
          console.error('Error response:', responseText)
          
          try {
            const data = JSON.parse(responseText)
            error.value = data.error || data.detail || '모임 생성에 실패했습니다'
          } catch {
            error.value = `서버 오류 (${response.status}): ${responseText || '모임 생성에 실패했습니다'}`
          }
        }
      } catch (err) {
        console.error('Network error:', err)
        error.value = '네트워크 오류가 발생했습니다. 다시 시도해주세요.'
      } finally {
        loading.value = false
      }
    }

    const logout = async () => {
      await authStore.logout()
      router.push('/login')
    }

    return {
      authStore,
      form,
      loading,
      error,
      handleSubmit,
      logout,
      imageInput,
      imagePreview,
      handleImageUpload,
      handleImageError,
      removeImage,
      durationOptions
    }
  }
}
</script>
