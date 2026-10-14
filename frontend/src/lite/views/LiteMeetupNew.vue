<template>
  <LiteTopbar
    :title="fromRequest ? `${fromRequest.vote_count}명이 원해요` : '모임 만들기'"
    back
  >
    <span />
  </LiteTopbar>
  <form
    class="l-body"
    @submit.prevent="submit"
  >
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
    <button
      class="l-btn p"
      type="submit"
      :disabled="busy"
    >
      열기
    </button>
  </form>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Users } from 'lucide-vue-next'
import { liteApi } from '../api'
import { toSeoulIso } from '../format'
import { useLiteStore } from '../store'
import LiteTopbar from '../components/LiteTopbar.vue'

const route = useRoute()
const router = useRouter()
const store = useLiteStore()
const busy = ref(false)
const fromRequest = ref(null)
const form = reactive({ title: '', date: '', time: '', location: '', capacity: 15 })

const submit = async () => {
  const missing = !form.title.trim() || !form.date || !form.time || !form.location.trim() || !form.capacity
  if (missing) {
    store.notify('모든 항목을 입력해 주세요', 'error')
    return
  }
  const payload = {
    title: form.title.trim(),
    starts_at: toSeoulIso(form.date, form.time),
    location: form.location.trim(),
    capacity: form.capacity,
  }
  if (fromRequest.value) payload.request_id = fromRequest.value.id
  busy.value = true
  const data = await store.act(() => liteApi.createMeetup(payload), '열었어요')
  busy.value = false
  if (data) router.push(`/lite/m/${data.meetup.id}`)
}

const loadRequest = async (id) => {
  const found = (await liteApi.requests()).requests.find((r) => String(r.id) === String(id))
  if (!found) throw new Error('요청을 찾을 수 없어요')
  fromRequest.value = found
  form.title = found.title
}

onMounted(async () => {
  if (!store.member) {
    router.replace('/lite')
    return
  }
  if (!store.isHost) {
    store.notify('운영자만 할 수 있어요', 'error')
    router.replace('/lite')
    return
  }
  if (route.query.request) await store.act(() => loadRequest(route.query.request))
})
</script>
