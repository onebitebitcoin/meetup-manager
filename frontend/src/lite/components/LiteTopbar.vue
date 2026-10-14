<template>
  <div class="l-top">
    <button
      v-if="back"
      class="l-icon-btn"
      aria-label="뒤로"
      @click="router.push('/lite')"
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
import { useRouter } from 'vue-router'
import { ChevronLeft } from 'lucide-vue-next'
import { useLiteStore } from '../store'

defineProps({
  title: { type: String, required: true },
  back: { type: Boolean, default: false },
})

const router = useRouter()
const store = useLiteStore()
</script>
