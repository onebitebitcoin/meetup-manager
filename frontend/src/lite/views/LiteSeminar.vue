<template>
  <LiteTopbar
    :title="title"
    back
  >
    <span />
  </LiteTopbar>
  <p
    v-if="error"
    class="l-state"
  >
    {{ error }}
  </p>
  <template v-else-if="seminar">
    <div class="l-bar">
      <Lock :size="18" />
      <span class="l-grow">{{ barText }}</span>
      <span
        v-if="seminar.status !== 'guide'"
        class="l-chip"
        :class="STATUS_CLASS[seminar.status]"
      >{{ SEMINAR_STATUS_LABEL[seminar.status] }}</span>
      <button
        v-if="store.isHost && seminar.status === 'received'"
        class="l-btn p"
        :disabled="confirming"
        @click="confirm"
      >
        확정
      </button>
    </div>
    <LiteChat
      ref="chat"
      :key="seminar.room_id"
      :room-id="seminar.room_id"
      :can-send="store.isHost || !!seminar.mode"
      :placeholder="placeholder"
      @sent="refresh"
    >
      <template
        v-if="!store.isHost && !seminar.mode"
        #after
      >
        <div class="l-choices">
          <button
            v-for="(label, mode) in MODE_LABEL"
            :key="mode"
            class="l-choice"
            :disabled="choosing"
            @click="choose(mode)"
          >
            <component
              :is="mode === 'online' ? Monitor : MapPin"
              :size="18"
            />{{ label }}
          </button>
        </div>
      </template>
    </LiteChat>
  </template>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { Lock, MapPin, Monitor } from 'lucide-vue-next'
import { liteApi } from '../api'
import { MODE_LABEL, SEMINAR_STATUS_LABEL } from '../format'
import { useLiteStore } from '../store'
import LiteChat from '../components/LiteChat.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

const STATUS_CLASS = { guide: 'none', received: 'maybe', confirmed: 'going' }
const route = useRoute()
const store = useLiteStore()
const seminar = ref(null)
const chat = ref(null)
const error = ref('')
const choosing = ref(false)
const confirming = ref(false)

const title = computed(() => (store.isHost && seminar.value ? `1:1 · ${seminar.value.member.name}` : '1:1 세미나'))
const barText = computed(() => {
  if (!store.isHost) return '운영자와 둘만 봐요'
  return seminar.value.mode ? MODE_LABEL[seminar.value.mode] : '방식 선택 전'
})
const placeholder = computed(() => {
  if (store.isHost) return '메시지'
  return seminar.value?.status === 'guide' ? '주제, 희망 일정' : '메시지'
})

// 내 세미나는 get-or-create, 운영자는 홈 목록에서 해당 세미나를 찾는다
const fetchSeminar = async () => {
  if (!store.isHost) return (await liteApi.seminar()).seminar
  const found = (await liteApi.home()).seminars.find((s) => String(s.id) === route.params.id)
  if (!found) throw new Error('세미나를 찾을 수 없어요')
  return found
}

const refresh = async () => {
  try {
    const previous = seminar.value?.status
    seminar.value = await fetchSeminar()
    error.value = ''
    if (!store.isHost && previous === 'guide' && seminar.value.status === 'received') store.notify('접수됐어요')
  } catch (e) {
    error.value = e.message
    store.notify(e.message, 'error')
  }
}

const choose = async (mode) => {
  if (choosing.value) return
  choosing.value = true
  const data = await store.act(() => liteApi.seminarMode(mode))
  choosing.value = false
  if (!data) return
  seminar.value = data.seminar
  chat.value?.poll()
}

const confirm = async () => {
  confirming.value = true
  const data = await store.act(() => liteApi.confirmSeminar(seminar.value.id), '확정했어요')
  confirming.value = false
  if (!data) return
  seminar.value = data.seminar
  chat.value?.poll()
}

onMounted(async () => {
  if (await store.ensureMember()) refresh()
})
</script>
