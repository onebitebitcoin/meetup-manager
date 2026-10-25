<template>
  <dl class="l-info">
    <div class="l-info-row">
      <dt><CalendarDays :size="20" />언제</dt>
      <dd>
        {{ longDate(meetup.starts_at) }} {{ koreanTime(meetup.starts_at) }}
        <span
          v-if="dday"
          class="l-info-sub"
        >{{ dday }}</span>
      </dd>
    </div>
    <div class="l-info-row">
      <dt><MapPin :size="20" />어디서</dt>
      <dd>{{ meetup.location }}</dd>
    </div>
    <div class="l-info-row">
      <dt><Users :size="20" />정원</dt>
      <dd>
        {{ meetup.capacity }}명
        <span class="l-info-sub">지금 {{ meetup.going_count }}명 참석</span>
      </dd>
    </div>
    <div
      v-if="audience"
      class="l-info-row"
    >
      <dt><UserCheck :size="20" />대상</dt>
      <dd>{{ audience }}</dd>
    </div>
    <div
      v-if="description"
      class="l-info-row l-info-long"
    >
      <dt><FileText :size="20" />내용</dt>
      <dd>{{ description }}</dd>
    </div>
  </dl>
</template>

<script setup>
import { computed } from 'vue'
import { CalendarDays, FileText, MapPin, UserCheck, Users } from 'lucide-vue-next'
import { daysUntilLabel, koreanTime, longDate } from '../format'

// 모임 안내: 언제, 어디서, 정원, 대상, 내용. 대상과 내용은 운영자가 적었을 때만 보인다.
const props = defineProps({
  meetup: { type: Object, required: true },
  description: { type: String, default: '' },
  audience: { type: String, default: '' },
})

const dday = computed(() => daysUntilLabel(props.meetup.starts_at))
</script>
