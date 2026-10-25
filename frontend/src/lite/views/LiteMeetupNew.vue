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
    <LiteMeetupForm
      :initial="initial"
      @change="form = $event"
    />
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
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { liteApi } from '../api'
import { toSeoulIso } from '../format'
import { useLiteStore } from '../store'
import LiteMeetupForm from '../components/LiteMeetupForm.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

const route = useRoute()
const router = useRouter()
const store = useLiteStore()
const busy = ref(false)
const fromRequest = ref(null)
const initial = ref({})
const form = ref({ title: '', date: '', time: '', location: '', capacity: 15, audience: '', description: '' })

const submit = async () => {
  const f = form.value
  const missing = !f.title.trim() || !f.date || !f.time || !f.location.trim() || !f.capacity
  if (missing) {
    store.notify('모든 항목을 입력해 주세요', 'error')
    return
  }
  const payload = {
    title: f.title.trim(),
    starts_at: toSeoulIso(f.date, f.time),
    location: f.location.trim(),
    capacity: f.capacity,
  }
  if (f.audience.trim()) payload.audience = f.audience.trim()
  if (f.description.trim()) payload.description = f.description.trim()
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
  initial.value = { title: found.title }
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
