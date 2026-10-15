<template>
  <div
    ref="bar"
    class="l-top"
  >
    <button
      v-if="back"
      class="l-icon-btn"
      aria-label="뒤로"
      @click="router.push(backTo)"
    >
      <ChevronLeft :size="22" />
    </button>
    <h2>{{ title }}</h2>
    <slot>
      <span
        v-if="!back && store.member"
        class="l-me"
      >
        <span class="l-av">{{ store.member.name.slice(0, 1) }}</span>
        {{ store.member.name }}
      </span>
    </slot>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronLeft } from 'lucide-vue-next'
import { useLiteStore } from '../store'

defineProps({
  title: { type: String, required: true },
  back: { type: Boolean, default: false },
  backTo: { type: String, default: '/lite' },
})

const router = useRouter()
const store = useLiteStore()
const bar = ref(null)
let observer = null

// 고정 공지 바가 상단 바 바로 아래 붙도록 실제 높이를 부모(.lite-shell)에 CSS 변수로 알린다
const publishHeight = () => bar.value?.parentElement?.style.setProperty('--l-top-h', `${bar.value.offsetHeight}px`)

onMounted(() => {
  publishHeight()
  if (typeof ResizeObserver === 'undefined') return
  observer = new ResizeObserver(publishHeight)
  observer.observe(bar.value)
})
onBeforeUnmount(() => observer?.disconnect())
</script>
