<template>
  <LiteTopbar
    :title="meetup ? meetup.title : '모임'"
    back
  >
    <span
      v-if="meetup"
      class="l-counts"
    >
      <Users :size="13" />{{ meetup.going_count }}/{{ meetup.capacity }}
    </span>
    <button
      v-if="meetup && store.isHost"
      class="l-icon-btn"
      aria-label="관리"
      @click="router.push(`/lite/admin/m/${meetup.id}`)"
    >
      <Settings :size="20" />
    </button>
  </LiteTopbar>
  <p
    v-if="error"
    class="l-state"
  >
    {{ error }}
  </p>
  <template v-else-if="meetup">
    <LiteRoomBar
      :meetup="meetup"
      :detail="detail"
      @rsvp="changeRsvp"
      @checkin="checkin"
    />
    <div
      v-if="!store.isHost && !joined"
      class="l-locked"
    >
      <div
        class="l-title"
        style="font-size: 24px; color: var(--lite-ink)"
      >
        {{ meetup.title }}
      </div>
      <span class="l-counts">{{ meetup.going_count }}명 참석</span>
      <LiteJoinRow
        :meetup="meetup"
        @done="load"
      />
    </div>
    <LiteChat
      v-else
      :key="meetup.room_id"
      :room-id="meetup.room_id"
    />
  </template>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Settings, Users } from 'lucide-vue-next'
import { liteApi } from '../api'
import { useLiteStore } from '../store'
import LiteChat from '../components/LiteChat.vue'
import LiteJoinRow from '../components/LiteJoinRow.vue'
import LiteRoomBar from '../components/LiteRoomBar.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

const route = useRoute()
const router = useRouter()
const store = useLiteStore()
const meetup = ref(null)
const detail = ref({ checkin_code: null, checked_in: false, checked_in_count: 0 })
const error = ref('')

const joined = computed(() => ['going', 'maybe'].includes(meetup.value?.my_status))

const load = async () => {
  try {
    const data = await liteApi.meetup(route.params.id)
    meetup.value = data.meetup
    detail.value = {
      checkin_code: data.checkin_code,
      checked_in: data.checked_in,
      checked_in_count: data.checked_in_count,
    }
    error.value = ''
  } catch (e) {
    error.value = e.message
    store.notify(e.message, 'error')
  }
}

const changeRsvp = async (status) => {
  const data = await store.act(() => liteApi.rsvp(meetup.value.id, status), '응답을 바꿨어요')
  if (data) await load()
}

const checkin = async (code) => {
  if (!/^\d{4}$/.test(code)) {
    store.notify('코드 4자리를 입력해 주세요', 'error')
    return
  }
  const data = await store.act(() => liteApi.checkin(meetup.value.id, code), '도착!')
  if (data) await load()
}

onMounted(() => {
  if (!store.member) router.replace('/lite')
  else load()
})
watch(() => route.params.id, load)
</script>
