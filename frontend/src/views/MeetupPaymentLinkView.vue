<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-900 py-8">
    <div class="max-w-lg mx-auto px-4">
      <!-- Header -->
      <div class="flex items-center mb-6">
        <button
          class="flex items-center text-neutral-600 hover:text-neutral-900 dark:text-neutral-400 dark:hover:text-neutral-100 transition-colors mr-4"
          @click="$router.back()"
        >
          <svg
            class="w-5 h-5 mr-1"
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
          뒤로
        </button>
        <h1 class="text-xl font-bold text-neutral-900 dark:text-neutral-100">
          결제 QR 링크
        </h1>
      </div>

      <!-- Error: no lightning address -->
      <div
        v-if="noLightningAddress"
        class="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 rounded-xl p-5 text-center"
      >
        <svg
          class="w-10 h-10 mx-auto mb-3 text-amber-500"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            stroke-linecap="round"
            stroke-linejoin="round"
            stroke-width="2"
            d="M13 10V3L4 14h7v7l9-11h-7z"
          />
        </svg>
        <p class="text-amber-800 dark:text-amber-200 font-medium mb-1">
          라이트닝 주소 미설정
        </p>
        <p class="text-sm text-amber-700 dark:text-amber-300 mb-4">
          결제 QR을 생성하려면 먼저 라이트닝 주소를 등록해야 합니다.
        </p>
        <button
          class="px-4 py-2 bg-amber-500 hover:bg-amber-600 text-white rounded-lg text-sm font-medium transition-colors"
          @click="$router.push('/settings')"
        >
          설정에서 등록하기
        </button>
      </div>

      <!-- Loading -->
      <div v-else-if="generating && !token" class="flex flex-col items-center py-16">
        <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mb-4" />
        <p class="text-neutral-500 dark:text-neutral-400 text-sm">
          인보이스 생성 중...
        </p>
      </div>

      <!-- Error -->
      <div
        v-else-if="error"
        class="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl p-5 text-center"
      >
        <p class="text-red-800 dark:text-red-200 text-sm mb-4">
          {{ error }}
        </p>
        <button
          class="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg text-sm font-medium transition-colors"
          @click="generate"
        >
          다시 시도
        </button>
      </div>

      <!-- Generated -->
      <div v-else-if="token" class="space-y-4">
        <!-- QR Code -->
        <div class="bg-white dark:bg-neutral-800 rounded-xl p-6 flex flex-col items-center">
          <canvas ref="qrCanvas" class="rounded-lg" />
          <p class="text-xs text-neutral-500 dark:text-neutral-400 mt-3">
            1 sats 인보이스 QR
          </p>
        </div>

        <!-- Expiry info -->
        <div class="flex items-center justify-center gap-2 text-sm text-neutral-500 dark:text-neutral-400">
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
              d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
            />
          </svg>
          <span>{{ expiryText }}</span>
        </div>

        <!-- Shareable link -->
        <div class="bg-beige-50 dark:bg-neutral-800 rounded-xl p-4">
          <p class="text-xs font-medium text-neutral-500 dark:text-neutral-400 mb-2">
            공유 링크
          </p>
          <div class="flex items-center gap-2">
            <input
              :value="shareUrl"
              readonly
              class="flex-1 bg-white dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg px-3 py-2 text-sm text-neutral-800 dark:text-neutral-200 focus:outline-none cursor-text select-all"
              @click="$event.target.select()"
            >
            <button
              class="flex-shrink-0 p-2 rounded-lg bg-primary-100 hover:bg-primary-200 dark:bg-primary-900 dark:hover:bg-primary-800 text-primary-700 dark:text-primary-300 transition-colors"
              :title="copied ? '복사됨!' : '링크 복사'"
              @click="copyLink"
            >
              <svg
                v-if="!copied"
                class="w-5 h-5"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"
                />
              </svg>
              <svg
                v-else
                class="w-5 h-5 text-green-600 dark:text-green-400"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  stroke-linecap="round"
                  stroke-linejoin="round"
                  stroke-width="2"
                  d="M5 13l4 4L19 7"
                />
              </svg>
            </button>
          </div>
        </div>

        <!-- Regenerate button -->
        <button
          :disabled="generating"
          class="w-full py-3 px-6 rounded-lg text-sm font-semibold border border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 disabled:opacity-50 transition-colors flex items-center justify-center gap-2"
          @click="generate"
        >
          <svg
            :class="['w-4 h-4', generating ? 'animate-spin' : '']"
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
          {{ generating ? '생성 중...' : '새 링크 생성' }}
        </button>

        <p class="text-center text-xs text-neutral-400 dark:text-neutral-500">
          링크는 1시간 후 만료됩니다. 만료 후에는 새 링크를 생성하세요.
        </p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { fetchWithCSRF } from '@/utils/csrf'
