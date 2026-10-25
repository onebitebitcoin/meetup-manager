<template>
  <section class="l-next">
    <div class="l-next-head">
      <span>다음 모임<span
        v-if="dday"
        class="l-dday"
      > · {{ dday }}</span></span>
      <span class="l-next-date">{{ head.month }}.{{ head.day }} ({{ head.weekday }})</span>
    </div>
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
          <span class="l-next-time">{{ dateParts(meetup.starts_at).time }}</span>
          <span class="l-next-title">{{ meetup.title }}</span>
        </button>
        <span
          v-if="meetup.my_status && !store.isHost"
          class="l-chip"
          :class="meetup.my_status"
        >{{ STATUS_LABEL[meetup.my_status] }}</span>
        <LiteJoinRow
          v-else-if="!store.isHost"
          :meetup="meetup"
          compact
          @done="open(meetup)"
        />
      </div>
    </div>
    <div class="l-next-info">
      {{ places }} · 정원 {{ capacities }}
    </div>
  </section>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { dateParts, daysUntilLabel, STATUS_LABEL } from '../format'
import { useLiteStore } from '../store'
import LiteJoinRow from './LiteJoinRow.vue'

// meetups: 같은 날(서울 기준)에 열리는 모임들, 시작 시각 순
const props = defineProps({ meetups: { type: Array, required: true } })

const router = useRouter()
const store = useLiteStore()
const head = computed(() => dateParts(props.meetups[0].starts_at))
const dday = computed(() => daysUntilLabel(props.meetups[0].starts_at))
const places = computed(() => [...new Set(props.meetups.map((m) => m.location))].join(', '))
const capacities = computed(() => {
  const caps = [...new Set(props.meetups.map((m) => m.capacity))]
  if (caps.length === 1) return props.meetups.length > 1 ? `각 ${caps[0]}명` : `${caps[0]}명`
  return props.meetups.map((m) => `${m.capacity}명`).join(' / ')
})

const open = (meetup) => router.push(`/lite/m/${meetup.id}`)
</script>
