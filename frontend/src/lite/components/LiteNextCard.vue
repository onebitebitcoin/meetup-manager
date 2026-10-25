<template>
  <section class="l-next">
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
          <!-- 같은 날 모임이라도 썸네일은 모임마다 다르므로 줄마다 자기 사진을 둔다 -->
          <img
            v-if="meetup.image_url"
            class="l-next-thumb"
            :src="meetup.image_url"
            alt=""
            loading="lazy"
          >
          <span class="l-next-badge">
            <b>{{ shortDate(meetup.starts_at) }}</b>
            <span>{{ koreanTime(meetup.starts_at) }}</span>
          </span>
          <span class="l-next-title">{{ meetup.title }}</span>
        </button>
        <div class="l-next-actions">
          <LiteRsvpSwitch
            v-if="!store.isHost"
            :meetup="meetup"
            @changed="emit('changed')"
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
import { useRouter } from 'vue-router'
import { ChevronRight } from 'lucide-vue-next'
import { dateParts, koreanTime } from '../format'
import { useLiteStore } from '../store'
import LiteRsvpSwitch from './LiteRsvpSwitch.vue'

// meetups: 같은 날(서울 기준)에 열리는 모임들, 시작 시각 순
defineProps({ meetups: { type: Array, required: true } })
// 참석/불참을 바꾸면 홈이 목록을 다시 불러오도록 알린다
const emit = defineEmits(['changed'])

const router = useRouter()
const store = useLiteStore()

// 원형 배지 첫 줄: "11/8 (일)"
const shortDate = (iso) => {
  const p = dateParts(iso)
  return `${p.month}/${p.day} (${p.weekday})`
}

// 자세히와 제목은 모임 정보 화면으로 보낸다
const open = (meetup) => router.push(`/lite/m/${meetup.id}/info`)
</script>
