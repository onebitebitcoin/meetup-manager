<template>
  <div class="l-onb">
    <span class="l-logo shadow-sticker">
      <LiteCookie filled />
    </span>
    <h2>이름만 알려주세요</h2>
    <form
      style="display: flex; flex-direction: column; gap: 14px"
      @submit.prevent="submit"
    >
      <input
        v-model="name"
        class="l-big-input"
        maxlength="20"
        placeholder="이름"
        autocomplete="nickname"
        aria-label="이름"
      >
      <button
        class="l-btn p"
        type="submit"
        :disabled="busy"
      >
        시작
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useLiteStore } from '../store'
import LiteCookie from './LiteCookie.vue'

const store = useLiteStore()
const name = ref('')
const busy = ref(false)

const submit = async () => {
  const trimmed = name.value.trim()
  if (!trimmed) {
    store.notify('이름을 입력해 주세요', 'error')
    return
  }
  busy.value = true
  await store.register(trimmed)
  busy.value = false
}
</script>
