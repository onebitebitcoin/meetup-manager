<template>
  <button
    v-if="open"
    type="button"
    class="l-fab-backdrop"
    aria-label="메뉴 닫기"
    @click="open = false"
  />
  <div class="l-fab">
    <div
      v-if="open"
      class="l-fab-menu"
    >
      <button
        type="button"
        @click="go('/lite/seminar')"
      >
        <GraduationCap :size="20" />
        <span class="l-grow">1:1 세미나</span>
        <span
          v-if="seminar && seminar.status !== 'guide'"
          class="l-chip"
          :class="STATUS_CLASS[seminar.status]"
        >{{ SEMINAR_STATUS_LABEL[seminar.status] }}</span>
      </button>
      <button
        type="button"
        @click="go('/lite/requests')"
      >
        <Hand :size="20" />
        <span class="l-grow">이런 모임 열어주세요</span>
      </button>
    </div>
    <button
      type="button"
      class="l-fab-btn"
      :aria-label="open ? '메뉴 닫기' : '문의'"
      :aria-expanded="open"
      @click="open = !open"
    >
      <X
        v-if="open"
        :size="24"
      />
      <b
        v-else
        class="l-fab-ask"
      >문의</b>
    </button>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { GraduationCap, Hand, X } from 'lucide-vue-next'
import { SEMINAR_STATUS_LABEL } from '../format'

// 운영자가 아닌 방문자 홈의 1:1 세미나·모임 요청 진입점. seminar가 없으면 아직 시작하지 않은 상태다.
defineProps({ seminar: { type: Object, default: null } })

const STATUS_CLASS = { guide: 'none', received: 'maybe', confirmed: 'going' }
const router = useRouter()
const open = ref(false)

const go = (path) => {
  open.value = false
  router.push(path)
}

const onKey = (e) => { if (e.key === 'Escape') open.value = false }
onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))
</script>
