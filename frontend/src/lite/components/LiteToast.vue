<template>
  <div
    v-if="store.toast"
    class="l-toast"
    :class="{ error: store.toast.kind === 'error' }"
    role="status"
  >
    <AlertCircle
      v-if="store.toast.kind === 'error'"
      :size="18"
    />
    <CheckCircle2
      v-else
      :size="18"
    />
    <span>{{ store.toast.message }}</span>
  </div>
</template>

<script setup>
import { AlertCircle, CheckCircle2 } from 'lucide-vue-next'
import { useLiteStore } from '../store'

const store = useLiteStore()
</script>
