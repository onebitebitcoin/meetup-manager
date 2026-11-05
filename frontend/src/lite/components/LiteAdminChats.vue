<template>
  <p
    v-if="error"
    class="l-state"
  >
    {{ error }}
  </p>
  <p
    v-else-if="!loaded"
    class="l-state"
  >
    불러오는 중
  </p>
  <p
    v-else-if="!rooms.length"
    class="l-state"
  >
    채팅방이 없어요
  </p>
  <button
    v-for="room in rooms"
    :key="room.room_id"
    class="l-row-btn"
    @click="router.push(pathOf(room))"
  >
    <div class="l-grow">
      <div class="l-title">
        {{ room.title }}
      </div>
      <div class="l-sub">
        <span class="l-chip">{{ room.kind === 'seminar' ? '세미나' : '모임' }}</span>
        <span
          v-if="room.cancelled"
          class="l-chip no"
        >취소됨</span>
        <span>{{ preview(room) }}</span>
      </div>
    </div>
    <div class="l-sub">
      <span v-if="room.last_message">{{ shortDateTime(room.last_message.created_at) }}</span>
      <span
        v-if="room.unread_count"
        class="l-badge"
      >{{ room.unread_count > 99 ? '99+' : room.unread_count }}</span>
    </div>
  </button>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { liteApi } from '../api'
import { shortDateTime } from '../format'
import { useLiteStore } from '../store'

const router = useRouter()
const store = useLiteStore()
const rooms = ref([])
const error = ref('')
const loaded = ref(false)

const pathOf = (room) => (room.kind === 'seminar' ? `/seminar/${room.seminar_id}?from=admin` : `/m/${room.meetup_id}?from=admin`)

const preview = (room) => {
  if (!room.last_message) return '메시지가 없어요'
  return room.last_message.body.trim() ? room.last_message.body : '첨부 파일'
}

onMounted(async () => {
  try {
    rooms.value = (await liteApi.adminRooms()).rooms
  } catch (e) {
    error.value = e.message
    store.notify(e.message, 'error')
  }
  loaded.value = true
})
</script>
