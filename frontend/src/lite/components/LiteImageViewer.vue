<template>
  <div
    class="l-viewer"
    role="dialog"
    aria-label="이미지 보기"
    @click.self="emit('close')"
  >
    <div class="l-viewer-bar">
      <a
        class="l-icon-btn"
        :href="attachment.url"
        :download="attachment.name"
        aria-label="다운로드"
      ><Download :size="22" /></a>
      <button
        type="button"
        class="l-icon-btn"
        aria-label="닫기"
        @click="emit('close')"
      >
        <X :size="22" />
      </button>
    </div>
    <img
      :src="attachment.url"
      :alt="attachment.name"
      @click.self="emit('close')"
    >
  </div>
</template>

<script setup>
import { onBeforeUnmount, onMounted } from 'vue'
import { Download, X } from 'lucide-vue-next'

defineProps({ attachment: { type: Object, required: true } })
const emit = defineEmits(['close'])

const onKey = (e) => { if (e.key === 'Escape') emit('close') }
onMounted(() => document.addEventListener('keydown', onKey))
onBeforeUnmount(() => document.removeEventListener('keydown', onKey))
</script>
