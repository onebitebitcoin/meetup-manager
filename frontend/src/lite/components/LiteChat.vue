<template>
  <div class="l-chatbox">
    <div
      v-if="pinned"
      class="l-pinbar"
    >
      <Pin :size="15" />
      <span class="l-pinbar-who">{{ pinned.member?.name }}</span>
      <span class="l-pinbar-body">{{ pinned.body || (pinned.attachment && attachmentLabel(pinned.attachment)) }}</span>
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
    <div
      ref="scroller"
      class="l-msgs"
    >
      <button
        v-if="hasMore"
        type="button"
        class="l-older"
        :disabled="loadingOlder"
        @click="loadOlder"
      >
        이전 메시지 보기
      </button>
      <template
        v-for="{ message, day, head, time } in rows"
        :key="message.id"
      >
        <div
          v-if="day"
          class="l-day"
        >
          {{ day }}
        </div>
        <LiteMessage
          :message="message"
          :mine="message.kind === 'user' && message.member?.id === store.member?.id"
          :head="head"
          :time="time"
          :menu-open="openMenuId === message.id"
          @toggle-menu="openMenuId = openMenuId === message.id ? null : message.id"
          @pin="pin(message.id)"
          @delete="remove(message.id)"
          @media-loaded="keepBottom"
        />
      </template>
      <slot name="after" />
    </div>
    <div
      v-if="canSend && attachment"
      class="l-attach-preview"
    >
      <img
        v-if="previewUrl"
        :src="previewUrl"
        alt=""
      >
      <FileText
        v-else
        :size="20"
      />
      <span class="l-att-name">{{ attachment.name }}</span>
      <button
        type="button"
        class="l-icon-btn"
        aria-label="첨부 취소"
        @click="clearAttachment"
      >
        <X :size="18" />
      </button>
    </div>
    <form
      v-if="canSend"
      class="l-composer"
      @submit.prevent="send"
    >
      <button
        type="button"
        class="l-attach-btn"
        aria-label="파일 첨부"
        :disabled="sending"
        @click="fileInput?.click()"
      >
        <Paperclip :size="20" />
      </button>
      <input
        v-model="draft"
        :placeholder="placeholder"
        maxlength="1000"
        autocomplete="off"
        aria-label="메시지"
      >
      <input
        ref="fileInput"
        type="file"
        class="l-file-input"
        tabindex="-1"
        @change="pickFile"
      >
      <button
        type="submit"
        aria-label="보내기"
        :disabled="sending"
      >
        <Send :size="18" />
      </button>
    </form>
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'
import { FileText, Paperclip, Pin, Send, X } from 'lucide-vue-next'
import { liteApi } from '../api'
import { useLiteStore } from '../store'
import LiteMessage from './LiteMessage.vue'
import { layoutMessages } from '../format'
import { MAX_UPLOAD_BYTES, attachmentLabel } from '../attachment'

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
const fileInput = ref(null)
const attachment = ref(null)
const previewUrl = ref('')
const scroller = ref(null)
const hasMore = ref(false)
const loadingOlder = ref(false)
const pinned = ref(null)
const openMenuId = ref(null)
const rows = computed(() => layoutMessages(messages.value))
let timer = null
let polling = false
let failing = false
// after 기준은 폴링으로 받은 마지막 id만 쓴다. 내가 보낸 메시지로 앞당기면 그 사이 다른 사람의 메시지가 누락된다.
let lastPolled = 0
let halted = false

const isAtBottom = () => {
  const box = scroller.value
  return !box || box.scrollHeight - box.scrollTop - box.clientHeight < 80
}

// 이미지가 늦게 로드되면 높이가 늘어나 맨 아래에서 밀려나므로, 보던 곳이 맨 아래였다면 다시 맞춘다
let stickBottom = true
const keepBottom = () => {
  if (stickBottom && scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight
}

const append = async (incoming) => {
  const known = new Set(messages.value.map((m) => m.id))
  const fresh = incoming.filter((m) => !known.has(m.id))
  if (!fresh.length) return false
  stickBottom = isAtBottom()
  messages.value = [...messages.value, ...fresh].sort((a, b) => a.id - b.id)
  await nextTick()
  if (scroller.value) scroller.value.scrollTop = scroller.value.scrollHeight
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
  const box = scroller.value
  const before = box?.scrollHeight ?? 0
  const known = new Set(messages.value.map((m) => m.id))
  messages.value = [...data.messages.filter((m) => !known.has(m.id)), ...messages.value]
  hasMore.value = !!data.has_more
  pinned.value = data.pinned ?? null
  await nextTick()
  if (box) box.scrollTop += box.scrollHeight - before
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

const clearAttachment = () => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  previewUrl.value = ''
  attachment.value = null
  if (fileInput.value) fileInput.value.value = ''
}

const pickFile = (event) => {
  const file = event.target.files?.[0]
  if (!file) return
  if (file.size > MAX_UPLOAD_BYTES) {
    clearAttachment()
    store.notify('파일은 10MB까지 올릴 수 있어요', 'error')
    return
  }
  clearAttachment()
  attachment.value = file
  if (file.type.startsWith('image/')) previewUrl.value = URL.createObjectURL(file)
}

const send = async () => {
  const body = draft.value.trim()
  const file = attachment.value
  if ((!body && !file) || sending.value) return
  sending.value = true
  const data = await store.act(() => (
    file ? liteApi.uploadFile(props.roomId, file, body) : liteApi.sendMessage(props.roomId, body)
  ))
  sending.value = false
  if (!data) return
  draft.value = ''
  clearAttachment()
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
  clearAttachment()
  document.removeEventListener('visibilitychange', onVisibility)
})

defineExpose({ poll })
</script>
