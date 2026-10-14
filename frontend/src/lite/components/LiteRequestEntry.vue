<template>
  <div class="l-card link pinned">
    <button
      type="button"
      class="l-cardbtn l-row center"
      @click="router.push('/lite/requests')"
    >
      <div class="l-date always">
        <Hand :size="24" />
      </div>
      <div class="l-grow">
        <div class="l-title">
          이런 모임 열어주세요
        </div>
        <div
          v-if="readyCount"
          class="l-sub"
        >
          <span class="l-chip maybe">개설 가능 {{ readyCount }}</span>
        </div>
      </div>
      <ChevronRight :size="18" />
    </button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'
import { ChevronRight, Hand } from 'lucide-vue-next'

defineProps({ readyCount: { type: Number, default: 0 } })

const router = useRouter()
</script>
