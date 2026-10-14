<template>
  <LiteTopbar
    title="이런 모임 열어주세요"
    back
  >
    <span />
  </LiteTopbar>
  <form
    class="l-body"
    @submit.prevent="submit"
  >
    <input
      v-model="title"
      class="l-big-input"
      maxlength="60"
      placeholder="어떤 모임?"
      aria-label="모임 주제"
    >
    <div
      class="l-seg"
      role="radiogroup"
      aria-label="원하는 시기"
    >
      <label
        v-for="(label, value) in PERIOD_LABEL"
        :key="value"
      >
        <input
          v-model="period"
          type="radio"
          name="period"
          :value="value"
        >
        <span>{{ label }}</span>
      </label>
    </div>
    <button
      class="l-btn p"
      type="submit"
      :disabled="busy"
    >
      올리기
    </button>
  </form>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { liteApi } from '../api'
import { PERIOD_LABEL } from '../format'
import { useLiteStore } from '../store'
import LiteTopbar from '../components/LiteTopbar.vue'

const router = useRouter()
const store = useLiteStore()
const title = ref('')
const period = ref('next_month')
const busy = ref(false)

const submit = async () => {
  const trimmed = title.value.trim()
  if (!trimmed) {
    store.notify('모임 주제를 입력해 주세요', 'error')
    return
  }
  busy.value = true
  const data = await store.act(() => liteApi.createRequest(trimmed, period.value), '올렸어요')
  busy.value = false
  if (data) router.push({ path: '/lite', query: { tab: 'requests' } })
}

onMounted(() => {
  if (!store.member) router.replace('/lite')
})
</script>
