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
      :aria-expanded="confirming"
      :disabled="busy"
      @click="confirming = !confirming"
    >
      <RefreshCw :size="16" />
    </button>
    <div
      v-if="confirming"
      class="l-me-confirm"
      role="dialog"
      aria-label="새 이름 확인"
    >
      <span>새 이름으로 바꿀까요?</span>
      <div class="l-btn-row">
        <button
          type="button"
          class="l-btn s"
          @click="confirming = false"
        >
          그만두기
        </button>
        <button
          type="button"
          class="l-btn p"
          :disabled="busy"
          @click="refresh"
        >
          바꾸기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { RefreshCw } from 'lucide-vue-next'
import { useLiteStore } from '../store'

const store = useLiteStore()
const busy = ref(false)
const confirming = ref(false)

const refresh = async () => {
  busy.value = true
  await store.renameRandom()
  busy.value = false
  confirming.value = false
}
</script>
