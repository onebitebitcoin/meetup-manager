<template>
  <div class="l-section">
    <input
      v-model="form.title"
      class="l-big-input"
      maxlength="80"
      placeholder="모임 이름"
      aria-label="모임 이름"
    >
    <div class="l-grid2">
      <input
        v-model="form.date"
        class="l-field"
        type="date"
        aria-label="날짜"
      >
      <input
        v-model="form.time"
        class="l-field"
        type="time"
        aria-label="시간"
      >
    </div>
    <input
      v-model="form.location"
      class="l-field"
      maxlength="100"
      placeholder="장소"
      aria-label="장소"
    >
    <label class="l-num">
      <Users :size="18" />
      <input
        v-model.number="form.capacity"
        class="l-field"
        type="number"
        min="2"
        max="200"
        aria-label="정원"
      >명
    </label>
    <textarea
      v-model="form.description"
      class="l-field"
      maxlength="2000"
      placeholder="설명"
      aria-label="설명"
    />
    <input
      v-if="showImage"
      v-model="form.image_url"
      class="l-field"
      maxlength="500"
      placeholder="썸네일 이미지 주소 (URL)"
      aria-label="썸네일 이미지 주소"
    >
  </div>
</template>

<script setup>
import { reactive, watch } from 'vue'
import { Users } from 'lucide-vue-next'

const props = defineProps({
  initial: { type: Object, default: () => ({}) },
  showImage: { type: Boolean, default: false },
})
const emit = defineEmits(['change'])

const blank = { title: '', date: '', time: '', location: '', capacity: 15, description: '', image_url: '' }
const form = reactive({ ...blank, ...props.initial })

watch(() => props.initial, (value) => Object.assign(form, value), { deep: true })
watch(form, () => emit('change', { ...form }), { deep: true, immediate: true })
</script>
