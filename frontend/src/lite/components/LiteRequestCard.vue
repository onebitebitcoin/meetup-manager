<template>
  <div
    v-if="request.status === 'done'"
    class="l-card link done"
    role="button"
    tabindex="0"
    @click="openMeetup"
    @keydown.enter="openMeetup"
  >
    <div class="l-row center">
      <div class="l-grow l-title">
        {{ request.title }}
      </div>
      <span class="l-chip going">열렸어요</span>
      <ChevronRight :size="18" />
    </div>
  </div>
  <div
    v-else
    class="l-card"
  >
    <div class="l-title">
      {{ request.title }}
    </div>
    <div class="l-sub">
      <LiteProgress
        :count="request.vote_count"
        :total="request.threshold"
      />
      <span class="l-counts">{{ PERIOD_LABEL[request.preferred_period] }}</span>
    </div>
    <div class="l-rfoot">
      <button
        class="l-vote"
        :aria-pressed="request.voted"
        :disabled="busy"
        @click="vote"
      >
        <Hand :size="18" />나도 {{ request.vote_count }}
      </button>
      <button
        v-if="store.isHost"
        class="l-vote"
        :class="{ primary: ready }"
        style="margin-left: auto"
        @click="router.push({ path: '/new-meetup', query: { request: request.id } })"
      >
        <Plus :size="18" />열기
      </button>
      <span
        v-else-if="ready"
        class="l-chip maybe"
        style="margin-left: auto"
      >검토 중</span>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronRight, Hand, Plus } from 'lucide-vue-next'
import { liteApi } from '../api'
import { PERIOD_LABEL } from '../format'
import { useLiteStore } from '../store'
import LiteProgress from './LiteProgress.vue'

const props = defineProps({ request: { type: Object, required: true } })
const emit = defineEmits(['updated'])

const router = useRouter()
const store = useLiteStore()
const busy = ref(false)
const ready = computed(() => props.request.vote_count >= props.request.threshold)

const openMeetup = () => router.push(`/m/${props.request.meetup_id}`)

const vote = async () => {
  if (busy.value) return
  busy.value = true
  const data = await store.act(() => liteApi.vote(props.request.id))
  busy.value = false
  if (!data) return
  const next = data.request
  store.notify(!next.voted ? '취소했어요' : next.vote_count === next.threshold ? `${next.threshold}명 모였어요!` : '나도 원해요')
  emit('updated', next)
}
</script>
