<template>
  <div class="lite-scroll">
    <div class="l-msgs">
      <LiteMessage
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :mine="message.kind === 'user' && message.member?.id === store.member?.id"
      />
      <slot name="after" />
      <div ref="bottom" />
    </div>
  </div>
  <form
    v-if="canSend"
    class="l-composer"
    @submit.prevent="send"
  >
    <input
      v-model="draft"
      :placeholder="placeholder"
      maxlength="1000"
      autocomplete="off"
      aria-label="메시지"
    >
    <button
      type="submit"
      aria-label="보내기"
      :disabled="sending"
    >
      <Send :size="18" />
    </button>
  </form>
</template>

<script setup>
import { nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { Send } from 'lucide-vue-next'
import { liteApi } from '../api'
import { useLiteStore } from '../store'
import LiteMessage from './LiteMessage.vue'

const props = defineProps({
  roomId: { type: Number, required: true },
  canSend: { type: Boolean, default: true },
  placeholder: { type: String, default: '메시지' },
})
const emit = defineEmits(['sent', 'received'])

const POLL_MS = 3000
const store = useLiteStore()
const messages = ref([])
const draft = ref('')
const sending = ref(false)
const bottom = ref(null)
let timer = null
let polling = false
let failing = false

const append = async (incoming) => {
  const known = new Set(messages.value.map((m) => m.id))
  const fresh = incoming.filter((m) => !known.has(m.id))
  if (!fresh.length) return false
  messages.value = [...messages.value, ...fresh]
  await nextTick()
  bottom.value?.scrollIntoView?.({ block: 'end' })
  return true
}

const poll = async () => {
  if (polling) return
  polling = true
  try {
    const last = messages.value.length ? messages.value[messages.value.length - 1].id : 0
    const data = await liteApi.messages(props.roomId, last)
    failing = false
    if (await append(data.messages)) emit('received')
  } catch (error) {
    // 폴링은 3초마다 반복되므로 실패가 이어져도 토스트는 한 번만 띄운다
    if (!failing) store.notify(error.message, 'error')
    failing = true
  } finally {
    polling = false
  }
}

const send = async () => {
  const body = draft.value.trim()
  if (!body || sending.value) return
  sending.value = true
  const data = await store.act(() => liteApi.sendMessage(props.roomId, body))
  sending.value = false
  if (!data) return
  draft.value = ''
  await append([data.message])
  emit('sent')
  poll()
}

onMounted(() => {
  poll()
  timer = setInterval(poll, POLL_MS)
})
onBeforeUnmount(() => clearInterval(timer))

defineExpose({ poll })
</script>
