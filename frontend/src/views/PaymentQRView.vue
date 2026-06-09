<template>
  <div class="min-h-screen bg-beige-100 dark:bg-neutral-900 flex flex-col items-center justify-center py-8 px-4">
    <!-- Loading -->
    <div v-if="loading" class="flex flex-col items-center">
      <div class="animate-spin rounded-full h-10 w-10 border-b-2 border-primary-600 mb-4" />
      <p class="text-neutral-500 dark:text-neutral-400 text-sm">
        불러오는 중...
      </p>
    </div>

    <!-- Not found -->
    <div v-else-if="notFound" class="text-center max-w-sm">
      <svg
        class="w-14 h-14 mx-auto mb-4 text-neutral-300 dark:text-neutral-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p class="text-neutral-600 dark:text-neutral-400 font-medium">
        링크를 찾을 수 없습니다
      </p>
      <p class="text-sm text-neutral-400 dark:text-neutral-500 mt-1">
        만료되었거나 잘못된 링크입니다.
      </p>
    </div>

    <!-- Expired -->
    <div v-else-if="isExpired" class="text-center max-w-sm">
      <svg
        class="w-14 h-14 mx-auto mb-4 text-neutral-300 dark:text-neutral-600"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="1.5"
          d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"
        />
      </svg>
      <p class="text-neutral-600 dark:text-neutral-400 font-medium">
        링크가 만료되었습니다
      </p>
      <p class="text-sm text-neutral-400 dark:text-neutral-500 mt-1">
        모임 주최자에게 새 링크를 요청하세요.
      </p>
    </div>

    <!-- QR Page -->
    <div v-else-if="bolt11" class="w-full max-w-sm">
      <!-- Meetup info -->
      <div class="text-center mb-6">
        <div class="inline-flex items-center gap-2 px-3 py-1 bg-primary-100 dark:bg-primary-900 rounded-full mb-3">
          <svg
            class="w-4 h-4 text-primary-600 dark:text-primary-400"
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
          <span class="text-xs font-medium text-primary-700 dark:text-primary-300">{{ amountSats.toLocaleString() }} sats 결제</span>
        </div>
        <h1 class="text-lg font-bold text-neutral-900 dark:text-neutral-100">
          {{ meetupName }}
        </h1>
        <p class="text-sm text-neutral-500 dark:text-neutral-400 mt-1">
          아래 QR 코드를 스캔해 {{ amountSats.toLocaleString() }} sats를 보내주세요
        </p>
      </div>

      <!-- QR Code -->
      <div class="bg-white dark:bg-neutral-800 rounded-2xl p-6 flex justify-center shadow-sm mb-4">
        <canvas ref="qrCanvas" class="rounded-lg" />
      </div>

      <!-- Expiry -->
      <div class="flex items-center justify-center gap-1.5 text-sm text-neutral-500 dark:text-neutral-400 mb-6">
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

      <!-- BOLT11 text (for manual copy) -->
      <div class="bg-beige-50 dark:bg-neutral-800 rounded-xl p-4">
        <p class="text-xs font-medium text-neutral-500 dark:text-neutral-400 mb-2">
          인보이스 (직접 입력)
        </p>
        <div class="flex items-center gap-2">
          <input
            :value="bolt11"
            readonly
            class="flex-1 bg-white dark:bg-neutral-700 border border-neutral-200 dark:border-neutral-600 rounded-lg px-3 py-2 text-xs text-neutral-600 dark:text-neutral-300 focus:outline-none font-mono truncate cursor-text"
            @click="$event.target.select()"
          >
          <button
            class="flex-shrink-0 p-2 rounded-lg bg-neutral-100 hover:bg-neutral-200 dark:bg-neutral-700 dark:hover:bg-neutral-600 text-neutral-600 dark:text-neutral-300 transition-colors"
            :title="copied ? '복사됨!' : '복사'"
            @click="copyBolt11"
          >
            <svg
              v-if="!copied"
              class="w-4 h-4"
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
              class="w-4 h-4 text-green-600 dark:text-green-400"
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
    </div>
  </div>
</template>

<script>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import QRCode from 'qrcode'

export default {
  name: 'PaymentQRView',
  setup() {
    const route = useRoute()
    const token = computed(() => route.params.token)

    const loading = ref(true)
    const notFound = ref(false)
    const isExpired = ref(false)
    const bolt11 = ref('')
    const amountSats = ref(1)
    const meetupName = ref('')
    const expiresAt = ref(null)
    const copied = ref(false)
    const qrCanvas = ref(null)

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
          width: 280,
          margin: 2,
          color: { dark: '#000000', light: '#ffffff' },
        })
      } catch (err) {
        console.error('QR render error:', err)
      }
    }

    const fetchLink = async () => {
      loading.value = true
      try {
        const res = await fetch(`/api/payment-link/${token.value}/`, {
          credentials: 'include',
        })
        if (res.status === 404) {
          notFound.value = true
          return
        }
        const data = await res.json()
        if (data.is_expired) {
          isExpired.value = true
          return
        }
        bolt11.value = data.bolt11
        amountSats.value = data.amount_sats || 1
        meetupName.value = data.meetup_name
        expiresAt.value = data.expires_at
        loading.value = false
        await nextTick()
        await renderQR()
      } catch {
        notFound.value = true
        loading.value = false
      }
    }

    const copyBolt11 = async () => {
      if (!bolt11.value) return
      try {
        await navigator.clipboard.writeText(bolt11.value)
        copied.value = true
        setTimeout(() => { copied.value = false }, 2000)
      } catch {
        const el = document.createElement('input')
        el.value = bolt11.value
        document.body.appendChild(el)
        el.select()
        document.execCommand('copy')
        document.body.removeChild(el)
        copied.value = true
        setTimeout(() => { copied.value = false }, 2000)
      }
    }

    onMounted(() => {
      fetchLink()
    })

    return {
      loading,
      notFound,
      isExpired,
      bolt11,
      amountSats,
      meetupName,
      expiryText,
      copied,
      qrCanvas,
      copyBolt11,
    }
  },
}
</script>
