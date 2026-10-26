<template>
  <!-- 줄 전체가 버튼이면 안에 스위치를 둘 수 없으므로, 모임 열기 버튼과 참석 스위치를 나란히 둔다 -->
  <div class="l-mrow">
    <button
      type="button"
      class="l-cardbtn l-mrow-open"
      @click="router.push(`/m/${meetup.id}`)"
    >
      <span class="l-mrow-date">{{ parts.month }}.{{ parts.day }} {{ parts.weekday }}</span>
      <span class="l-grow">
        <span class="l-mrow-title">{{ meetup.title }}</span>
        <span class="l-mrow-sub">{{ parts.time }} · {{ meetup.location }}</span>
      </span>
      <img
        v-if="meetup.thumb_url"
        class="l-thumb sm"
        :src="meetup.thumb_url"
        alt=""
        loading="lazy"
      >
      <span
        v-else
        class="l-thumb sm l-thumb-empty"
        aria-hidden="true"
      />
      <span
        v-if="meetup.cancelled"
        class="l-chip no"
      >취소됨</span>
      <ChevronRight
        :size="18"
        class="l-mrow-go"
      />
    </button>
    <div
      v-if="!store.isHost && !meetup.cancelled"
      class="l-mrow-rsvp"
    >
      <LiteRsvpSwitch
        :meetup="meetup"
        @changed="emit('changed')"
      />
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronRight } from 'lucide-vue-next'
import { dateParts } from '../format'
import { useLiteStore } from '../store'
import LiteRsvpSwitch from './LiteRsvpSwitch.vue'

const props = defineProps({ meetup: { type: Object, required: true } })
const emit = defineEmits(['changed'])

const router = useRouter()
const store = useLiteStore()
const parts = computed(() => dateParts(props.meetup.starts_at))
</script>
