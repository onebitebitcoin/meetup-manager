<template>
  <div
    v-if="store.member"
    class="l-me"
  >
    <span class="l-av">{{ store.member.name.slice(0, 1) }}</span>
    {{ store.member.name }}
    <!-- 이름이 마음에 안 들면 새로고침으로 자동 닉네임을 새로 받는다(참석·대화 기록은 그대로) -->
    <button
      type="button"
      class="l-me-refresh"
      aria-label="새 이름 받기"
      :disabled="busy"
      @click="refresh"
    >
      <RefreshCw :size="16" />
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import { useLiteStore } from '../store'

const store = useLiteStore()
const busy = ref(false)

const refresh = async () => {
  busy.value = true
  await store.renameRandom()
  busy.value = false
}
</script>
