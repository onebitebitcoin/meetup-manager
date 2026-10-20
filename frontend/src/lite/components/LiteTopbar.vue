<template>
  <div
    class="l-top"
    :class="{ scrolled }"
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
      <LiteMeMenu v-if="!back && store.member" />
    </slot>
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronLeft } from 'lucide-vue-next'
import { useLiteStore } from '../store'
import LiteMeMenu from './LiteMeMenu.vue'

defineProps({
  title: { type: String, required: true },
  back: { type: Boolean, default: false },
  backTo: { type: String, default: '/lite' },
})

const router = useRouter()
const store = useLiteStore()
const scrolled = ref(false)

// 배경과 같은 색인 상단 바는 내용이 아래로 지나갈 때만 구분선을 보인다
const updateScrolled = () => { scrolled.value = window.scrollY > 0 }

onMounted(() => {
  updateScrolled()
  window.addEventListener('scroll', updateScrolled, { passive: true })
})
onBeforeUnmount(() => {
  window.removeEventListener('scroll', updateScrolled)
})
</script>
