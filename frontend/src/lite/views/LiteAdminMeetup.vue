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
    class="l-body l-body-toast"
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
      <h3>참석 {{ goingCount }}/{{ data.meetup.capacity }}명</h3>
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
          class="l-btn p danger"
          :disabled="busy"
          @click="destroy"
        >
          <Trash2 :size="18" />삭제
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
        class="l-btn s danger"
        @click="deleting = true"
      >
        <Trash2 :size="18" />삭제
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
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

const goingCount = computed(() => (data.value?.attendees || []).filter((a) => a.status === 'going' && !a.removed).length)

// 명단과 취소 상태만 갱신한다. 폼 값(initial)은 건드리지 않아 입력 중인 내용이 남는다.
const apply = (next) => {
  data.value = next
}

// 폼의 기준값은 처음 불러올 때와 저장에 성공했을 때만 서버 값으로 맞춘다
const applyForm = (next) => {
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
    const next = await liteApi.adminMeetup(route.params.id)
    apply(next)
    applyForm(next)
    error.value = ''
  } catch (e) {
    error.value = e.message
    store.notify(e.message, 'error')
  }
}

// 서버 동작을 실행하고 성공하면 응답으로 화면을 갱신한다
const run = async (fn, okMessage, { syncForm = false } = {}) => {
  busy.value = true
  const result = await store.act(fn, okMessage)
  busy.value = false
  if (result) {
    apply(result)
    if (syncForm) applyForm(result)
  }
  return result
}

const save = () => {
  const v = values.value
  if (!v.title.trim() || !v.date || !v.time || !v.location.trim() || !v.capacity) {
    store.notify('모든 항목을 입력해 주세요', 'error')
    return Promise.resolve(null)
  }
  const base = initial.value
  const next = {
    title: v.title.trim(),
    location: v.location.trim(),
    capacity: v.capacity,
    description: v.description.trim(),
    image_url: v.image_url.trim(),
  }
  const body = Object.fromEntries(Object.entries(next).filter(([key, value]) => value !== base[key]))
  if (v.date !== base.date || v.time !== base.time) body.starts_at = toSeoulIso(v.date, v.time)
  if (Object.keys(body).length === 0) {
    store.notify('바뀐 내용이 없어요')
    return Promise.resolve(null)
  }
  return run(() => liteApi.updateMeetup(data.value.meetup.id, body), '저장했어요', { syncForm: true })
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
