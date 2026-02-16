<template>
  <div id="app" class="min-h-screen bg-neutral-50 dark:bg-neutral-950 transition-colors duration-300 safe-area-top">
    <router-view />
    
    <!-- PWA Update Available Notification with enhanced design -->
    <Transition
      enter-active-class="transform transition duration-300 ease-out"
      enter-from-class="translate-y-full opacity-0"
      enter-to-class="translate-y-0 opacity-100"
      leave-active-class="transform transition duration-200 ease-in"
      leave-from-class="translate-y-0 opacity-100"
      leave-to-class="translate-y-full opacity-0"
    >
      <div 
        v-if="showUpdateNotification" 
        class="fixed bottom-4 left-4 right-4 z-50 animate-slide-up"
      >
        <div class="card card-elevated p-4 border border-primary-200 dark:border-primary-800">
          <div class="flex items-start justify-between">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-primary-100 dark:bg-primary-900/20 rounded-lg flex items-center justify-center">
                  <svg
                    class="w-5 h-5 text-primary-600 dark:text-primary-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
                    />
                  </svg>
                </div>
              </div>
              <div>
                <p class="font-semibold text-neutral-900 dark:text-neutral-100">
                  앱 업데이트가 있습니다!
                </p>
                <p class="text-sm text-neutral-600 dark:text-neutral-400">
                  새 버전을 설치하시겠습니까?
                </p>
              </div>
            </div>
            <div class="flex space-x-2 ml-4">
              <button class="btn-primary" @click="updateApp">
                업데이트
              </button>
              <button class="btn-ghost p-2" @click="dismissUpdate">
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
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'

export default {
  name: 'App',
  setup() {
    const authStore = useAuthStore()
    const showUpdateNotification = ref(false)
    let refreshSW = null

    onMounted(() => {
      authStore.checkAuth()
      
      // PWA service worker registration check
      if ('serviceWorker' in navigator) {
        // Listen for service worker updates
        navigator.serviceWorker.addEventListener('controllerchange', () => {
          window.location.reload()
        })
      }
      
      // Check for PWA update
      if (window.__SW_UPDATE_AVAILABLE__) {
        showUpdateNotification.value = true
        refreshSW = window.__SW_UPDATE_AVAILABLE__
      }
    })

    const updateApp = () => {
      if (refreshSW) {
        refreshSW(true)
      } else {
        window.location.reload()
      }
    }

    const dismissUpdate = () => {
      showUpdateNotification.value = false
    }

    return {
      showUpdateNotification,
      updateApp,
      dismissUpdate,
    }
  },
}
</script>
