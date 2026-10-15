<template>
  <LiteTopbar
    :title="data ? data.meetup.title : '모임 관리'"
    back
    back-to="/lite/admin"
  >
    <span />
  </LiteTopbar>
  <p
    v-if="error"
    class="l-state"
  >
    {{ error }}
  </p>
  <p
    v-else-if="!data"
    class="l-state"
  >
    불러오는 중
  </p>
  <div
    v-else
    class="l-body"
  >
    <span
      v-if="data.meetup.cancelled"
      class="l-chip no"
    >취소됨</span>
    <LiteMeetupForm
      :initial="initial"
      show-image
      @change="values = $event"
    />
    <button
      class="l-btn p"
      :disabled="busy"
      @click="save"
    >
      저장
    </button>

    <div class="l-section">
      <h3>참석자 {{ data.attendees.length }}명</h3>
      <div
        v-for="a in data.attendees"
        :key="a.member.id"
        class="l-person"
      >
        <div class="l-grow">
          {{ a.member.name }}
        </div>
        <span
          class="l-chip"
          :class="a.status"
        >{{ STATUS_LABEL[a.status] }}</span>
        <span
          v-if="a.checked_in_at"
          class="l-chip plum"
        >도착</span>
        <span
          v-if="a.removed"
          class="l-chip no"
        >내보냄</span>
        <template v-else>
          <div
            v-if="removing === a.member.id"
            class="l-confirm"
          >
            <span>내보낼까요?</span>
            <button
              class="l-btn p"
              :disabled="busy"
              @click="remove(a.member.id)"
            >
              내보내기
            </button>
            <button
              class="l-btn s"
              @click="removing = null"
            >
              그만두기
            </button>
          </div>
          <button
            v-else
            class="l-btn s"
            @click="removing = a.member.id"
          >
            내보내기
          </button>
        </template>
      </div>
    </div>

    <button
      class="l-btn s"
      @click="router.push(`/lite/m/${data.meetup.id}`)"
    >
      <MessageCircle :size="18" />채팅방 열기
    </button>

    <div class="l-section">
      <button
        class="l-btn s"
        :disabled="busy"
        @click="toggleCancel"
      >
        {{ data.meetup.cancelled ? '취소 되돌리기' : '모임 취소' }}
      </button>
      <div
        v-if="deleting"
        class="l-confirm"
      >
        <span>삭제할까요?</span>
        <button
          class="l-btn p"
          :disabled="busy"
          @click="destroy"
        >
          삭제
        </button>
        <button
          class="l-btn s"
          @click="deleting = false"
        >
          그만두기
        </button>
      </div>
      <button
        v-else
        class="l-btn s"
        @click="deleting = true"
      >
        <Trash2 :size="18" />삭제
      </button>
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { MessageCircle, Trash2 } from 'lucide-vue-next'
import { liteApi } from '../api'
import { STATUS_LABEL, toSeoulIso, toSeoulParts } from '../format'
import { useLiteStore } from '../store'
import LiteMeetupForm from '../components/LiteMeetupForm.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

const route = useRoute()
const router = useRouter()
const store = useLiteStore()
const data = ref(null)
const initial = ref({})
const values = ref({})
const error = ref('')
const busy = ref(false)
const removing = ref(null)
const deleting = ref(false)

const apply = (next) => {
  data.value = next
  const m = next.meetup
  initial.value = {
    title: m.title,
    ...toSeoulParts(m.starts_at),
    location: m.location,
    capacity: m.capacity,
    description: next.description || '',
    image_url: next.image_url || '',
  }
}

const load = async () => {
  try {
    apply(await liteApi.adminMeetup(route.params.id))
    error.value = ''
  } catch (e) {
    error.value = e.message
    store.notify(e.message, 'error')
  }
}

// 서버 동작을 실행하고 성공하면 응답으로 화면을 갱신한다
const run = async (fn, okMessage) => {
  busy.value = true
  const result = await store.act(fn, okMessage)
  busy.value = false
  if (result) apply(result)
  return result
}

const save = () => {
  const v = values.value
  if (!v.title.trim() || !v.date || !v.time || !v.location.trim() || !v.capacity) {
    store.notify('모든 항목을 입력해 주세요', 'error')
    return Promise.resolve(null)
  }
  const body = {
    title: v.title.trim(),
    starts_at: toSeoulIso(v.date, v.time),
    location: v.location.trim(),
    capacity: v.capacity,
    description: v.description.trim(),
    image_url: v.image_url.trim(),
  }
  return run(() => liteApi.updateMeetup(data.value.meetup.id, body), '저장했어요')
}

const remove = async (memberId) => {
  await run(() => liteApi.removeAttendee(data.value.meetup.id, memberId), '내보냈어요')
  removing.value = null
}

const toggleCancel = () => {
  const cancelled = !data.value.meetup.cancelled
  return run(() => liteApi.cancelMeetup(data.value.meetup.id, cancelled), cancelled ? '모임을 취소했어요' : '취소를 되돌렸어요')
}

const destroy = async () => {
  busy.value = true
  const result = await store.act(() => liteApi.deleteMeetup(data.value.meetup.id), '삭제했어요')
  busy.value = false
  if (result) router.push('/lite/admin')
}

onMounted(() => {
  if (!store.isHost) {
    router.replace('/lite')
    return
  }
  load()
})
watch(() => route.params.id, load)
</script>
