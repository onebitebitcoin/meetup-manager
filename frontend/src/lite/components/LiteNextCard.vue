<template>
  <section class="l-next">
    <img
      v-if="meetups[0].image_url"
      class="l-next-img"
      :src="meetups[0].image_url"
      alt=""
    >
    <div class="l-next-slots">
      <div
        v-for="meetup in meetups"
        :key="meetup.id"
        class="l-next-slot"
      >
        <button
          type="button"
          class="l-cardbtn l-next-open"
          @click="open(meetup)"
        >
          <span class="l-next-badge">
            <b>{{ shortDate(meetup.starts_at) }}</b>
            <span>{{ koreanTime(meetup.starts_at) }}</span>
          </span>
          <span class="l-next-title">{{ meetup.title }}</span>
        </button>
        <div class="l-next-actions">
          <!-- 응답한 회원은 홈에서 바로 참석/불참을 바꾼다. 아직 응답하지 않았으면 신청하기로 가입·신청한다. -->
          <button
            v-if="meetup.my_status && !store.isHost"
            type="button"
            role="switch"
            class="l-switch"
            :class="meetup.my_status"
            :aria-checked="meetup.my_status === 'going'"
            :aria-label="`${meetup.title} 참석`"
            :disabled="busyId === meetup.id"
            @click="toggle(meetup)"
          >
            <span class="l-switch-track"><span class="l-switch-thumb" /></span>
            <span class="l-switch-label">{{ STATUS_LABEL[meetup.my_status] }}</span>
          </button>
          <LiteJoinRow
            v-else-if="!store.isHost"
            :meetup="meetup"
            compact
            @done="openRoom(meetup)"
          />
          <button
            type="button"
            class="l-more"
            @click="open(meetup)"
          >
            자세히<ChevronRight :size="16" />
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronRight } from 'lucide-vue-next'
import { liteApi } from '../api'
import { dateParts, koreanTime, STATUS_LABEL } from '../format'
import { useLiteStore } from '../store'
import LiteJoinRow from './LiteJoinRow.vue'

// meetups: 같은 날(서울 기준)에 열리는 모임들, 시작 시각 순
defineProps({ meetups: { type: Array, required: true } })
// 참석/불참을 바꾸면 홈이 목록을 다시 불러오도록 알린다
const emit = defineEmits(['changed'])

const router = useRouter()
const store = useLiteStore()

const busyId = ref(null)

// 원형 배지 첫 줄: "11/8 (일)"
const shortDate = (iso) => {
  const p = dateParts(iso)
  return `${p.month}/${p.day} (${p.weekday})`
}

// 자세히와 제목은 모임 정보 화면으로, 신청 직후는 채팅방으로 보낸다
const open = (meetup) => router.push(`/lite/m/${meetup.id}/info`)
const openRoom = (meetup) => router.push(`/lite/m/${meetup.id}`)

const toggle = async (meetup) => {
  if (busyId.value) return
  const next = meetup.my_status === 'going' ? 'no' : 'going'
  busyId.value = meetup.id
  const data = await store.act(() => liteApi.rsvp(meetup.id, next), next === 'going' ? '참석으로 바꿨어요' : '불참으로 바꿨어요')
  busyId.value = null
  if (data) emit('changed')
}
</script>
