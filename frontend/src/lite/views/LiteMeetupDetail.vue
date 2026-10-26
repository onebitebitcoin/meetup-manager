<template>
  <LiteTopbar
    :title="meetup ? meetup.title : '모임'"
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
  <div
    v-else-if="meetup"
    class="l-intro"
  >
    <p
      v-if="notice"
      class="l-state"
    >
      {{ notice }}
    </p>
    <LiteMeetupInfo
      :meetup="meetup"
      :description="description"
      :audience="audience"
    />
    <!-- 신청한 회원과 운영자는 채팅방에서 공지를 본다. 아직 신청하지 않았으면 신청부터 받는다. -->
    <button
      v-if="joined || store.isHost"
      type="button"
      class="l-btn p"
      @click="openRoom"
    >
      <Megaphone :size="20" />공지 확인하기
      <span
        v-if="unread > 0"
        class="l-badge"
        :aria-label="`안 읽은 대화 ${unread}개`"
      >{{ unread > 99 ? '99+' : unread }}</span>
    </button>
    <LiteJoinRow
      v-else-if="!notice"
      :meetup="meetup"
      @done="openRoom"
    />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Megaphone } from 'lucide-vue-next'
import { liteApi } from '../api'
import { useLiteStore } from '../store'
import LiteJoinRow from '../components/LiteJoinRow.vue'
import LiteMeetupInfo from '../components/LiteMeetupInfo.vue'
import LiteTopbar from '../components/LiteTopbar.vue'

// 홈의 "자세히"에서 오는 모임 정보 화면. 채팅방(/m/:id)으로 가기 전 단계다.
const route = useRoute()
const router = useRouter()
const store = useLiteStore()
const meetup = ref(null)
const description = ref('')
const audience = ref('')
// 채팅방에서 아직 읽지 않은 대화 수(신청한 회원·운영자만 서버가 센다)
const unread = ref(0)
const removed = ref(false)
const error = ref('')

const joined = computed(() => ['going', 'maybe'].includes(meetup.value?.my_status))
const notice = computed(() => {
  if (store.isHost) return ''
  if (removed.value) return '운영자가 내보낸 모임이에요'
  if (meetup.value?.cancelled) return '취소된 모임이에요'
  return ''
})

const load = async () => {
  try {
    const data = await liteApi.meetup(route.params.id)
    meetup.value = data.meetup
    description.value = data.description || ''
    audience.value = data.audience || ''
    removed.value = Boolean(data.removed)
    unread.value = data.unread_count || 0
    error.value = ''
  } catch (e) {
    error.value = e.message
    store.notify(e.message, 'error')
  }
}

const openRoom = () => router.push(`/m/${route.params.id}`)

onMounted(load)
watch(() => route.params.id, load)
</script>
