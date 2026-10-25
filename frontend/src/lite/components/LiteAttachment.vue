<template>
  <button
    v-if="attachment.kind === 'image'"
    type="button"
    class="l-att-open"
    :aria-label="`${attachment.name} 크게 보기`"
    @click="viewing = true"
  >
    <img
      class="l-att-img"
      :src="attachment.url"
      :alt="attachment.name"
      loading="lazy"
      @load="emit('loaded')"
    >
  </button>
  <a
    v-else
    class="l-att-file"
    :href="attachment.url"
    :download="attachment.name"
  >
    <FileText :size="20" />
    <span class="l-att-name">{{ attachment.name }}</span>
    <span class="l-att-size">{{ formatSize(attachment.size) }}</span>
  </a>
  <LiteImageViewer
    v-if="viewing"
    :attachment="attachment"
    @close="viewing = false"
  />
</template>

<script setup>
import { ref } from 'vue'
import { FileText } from 'lucide-vue-next'
import LiteImageViewer from './LiteImageViewer.vue'
import { formatSize } from '../attachment'

defineProps({ attachment: { type: Object, required: true } })
const emit = defineEmits(['loaded'])
const viewing = ref(false)
</script>
