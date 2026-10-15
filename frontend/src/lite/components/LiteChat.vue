<template>
  <div class="lite-scroll">
    <div
      v-if="pinned"
      class="l-pinbar"
    >
      <Pin :size="15" />
      <span class="l-pinbar-who">{{ pinned.member?.name }}</span>
      <span class="l-pinbar-body">{{ pinned.body }}</span>
      <button
        v-if="store.isHost"
        type="button"
        class="l-icon-btn"
        aria-label="공지 해제"
        @click="unpin"
      >
        <X :size="16" />
      </button>
    </div>
    <div class="l-msgs">
      <button
        v-if="hasMore"
        type="button"
        class="l-older"
        :disabled="loadingOlder"
        @click="loadOlder"
      >
        이전 메시지 보기
      </button>
      <LiteMessage
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :mine="message.kind === 'user' && message.member?.id === store.member?.id"
        :menu-open="openMenuId === message.id"
        @toggle-menu="openMenuId = openMenuId === message.id ? null : message.id"
        @pin="pin(message.id)"
        @delete="remove(message.id)"
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
import { Pin, Send, X } from 'lucide-vue-next'
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
const hasMore = ref(false)
const loadingOlder = ref(false)
const pinned = ref(null)
const openMenuId = ref(null)
let timer = null
let polling = false
let failing = false
// after 기준은 폴링으로 받은 마지막 id만 쓴다. 내가 보낸 메시지로 앞당기면 그 사이 다른 사람의 메시지가 누락된다.
let lastPolled = 0
let halted = false

const append = async (incoming) => {
  const known = new Set(messages.value.map((m) => m.id))
  const fresh = incoming.filter((m) => !known.has(m.id))
  if (!fresh.length) return false
  messages.value = [...messages.value, ...fresh].sort((a, b) => a.id - b.id)
  await nextTick()
  bottom.value?.scrollIntoView?.({ block: 'end' })
  return true
}

const stop = () => {
  clearInterval(timer)
  timer = null
}

const poll = async () => {
  if (polling || document.visibilityState === 'hidden') return
  polling = true
  try {
    const first = lastPolled === 0
    const data = await liteApi.messages(props.roomId, lastPolled)
    failing = false
    // 첫 조회(after 없음)는 최신 100개만 오므로, 더 오래된 메시지가 있는지 응답으로 알 수 있다
    if (first) hasMore.value = !!data.has_more
    pinned.value = data.pinned ?? null
    lastPolled = data.messages.reduce((max, m) => Math.max(max, m.id), lastPolled)
    if (await append(data.messages)) emit('received')
  } catch (error) {
    if (error.status === 401 || error.status === 403) {
      halted = true
      stop()
    }
    // 폴링은 3초마다 반복되므로 실패가 이어져도 토스트는 한 번만 띄운다
    if (!failing) store.notify(error.message, 'error')
    failing = true
  } finally {
    polling = false
  }
}

// 위로 붙일 때는 보던 위치가 밀려 내려가지 않도록, 늘어난 높이만큼 스크롤을 보정한다
const loadOlder = async () => {
  const oldest = messages.value[0]
  if (!oldest || loadingOlder.value) return
  loadingOlder.value = true
  const data = await store.act(() => liteApi.olderMessages(props.roomId, oldest.id))
  loadingOlder.value = false
  if (!data) return
  const scroller = document.scrollingElement
  const before = scroller?.scrollHeight ?? 0
  const known = new Set(messages.value.map((m) => m.id))
  messages.value = [...data.messages.filter((m) => !known.has(m.id)), ...messages.value]
  hasMore.value = !!data.has_more
  pinned.value = data.pinned ?? null
  await nextTick()
  if (scroller) scroller.scrollTop += scroller.scrollHeight - before
}

const pin = async (id) => {
  openMenuId.value = null
  const data = await store.act(() => liteApi.pinMessage(props.roomId, id), '공지로 고정했어요')
  if (data) pinned.value = data.pinned ?? null
}

const unpin = async () => {
  const data = await store.act(() => liteApi.pinMessage(props.roomId, null), '공지를 내렸어요')
  if (data) pinned.value = data.pinned ?? null
}

const remove = async (id) => {
  openMenuId.value = null
  const data = await store.act(() => liteApi.deleteMessage(props.roomId, id), '삭제했어요')
  if (!data) return
  messages.value = messages.value.filter((m) => m.id !== id)
  if (pinned.value?.id === id) pinned.value = null
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

const start = () => {
  stop()
  timer = setInterval(poll, POLL_MS)
}

// 탭이 숨겨지면 멈추고, 다시 보이면 즉시 한 번 가져온 뒤 재개한다
const onVisibility = () => {
  if (document.visibilityState === 'hidden') {
    stop()
  } else if (!halted) {
    poll()
    start()
  }
}

onMounted(() => {
  poll()
  start()
  document.addEventListener('visibilitychange', onVisibility)
})
onBeforeUnmount(() => {
  stop()
  document.removeEventListener('visibilitychange', onVisibility)
})

defineExpose({ poll })
</script>
