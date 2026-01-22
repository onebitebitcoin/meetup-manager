<template>
  <div class="relative">
    <!-- Modern Simple Banner Container -->
    <div 
      class="relative bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 rounded-lg sm:rounded-xl p-3 sm:p-4 cursor-pointer group"
      @click="handleBannerClick"
    >
      <!-- Banner Content -->
      <div v-if="currentAd" class="flex items-center justify-between">
        <!-- Left Content -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center space-x-2 sm:space-x-3">
            <!-- Icon/Badge -->
            <div class="flex-shrink-0">
              <div class="w-7 h-7 sm:w-8 sm:h-8 bg-primary-100 dark:bg-primary-900 rounded-lg flex items-center justify-center">
                <svg
                  class="w-3.5 h-3.5 sm:w-4 sm:h-4 text-primary-600 dark:text-primary-400"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"
                  />
                </svg>
              </div>
            </div>
            
            <!-- Content -->
            <div class="min-w-0 flex-1">
              <h3 class="text-sm sm:text-base font-medium text-neutral-900 dark:text-neutral-100 truncate mb-0.5">
                {{ currentAd.title }}
              </h3>
              <!-- Mobile-only one-line description -->
              <p v-if="currentAd.description" class="sm:hidden text-[11px] text-neutral-500 dark:text-neutral-400 truncate mb-0.5">
                {{ currentAd.description }}
              </p>
              <div class="flex items-center space-x-3 sm:space-x-4 text-[11px] sm:text-xs text-neutral-500 dark:text-neutral-400">
                <!-- Show only date on mobile -->
                <span class="flex items-center">
                  <svg
                    class="w-3 h-3 mr-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"
                    />
                  </svg>
                  {{ formatDate(currentAd.dateTime) }}
                </span>
                <span class="hidden sm:inline-flex items-center">
                  <svg
                    class="w-3 h-3 mr-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"
                    />
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"
                    />
                  </svg>
                  {{ currentAd.location }}
                </span>
                <span class="hidden sm:inline-flex items-center">
                  <svg
                    class="w-3 h-3 mr-1"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z"
                    />
                  </svg>
                  {{ currentAd.currentParticipants }}/{{ currentAd.maxParticipants }}
                </span>
              </div>
            </div>
          </div>
        </div>

        <!-- Right Side: Swipe Navigation Arrows -->
        <div v-if="adBanners.length" class="hidden sm:flex items-center space-x-1 flex-shrink-0 ml-4">
          <!-- Previous Arrow -->
          <button
            class="p-1.5 text-neutral-400 rounded-lg"
            :disabled="currentAdIndex === 0"
            :class="{ 'opacity-50 cursor-not-allowed': currentAdIndex === 0 }"
            @click.stop="previousSlide"
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
                d="M15 19l-7-7 7-7"
              />
            </svg>
          </button>
          
          <!-- Slide Indicator -->
          <div class="px-2 py-1 text-xs text-neutral-500 dark:text-neutral-400 font-medium">
            {{ currentAdIndex + 1 }}/{{ adBanners.length }}
          </div>
          
          <!-- Next Arrow -->
          <button
            class="p-1.5 text-neutral-400 rounded-lg"
            :disabled="currentAdIndex === adBanners.length - 1"
            :class="{ 'opacity-50 cursor-not-allowed': currentAdIndex === adBanners.length - 1 }"
            @click.stop="nextSlide"
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
                d="M9 5l7 7-7 7"
              />
            </svg>
          </button>
        </div>
      </div>
      <!-- Placeholder when no meetups available -->
      <div v-else class="text-sm text-neutral-500 dark:text-neutral-400">
        현재 표시할 모임이 없습니다.
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'

export default {
  name: 'AdsBanner',
  props: {
    // Meetups to display in the banner (already filtered by parent)
    meetups: {
      type: Array,
      default: () => [],
    },
  },
  emits: ['banner-click'],
  setup(props, { emit }) {
    const currentAdIndex = ref(0)
    const autoRotateInterval = ref(null)

    // Adapt meetups into banner items
    const adBanners = computed(() => {
      return (props.meetups || []).map(m => ({
        id: m.id,
        title: m.name,
        description: m.description,
        dateTime: m.date_time,
        location: m.location,
        currentParticipants: m.current_participants,
        maxParticipants: m.max_participants,
        hashtags: m.hashtags_list || [],
        image_display_url: m.image_display_url || null,
      }))
    })

    const currentAd = computed(() => adBanners.value[currentAdIndex.value] || null)

    // 날짜 포맷팅
    const formatDate = (dateString) => {
      if (!dateString) return ''
      const date = new Date(dateString)
      const month = date.getMonth() + 1
      const day = date.getDate()
      const hours = date.getHours()
      const minutes = date.getMinutes()
      return `${month}/${day} ${hours}:${minutes.toString().padStart(2, '0')}`
    }

    // 배너 클릭 핸들러
    const handleBannerClick = () => {
      if (currentAd.value) emit('banner-click', currentAd.value)
    }

    // 슬라이드 네비게이션 함수
    const previousSlide = () => {
      if (currentAdIndex.value > 0) {
        currentAdIndex.value--
      }
    }

    const nextSlide = () => {
      if (currentAdIndex.value < adBanners.value.length - 1) {
        currentAdIndex.value++
      }
    }

    // 자동 회전 시작
    const startAutoRotate = () => {
      stopAutoRotate()
      if (!adBanners.value.length) return
      autoRotateInterval.value = setInterval(() => {
        if (!adBanners.value.length) return
        if (currentAdIndex.value < adBanners.value.length - 1) {
          currentAdIndex.value++
        } else {
          currentAdIndex.value = 0 // 마지막에서 처음으로 돌아가기
        }
      }, 5000)
    }

    // 자동 회전 중지
    const stopAutoRotate = () => {
      if (autoRotateInterval.value) {
        clearInterval(autoRotateInterval.value)
        autoRotateInterval.value = null
      }
    }

    onMounted(() => {
      startAutoRotate()
    })

    onUnmounted(() => {
      stopAutoRotate()
    })

    // Start or stop auto-rotate when data availability changes
    watch(adBanners, (list) => {
      if (!list || list.length <= 1) {
        stopAutoRotate()
        currentAdIndex.value = 0
        return
      }
      if (currentAdIndex.value > list.length - 1) currentAdIndex.value = 0
      startAutoRotate()
    }, { immediate: true })

    return {
      currentAdIndex,
      adBanners,
      currentAd,
      formatDate,
      handleBannerClick,
      previousSlide,
      nextSlide,
    }
  },
}
</script>