import QRCode from 'qrcode'

export default {
  name: 'MeetupPaymentLinkView',
  setup() {
    const route = useRoute()
    const authStore = useAuthStore()

    const meetupId = computed(() => parseInt(route.params.id))
    const token = ref('')
    const bolt11 = ref('')
    const expiresAt = ref(null)
    const generating = ref(false)
    const error = ref('')
    const noLightningAddress = ref(false)
    const copied = ref(false)
    const qrCanvas = ref(null)

    const shareUrl = computed(() => {
      if (!token.value) return ''
      return `${window.location.origin}/pay/${token.value}`
    })

    const expiryText = computed(() => {
      if (!expiresAt.value) return ''
      const now = new Date()
      const exp = new Date(expiresAt.value)
      const diffMs = exp - now
      if (diffMs <= 0) return '만료됨'
      const diffMin = Math.floor(diffMs / 60000)
      if (diffMin >= 60) return `${Math.floor(diffMin / 60)}시간 후 만료`
      return `${diffMin}분 후 만료`
    })

    const renderQR = async () => {
      if (!bolt11.value || !qrCanvas.value) return
      await nextTick()
      try {
        await QRCode.toCanvas(qrCanvas.value, bolt11.value.toUpperCase(), {
          width: 260,
          margin: 2,
          color: {
            dark: '#000000',
            light: '#ffffff',
          },
        })
      } catch (err) {
        console.error('QR render error:', err)
      }
    }

    const generate = async () => {
      if (generating.value) return
      generating.value = true
      error.value = ''
      noLightningAddress.value = false

      try {
        const res = await fetchWithCSRF(`/api/meetups/${meetupId.value}/payment-link/`, {
          method: 'POST',
        })
        const data = await res.json()

        if (res.ok) {
          token.value = data.token
          bolt11.value = data.bolt11
          expiresAt.value = data.expires_at
          await nextTick()
          await renderQR()
        } else {
          const msg = data.error || '링크 생성에 실패했습니다.'
          if (msg.includes('라이트닝 주소')) {
            noLightningAddress.value = true
          } else {
            error.value = msg
          }
        }
      } catch (err) {
        error.value = '네트워크 오류가 발생했습니다.'
      } finally {
        generating.value = false
      }
    }

    const copyLink = async () => {
      if (!shareUrl.value) return
      try {
        await navigator.clipboard.writeText(shareUrl.value)
        copied.value = true
        setTimeout(() => { copied.value = false }, 2000)
      } catch {
        // fallback
        const el = document.createElement('input')
        el.value = shareUrl.value
        document.body.appendChild(el)
        el.select()
        document.execCommand('copy')
        document.body.removeChild(el)
        copied.value = true
        setTimeout(() => { copied.value = false }, 2000)
      }
    }

    onMounted(() => {
      generate()
    })

    return {
      token,
      generating,
      error,
      noLightningAddress,
      shareUrl,
      expiryText,
      copied,
      qrCanvas,
      generate,
      copyLink,
      authStore,
    }
  },
}
</script>
