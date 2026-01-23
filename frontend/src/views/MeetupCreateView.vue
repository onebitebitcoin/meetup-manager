<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-950">
    <!-- Navigation -->
    <nav class="bg-beige-200 dark:bg-neutral-900 border-b border-beige-300 dark:border-neutral-800 safe-area-top">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex items-center">
            <div class="flex items-center space-x-3">
              <img
                src="/icons/logo-transparent.svg"
                alt="한입 모임 로고"
                class="h-8 w-8"
              >
              <div class="flex items-center space-x-2">
                <div class="p-1 bg-primary-200 dark:bg-primary-800 rounded-lg">
                  <svg
                    class="w-5 h-5 text-primary-600 dark:text-primary-300"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    />
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
                  d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2H5a2 2 0 00-2-2V7z"
                />
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 5h8"
                />
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
            <span class="hidden sm:inline text-slate-800 dark:text-neutral-200">{{ authStore.user?.name }}님</span>
            
            <!-- Logout button - compact on mobile -->
            <button
              class="bg-red-600 hover:bg-red-700 text-white px-1 sm:px-4 py-1 sm:py-2 rounded-md text-sm font-medium"
              @click="logout"
            >
              <span class="hidden sm:inline">로그아웃</span>
              <svg
                class="w-4 h-4 sm:hidden"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"
                />
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
        <div class="bg-gradient-to-r from-slate-100 to-gray-100 dark:bg-gradient-to-r dark:from-neutral-800 dark:to-neutral-800 overflow-hidden shadow rounded-lg mb-6 border border-slate-200 dark:border-neutral-600">
          <div class="px-4 py-5 sm:p-6">
            <div class="flex items-center">
              <div class="flex-shrink-0">
                <div class="p-3 bg-slate-200 dark:bg-neutral-600 rounded-full">
                  <svg
                    class="h-8 w-8 text-slate-600 dark:text-neutral-300"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 6v6m0 0v6m0-6h6m-6 0H6"
                    />
                  </svg>
                </div>
              </div>
              <div class="ml-5">
                <h3 class="text-lg leading-6 font-medium text-slate-900 dark:text-neutral-50">
                  새로운 모임을 만들어보세요
                </h3>
                <p class="mt-1 max-w-2xl text-sm text-slate-700 dark:text-neutral-300">
                  사람들과 함께할 멋진 모임을 계획하고 공유하세요.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Form Card -->
        <div class="bg-gradient-to-br from-white to-slate-50 dark:bg-gradient-to-br dark:from-neutral-800 dark:to-neutral-900 shadow rounded-lg border border-slate-200 dark:border-neutral-600">
          <div class="px-4 py-5 sm:p-6">
            <form class="space-y-6" @submit.prevent="handleSubmit">
              <div class="grid grid-cols-1 gap-6">
                <div>
                  <label for="name" class="block text-sm font-medium text-slate-800 dark:text-neutral-200">
                    모임 이름 *
                  </label>
                  <input
                    id="name"
                    v-model="form.name"
                    type="text"
                    required
                    placeholder="예: 비트코인 독서 모임"
                    class="mt-1 block w-full px-3 py-3 border-slate-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-neutral-700 dark:border-neutral-600 dark:text-neutral-100 dark:placeholder-neutral-400 sm:text-base"
                  >
                </div>

                <div>
                  <label for="description" class="block text-sm font-medium text-slate-800 dark:text-neutral-200">
                    상세 설명
                  </label>
                  <textarea
                    id="description"
                    v-model="form.description"
                    rows="5"
                    placeholder="모임에 대한 자세한 설명을 작성해주세요..."
                    class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-neutral-700 dark:border-neutral-600 dark:text-neutral-100 dark:placeholder-neutral-400 sm:text-base resize-y"
                  />
                  <p class="mt-2 text-sm text-slate-600 dark:text-neutral-300">
                    모임의 목적, 진행 방식, 준비물 등을 포함해주세요.
                  </p>
                </div>

                <!-- Image Upload Section -->
                <div>
                  <label class="block text-sm font-medium text-slate-800 dark:text-neutral-200 mb-2">
                    모임 이미지
                  </label>
                  <div class="space-y-4">
                    <!-- Image Upload Options -->
                    <div class="flex flex-col sm:flex-row sm:space-x-4 space-y-3 sm:space-y-0">
                      <!-- File Upload -->
                      <div class="flex-1">
                        <label for="image-upload" class="block text-xs font-medium text-slate-600 dark:text-neutral-300 mb-1">
                          파일 업로드
                        </label>
                        <input
                          id="image-upload"
                          ref="imageInput"
                          type="file"
                          accept="image/*"
                          class="block w-full text-sm text-slate-600 dark:text-neutral-300 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:text-sm file:font-medium file:bg-slate-50 file:text-slate-700 hover:file:bg-slate-100 dark:file:bg-neutral-600 dark:file:text-neutral-300"
                          @change="handleImageUpload"
                        >
                      </div>
                      
                      <!-- URL Input -->
                      <div class="flex-1">
                        <label for="image-url" class="block text-xs font-medium text-slate-600 dark:text-neutral-300 mb-1">
                          또는 이미지 URL
                        </label>
                        <input
                          id="image-url"
                          v-model="form.imageUrl"
                          type="url"
                          placeholder="https://example.com/image.jpg"
                          class="block w-full px-3 py-2 border-gray-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-neutral-700 dark:border-neutral-600 dark:text-neutral-100 dark:placeholder-neutral-400 text-sm"
                        >
                      </div>
                    </div>

                    <!-- Image Preview -->
                    <div v-if="imagePreview" class="mt-4">
                      <p class="text-sm font-medium text-slate-800 dark:text-neutral-200 mb-2">
                        미리보기 
                        <span class="text-xs text-slate-500 dark:text-neutral-400">(이미지를 드래그하여 위치 조정)</span>
                      </p>
                      
                      <!-- Interactive Image Preview Container -->
                      <div class="relative inline-block">
                        <!-- Image Container with Drag Interaction -->
                        <div 
                          ref="imageContainer"
                          class="relative w-48 h-32 bg-gray-100 dark:bg-neutral-800 rounded-lg border-2 border-slate-300 dark:border-neutral-600 overflow-hidden cursor-move group"
                          :class="{ 'border-blue-500 dark:border-blue-400': isDragging }"
                          @mousedown="startDrag"
                          @mousemove="onDrag"
                          @mouseup="endDrag"
                          @mouseleave="endDrag"
                        >
                          <!-- Preview Image -->
                          <img 
                            :src="imagePreview" 
                            alt="미리보기"
                            class="absolute w-full h-full object-cover pointer-events-none select-none transition-all duration-200 ease-out"
                            :style="{ 
                              objectPosition: `${imageOffsetX}% ${imageOffsetY}%`,
                              transform: isDragging ? 'scale(1.02)' : 'scale(1)'
                            }"
                            draggable="false"
                            @error="handleImageError"
                          >
                          
                          <!-- Drag Overlay -->
                          <div 
                            v-if="isDragging"
                            class="absolute inset-0 bg-blue-500 bg-opacity-10 pointer-events-none"
                          />
                          
                          <!-- Position Indicator -->
                          <div 
                            class="absolute top-1 left-1 bg-black bg-opacity-50 text-white text-xs px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity"
                          >
                            {{ Math.round(imageOffsetX) }}%, {{ Math.round(imageOffsetY) }}%
                          </div>
                        </div>
                        
                        <!-- Remove Button -->
                        <button
                          type="button"
                          class="absolute -top-2 -right-2 bg-red-500 hover:bg-red-600 text-white rounded-full p-1 shadow-md z-10"
                          @click="removeImage"
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
                        
                        <!-- Reset Position Button -->
                        <button
                          type="button"
                          class="absolute -bottom-2 -right-2 bg-gray-500 hover:bg-gray-600 text-white rounded-full p-1 shadow-md text-xs"
                          title="위치 초기화"
                          @click="resetImagePosition"
                        >
                          <svg
                            class="w-3 h-3"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                          >
                            <path
                              stroke-linecap="round"
                              stroke-linejoin="round"
                              stroke-width="2"
                              d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                            />
                          </svg>
                        </button>
                      </div>
                      
                      <!-- Position Info -->
                      <div class="mt-2 text-xs text-slate-500 dark:text-neutral-400">
                        현재 위치: X{{ Math.round(imageOffsetX) }}%, Y{{ Math.round(imageOffsetY) }}%
                      </div>
                    </div>
                    
                    <p class="text-xs text-slate-600 dark:text-neutral-300">
                      JPG, PNG, GIF 형식의 이미지를 업로드하거나 이미지 URL을 입력하세요. (최대 5MB)
                    </p>
                  </div>
                </div>

                <div>
                  <label for="date" class="block text-sm font-medium text-slate-800 dark:text-neutral-200 mb-1">
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
                    <label for="time" class="block text-sm font-medium text-slate-800 dark:text-neutral-200 mb-1">
                      시작 시간 *
                    </label>
                    <CustomTimeSelect
                      v-model="form.time"
                      :required="true"
                    />
                  </div>

                  <div>
                    <label for="duration" class="block text-sm font-medium text-slate-800 dark:text-neutral-200">
                      모임 진행 시간 (시간) *
                    </label>
                    <CustomSelect
                      v-model="form.duration"
                      :options="durationOptions"
                      placeholder="진행 시간을 선택하세요"
                      :required="true"
                    />
                    <p class="mt-1 text-xs text-slate-600 dark:text-neutral-300">
                      모임이 진행될 시간을 입력하세요
                    </p>
                  </div>
                </div>

                <div>
                  <label for="location" class="block text-sm font-medium text-slate-800 dark:text-neutral-200">
                    장소 *
                  </label>
                  <input
                    id="location"
                    v-model="form.location"
                    type="text"
                    required
                    placeholder="예: 동탄 석우동 카페"
                    class="mt-1 block w-full px-3 py-3 border-slate-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-neutral-700 dark:border-neutral-600 dark:text-neutral-100 dark:placeholder-neutral-400 sm:text-base"
                  >
                </div>

                <div>
                  <label for="max_participants" class="block text-sm font-medium text-slate-800 dark:text-neutral-200">
                    최대 참여 인원 *
                  </label>
                  <input
                    id="max_participants"
                    v-model.number="form.max_participants"
                    type="number"
                    min="1"
                    max="100"
                    required
                    class="mt-1 block w-full px-3 py-3 border-gray-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-neutral-700 dark:border-neutral-600 dark:text-neutral-100 sm:text-base"
                  >
                  <p class="mt-2 text-sm text-slate-600 dark:text-neutral-300">
                    모임에 참여할 수 있는 최대 인원을 설정해주세요.
                  </p>
                </div>

                <div>
                  <label for="hashtags" class="block text-sm font-medium text-slate-800 dark:text-neutral-200">
                    해시태그
                  </label>
                  <input
                    id="hashtags"
                    v-model="form.hashtags"
                    type="text"
                    placeholder="예: #개발,#네트워킹,#스타트업 (쉼표로 구분)"
                    class="mt-1 block w-full px-3 py-3 border-slate-300 rounded-md shadow-sm focus:ring-slate-500 focus:border-slate-500 dark:bg-neutral-700 dark:border-neutral-600 dark:text-neutral-100 dark:placeholder-neutral-400 sm:text-base"
                  >
                  <p class="mt-2 text-sm text-slate-600 dark:text-neutral-300">
                    모임과 관련된 해시태그를 쉼표로 구분하여 입력하세요. # 기호는 자동으로 추가됩니다. 최대 5개까지 입력 가능합니다.
                  </p>
                </div>
              </div>

              <div v-if="error" class="rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 mb-6">
                <div class="flex">
                  <div class="flex-shrink-0">
                    <!-- Different icons based on error type -->
                    <svg
                      v-if="error.includes('네트워크') || error.includes('연결')"
                      class="h-5 w-5 text-red-500 dark:text-red-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <svg
                      v-else-if="error.includes('로그인') || error.includes('권한')"
                      class="h-5 w-5 text-red-500 dark:text-red-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M12 15v2m0 0v2m0-2h2m-2 0h-2M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                      />
                    </svg>
                    <svg
                      v-else-if="error.includes('이미지') || error.includes('파일')"
                      class="h-5 w-5 text-red-500 dark:text-red-400"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        stroke-linecap="round"
                        stroke-linejoin="round"
                        stroke-width="2"
                        d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                      />
                    </svg>
                    <svg
                      v-else
                      class="h-5 w-5 text-red-500 dark:text-red-400"
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path fill-rule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clip-rule="evenodd" />
                    </svg>
                  </div>
                  <div class="ml-3 flex-1">
                    <h3 class="text-sm font-semibold text-red-800 dark:text-red-200 mb-1">
                      오류 발생
                    </h3>
                    <p class="text-sm text-red-700 dark:text-red-300 leading-relaxed">
                      {{ error }}
                    </p>
                    <!-- Additional help text for common errors -->
                    <div class="mt-2 text-xs text-red-600 dark:text-red-400">
                      <p v-if="error.includes('500')">
                        💡 문제가 지속되면 브라우저를 새로고침하거나 관리자에게 문의해주세요.
                      </p>
                      <p v-else-if="error.includes('네트워크')">
                        💡 인터넷 연결을 확인하고 VPN을 사용 중이라면 끄고 다시 시도해보세요.
                      </p>
                      <p v-else-if="error.includes('로그인')">
                        💡 로그인 페이지로 자동 이동합니다...
                      </p>
                      <p v-else-if="error.includes('이미지')">
                        💡 다른 이미지 파일을 선택하거나 이미지 없이 모임을 생성해보세요.
                      </p>
                    </div>
                  </div>
                  <!-- Close button -->
                  <div class="ml-auto pl-3">
                    <button
                      class="inline-flex rounded-md bg-red-50 dark:bg-red-900/20 p-1.5 text-red-500 hover:bg-red-100 dark:hover:bg-red-800/30 focus:outline-none focus:ring-2 focus:ring-red-600 focus:ring-offset-2 focus:ring-offset-red-50"
                      @click="error = ''"
                    >
                      <span class="sr-only">닫기</span>
                      <svg class="h-3 w-3" fill="currentColor" viewBox="0 0 20 20">
                        <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </div>
              </div>

              <div class="flex justify-end space-x-3 pt-6 border-t border-slate-200 dark:border-neutral-600">
                <button
                  type="button"
                  class="bg-white dark:bg-neutral-700 border border-slate-300 dark:border-neutral-600 rounded-md shadow-sm py-2 px-4 text-sm font-medium text-slate-700 dark:text-neutral-300 hover:bg-slate-50 dark:hover:bg-neutral-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500"
                  @click="$router.go(-1)"
                >
                  취소
                </button>
                <button
                  type="submit"
                  :disabled="loading"
                  class="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-slate-600 dark:bg-neutral-800 hover:bg-slate-700 dark:hover:bg-neutral-900 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-slate-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg
                    v-if="loading"
                    class="animate-spin -ml-1 mr-3 h-5 w-5 text-white"
                    xmlns="http://www.w3.org/2000/svg"
                    fill="none"
                    viewBox="0 0 24 24"
                  >
                    <circle
                      class="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      stroke-width="4"
                    />
                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
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
import { ref, watch, computed, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'
import { toUTC, addDurationToLocal } from '@/utils/datetime'
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
    CustomSelect,
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
      hashtags: '',
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
      { value: 8, label: '8시간' },
    ])

    const imageInput = ref(null)
    const imagePreview = ref('')
    const imageContainer = ref(null)
    
    // Mouse drag state
    const isDragging = ref(false)
    const dragStart = ref({ x: 0, y: 0 })
    const imageOffsetX = ref(50) // Center position (50%)
    const imageOffsetY = ref(50) // Center position (50%)

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
      imageOffsetX.value = 50 // Reset to center
      imageOffsetY.value = 50 // Reset to center
      if (imageInput.value) {
        imageInput.value.value = ''
      }
    }

    // Reset image position to center
    const resetImagePosition = () => {
      imageOffsetX.value = 50
      imageOffsetY.value = 50
    }

    // Mouse drag handlers
    const startDrag = (event) => {
      event.preventDefault()
      if (!imageContainer.value) return
      
      isDragging.value = true
      const rect = imageContainer.value.getBoundingClientRect()
      dragStart.value = {
        x: event.clientX - rect.left,
        y: event.clientY - rect.top,
      }
      
      // Add global mouse event listeners
      document.addEventListener('mousemove', onDragGlobal)
      document.addEventListener('mouseup', endDragGlobal)
    }

    const onDrag = (event) => {
      if (!isDragging.value || !imageContainer.value) return
      event.preventDefault()
      updateImagePosition(event)
    }

    const onDragGlobal = (event) => {
      if (!isDragging.value) return
      event.preventDefault()
      updateImagePosition(event)
    }

    const updateImagePosition = (event) => {
      if (!imageContainer.value) return
      
      const rect = imageContainer.value.getBoundingClientRect()
      const x = event.clientX - rect.left
      const y = event.clientY - rect.top
      
      // Convert to percentage (0-100%)
      const percentX = Math.max(0, Math.min(100, (x / rect.width) * 100))
      const percentY = Math.max(0, Math.min(100, (y / rect.height) * 100))
      
      imageOffsetX.value = percentX
      imageOffsetY.value = percentY
    }

    const endDrag = () => {
      isDragging.value = false
      document.removeEventListener('mousemove', onDragGlobal)
      document.removeEventListener('mouseup', endDragGlobal)
    }

    const endDragGlobal = () => {
      endDrag()
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

        const dateTime = `${form.value.date}T${form.value.time}`

        // Convert to UTC for storage
        const dateTimeUTC = toUTC(dateTime)
        const endDateTimeUTC = addDurationToLocal(dateTime, form.value.duration, 'hour')
        
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
          date_time: dateTimeUTC,
          end_time: endDateTimeUTC,
          location: form.value.location,
          max_participants: form.value.max_participants,
          hashtags: processedHashtags,
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
            body: formData,
          })
        } else {
          response = await fetchWithCSRF('/api/meetups/', {
            method: 'POST',
            body: JSON.stringify(meetupData),
          })
        }

        console.log('Response status:', response.status)
        console.log('Response headers:', response.headers)

        if (response.ok) {
          router.push('/settings?message=모임이 성공적으로 생성되었습니다')
        } else {
          const responseText = await response.text()
          console.error('Error response:', response.status, responseText)
          
          // Handle different HTTP status codes with specific messages
          let errorMessage = '모임 생성에 실패했습니다'
          
          switch (response.status) {
          case 400:
            try {
              const data = JSON.parse(responseText)
              if (data.name) {
                errorMessage = `모임 이름 오류: ${Array.isArray(data.name) ? data.name.join(', ') : data.name}`
              } else if (data.max_participants) {
                errorMessage = `참가자 수 오류: ${Array.isArray(data.max_participants) ? data.max_participants.join(', ') : data.max_participants}`
              } else if (data.date_time) {
                errorMessage = `날짜/시간 오류: ${Array.isArray(data.date_time) ? data.date_time.join(', ') : data.date_time}`
              } else if (data.location) {
                errorMessage = `장소 오류: ${Array.isArray(data.location) ? data.location.join(', ') : data.location}`
              } else if (data.description) {
                errorMessage = `설명 오류: ${Array.isArray(data.description) ? data.description.join(', ') : data.description}`
              } else if (data.hashtags) {
                errorMessage = `해시태그 오류: ${Array.isArray(data.hashtags) ? data.hashtags.join(', ') : data.hashtags}`
              } else if (data.image) {
                errorMessage = `이미지 오류: ${Array.isArray(data.image) ? data.image.join(', ') : data.image}`
              } else {
                errorMessage = `입력 정보 오류: ${data.error || data.detail || '필수 정보를 확인해주세요'}`
              }
            } catch {
              errorMessage = '입력 정보에 오류가 있습니다. 모든 필드를 확인해주세요.'
            }
            break
              
          case 401:
            errorMessage = '로그인이 필요합니다. 다시 로그인해주세요.'
            // Auto redirect to login after 2 seconds
            setTimeout(() => {
              router.push('/login')
            }, 2000)
            break
              
          case 403:
            errorMessage = '모임 생성 권한이 없습니다. 관리자에게 문의하세요.'
            break
              
          case 413:
            errorMessage = '업로드한 이미지 파일이 너무 큽니다. 5MB 이하의 파일을 사용해주세요.'
            break
              
          case 415:
            errorMessage = '지원하지 않는 이미지 형식입니다. JPG, PNG, GIF 형식을 사용해주세요.'
            break
              
          case 422:
            try {
              const data = JSON.parse(responseText)
              errorMessage = `데이터 검증 오류: ${data.error || data.detail || '입력 데이터를 확인해주세요'}`
            } catch {
              errorMessage = '입력 데이터 형식이 올바르지 않습니다.'
            }
            break
              
          case 500:
            try {
              const data = JSON.parse(responseText)
              if (data.error && data.error.includes('CSRF')) {
                errorMessage = '보안 토큰이 만료되었습니다. 페이지를 새로고침해주세요.'
              } else if (data.error && data.error.includes('database')) {
                errorMessage = '데이터베이스 연결 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'
              } else if (data.error && data.error.includes('file')) {
                errorMessage = '파일 처리 중 오류가 발생했습니다. 다른 이미지를 시도해보세요.'
              } else {
                errorMessage = `서버 내부 오류: ${data.error || data.detail || '서버에서 처리 중 문제가 발생했습니다'}`
              }
            } catch {
              errorMessage = '서버에서 처리 중 오류가 발생했습니다. 관리자에게 문의하거나 잠시 후 다시 시도해주세요.'
            }
            break
              
          case 502:
          case 503:
          case 504:
            errorMessage = '서버가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.'
            break
              
          default:
            try {
              const data = JSON.parse(responseText)
              errorMessage = `오류 (${response.status}): ${data.error || data.detail || data.message || '알 수 없는 오류가 발생했습니다'}`
            } catch {
              errorMessage = `서버 오류 (${response.status}): ${responseText ? responseText.substring(0, 100) : '알 수 없는 오류가 발생했습니다'}`
            }
          }
          
          error.value = errorMessage
        }
      } catch (err) {
        console.error('Network error:', err)
        
        // Handle different network error types
        if (err.name === 'TypeError' && err.message.includes('fetch')) {
          error.value = '서버에 연결할 수 없습니다. 인터넷 연결을 확인하거나 잠시 후 다시 시도해주세요.'
        } else if (err.name === 'AbortError') {
          error.value = '요청이 취소되었습니다. 다시 시도해주세요.'
        } else if (err.message.includes('timeout')) {
          error.value = '요청 시간이 초과되었습니다. 네트워크 상태를 확인하고 다시 시도해주세요.'
        } else if (err.message.includes('NetworkError')) {
          error.value = '네트워크 오류가 발생했습니다. 인터넷 연결을 확인해주세요.'
        } else {
          error.value = `연결 오류: ${err.message || '서버와의 통신 중 오류가 발생했습니다. 다시 시도해주세요.'}`
        }
      } finally {
        loading.value = false
      }
    }

    const logout = async () => {
      await authStore.logout()
      router.push('/login')
    }

    // Cleanup event listeners on component unmount
    onUnmounted(() => {
      document.removeEventListener('mousemove', onDragGlobal)
      document.removeEventListener('mouseup', endDragGlobal)
    })

    return {
      authStore,
      form,
      loading,
      error,
      handleSubmit,
      logout,
      imageInput,
      imagePreview,
      imageContainer,
      isDragging,
      imageOffsetX,
      imageOffsetY,
      handleImageUpload,
      handleImageError,
      removeImage,
      resetImagePosition,
      startDrag,
      onDrag,
      endDrag,
      durationOptions,
    }
  },
}
</script>
