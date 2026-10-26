<template>
  <!-- 미신청자는 아래 안내 패널에 같은 정보가 있으므로, 취소·내보냄 안내가 필요할 때만 요약 줄을 둔다 -->
  <div
    v-if="joined || store.isHost || meetup.cancelled || detail.removed"
    class="l-bar"
  >
    <img
      v-if="meetup.thumb_url"
      class="l-thumb sm"
      :src="meetup.thumb_url"
      alt=""
    >
    <CalendarDays
      v-else
      :size="18"
    />
    <span class="l-grow">{{ when }} {{ parts.time }} · {{ meetup.location }}</span>
    <span
      v-if="!store.isHost && detail.removed"
      class="l-chip no"
    >운영자가 내보낸 모임이에요</span>
    <span
      v-else-if="!store.isHost && meetup.cancelled"
      class="l-chip no"
    >취소된 모임이에요</span>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { CalendarDays } from 'lucide-vue-next'
import { dateParts, daysUntilLabel } from '../format'
import { useLiteStore } from '../store'

const props = defineProps({
  meetup: { type: Object, required: true },
  detail: { type: Object, required: true },
})

// 채팅방 위 요약 줄. 참석 여부는 홈 스위치에서, 모임 안내는 모임 정보 화면에서 다룬다.
const store = useLiteStore()
const parts = computed(() => dateParts(props.meetup.starts_at))
const joined = computed(() => ['going', 'maybe'].includes(props.meetup.my_status))
const dday = computed(() => daysUntilLabel(props.meetup.starts_at))
const when = computed(() => (props.meetup.is_today ? '오늘' : `${parts.value.month}/${parts.value.day}(${parts.value.weekday}) · ${dday.value}`))
</script>
