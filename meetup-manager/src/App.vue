<template>
  <div id="app" class="min-h-screen safe-area-top">
    <router-view />
    <!-- PWA Update Available Notification -->
    <div v-if="showUpdateNotification" class="fixed bottom-4 left-4 right-4 bg-indigo-600 text-white p-4 rounded-lg shadow-lg z-50 flex items-center justify-between">
      <div>
        <p class="font-medium">앱 업데이트가 있습니다!</p>
        <p class="text-sm opacity-90">새 버전을 설치하시겠습니까?</p>
      </div>
      <div class="flex space-x-2 ml-4">
        <button @click="updateApp" class="bg-white text-indigo-600 px-3 py-1 rounded text-sm font-medium">
          업데이트
        </button>
        <button @click="dismissUpdate" class="text-white opacity-75 hover:opacity-100">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </button>
      </div>
    </div>
    
    <!-- PWA Install Prompt -->
    <PWAInstallPrompt />
  </div>
</template>

<script>
import { onMounted, ref } from 'vue'
import { useAuthStore } from '@/stores/auth'
import PWAInstallPrompt from '@/components/PWAInstallPrompt.vue'

export default {
  name: 'App',
  components: {
    PWAInstallPrompt
  },
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
      dismissUpdate
    }
  }
}
</script>