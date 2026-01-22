<template>
  <div v-if="showInstallPrompt" class="fixed bottom-4 left-4 right-4 bg-indigo-600 text-white p-4 rounded-lg shadow-lg z-50 flex items-center justify-between safe-area-bottom">
    <div class="flex items-center space-x-3">
      <div class="bg-white p-2 rounded">
        <svg
          class="w-6 h-6 text-indigo-600"
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
      </div>
      <div>
        <p class="font-medium text-sm sm:text-base">
          한입 모임 설치
        </p>
        <p class="text-xs sm:text-sm opacity-90">
          홈 화면에서 바로 실행하세요!
        </p>
      </div>
    </div>
    <div class="flex space-x-2 ml-4">
      <button class="bg-white text-indigo-600 px-3 py-1 rounded text-sm font-medium" @click="installApp">
        설치
      </button>
      <button class="text-white opacity-75 hover:opacity-100" @click="dismissInstall">
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
</template>

<script>
import { ref, onMounted } from 'vue'

export default {
  name: 'PWAInstallPrompt',
  setup() {
    const showInstallPrompt = ref(false)
    let deferredPrompt = null

    onMounted(() => {
      // Check if already installed
      if (window.matchMedia('(display-mode: standalone)').matches) {
        return
      }

      // Listen for the beforeinstallprompt event
      window.addEventListener('beforeinstallprompt', (e) => {
        // Prevent Chrome 67 and earlier from automatically showing the prompt
        e.preventDefault()
        deferredPrompt = e
        showInstallPrompt.value = true
      })

      // Listen for the app being installed
      window.addEventListener('appinstalled', () => {
        showInstallPrompt.value = false
        deferredPrompt = null
      })

      // iOS Safari detection
      const isIOS = /iPad|iPhone|iPod/.test(navigator.userAgent) && !window.MSStream
      const isInStandaloneMode = ('standalone' in window.navigator) && (window.navigator.standalone)
      
      if (isIOS && !isInStandaloneMode) {
        // Show iOS install instructions after a delay
        setTimeout(() => {
          if (!localStorage.getItem('ios-install-dismissed')) {
            showInstallPrompt.value = true
          }
        }, 3000)
      }
    })

    const installApp = async () => {
      if (deferredPrompt) {
        deferredPrompt.prompt()
        const { outcome } = await deferredPrompt.userChoice
        if (outcome === 'accepted') {
          showInstallPrompt.value = false
        }
        deferredPrompt = null
      } else {
        // For iOS, show instructions
        alert('iOS에서 설치하려면:\n1. 공유 버튼(□↗)을 누르세요\n2. "홈 화면에 추가"를 선택하세요')
        localStorage.setItem('ios-install-dismissed', 'true')
        showInstallPrompt.value = false
      }
    }

    const dismissInstall = () => {
      showInstallPrompt.value = false
      localStorage.setItem('ios-install-dismissed', 'true')
      deferredPrompt = null
    }

    return {
      showInstallPrompt,
      installApp,
      dismissInstall,
    }
  },
}
</script>