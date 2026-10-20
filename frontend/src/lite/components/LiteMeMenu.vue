<template>
  <div
    v-if="store.member"
    class="l-me-wrap"
  >
    <button
      type="button"
      class="l-me"
      :aria-expanded="open"
      aria-label="내 이름 메뉴"
      @click="open = !open"
    >
      <span class="l-av">{{ store.member.name.slice(0, 1) }}</span>
      {{ store.member.name }}
    </button>
    <div
      v-if="open"
      class="l-me-menu"
    >
      <span>이 기기에서 이름을 지울까요?</span>
      <div class="l-btn-row">
        <button
          type="button"
          class="l-btn s"
          @click="open = false"
        >
          그만두기
        </button>
        <button
          type="button"
          class="l-btn p"
          @click="forget"
        >
          <Trash2 :size="16" />지우기
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { Trash2 } from 'lucide-vue-next'
import { useLiteStore } from '../store'

// 이 브라우저에 저장된 토큰만 지운다. 서버의 회원·참석 기록은 그대로 남는다.
const store = useLiteStore()
const open = ref(false)

const forget = () => {
  open.value = false
  store.logout()
  store.notify('이 기기에서 이름을 지웠어요')
}
</script>
