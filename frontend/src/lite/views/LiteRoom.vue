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
      @click="router.push(`/admin/m/${meetup.id}`)"
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
    />
    <div
      v-if="!store.isHost && !joined"
      class="l-intro"
    >
      <LiteMeetupInfo
        :meetup="meetup"
        :description="detail.description"
        :audience="detail.audience"
      />
      <LiteJoinRow
        v-if="!detail.removed"
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
import LiteMeetupInfo from '../components/LiteMeetupInfo.vue'
import LiteRoomBar from '../components/LiteRoomBar.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

const route = useRoute()
const router = useRouter()
const store = useLiteStore()
const meetup = ref(null)
const detail = ref({ removed: undefined, description: '', audience: '' })
const error = ref('')

const joined = computed(() => ['going', 'maybe'].includes(meetup.value?.my_status))

const load = async () => {
  try {
    const data = await liteApi.meetup(route.params.id)
    meetup.value = data.meetup
    detail.value = {
      removed: data.removed,
      description: data.description || '',
      audience: data.audience || '',
    }
    error.value = ''
  } catch (e) {
    error.value = e.message
    store.notify(e.message, 'error')
  }
}

const changeRsvp = async (status) => {
  const data = await store.act(
    () => liteApi.rsvp(meetup.value.id, status),
    status === 'going' ? '참석으로 바꿨어요' : '불참으로 바꿨어요',
    status,
  )
  if (data) await load()
}

onMounted(load)
watch(() => route.params.id, load)
</script>
