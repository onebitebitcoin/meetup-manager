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
    <button
      v-else-if="joined || store.isHost"
      type="button"
      :aria-expanded="infoOpen"
      @click="infoOpen = !infoOpen"
    >
      안내<component
        :is="infoOpen ? ChevronUp : ChevronDown"
        :size="14"
      />
    </button>
  </div>
  <div
    v-if="infoOpen"
    class="l-bar l-bar-info"
  >
    <LiteMeetupInfo
      :meetup="meetup"
      :description="detail.description"
      :audience="detail.audience"
    />
  </div>
  <div
    v-if="joined && !store.isHost && !meetup.cancelled && !detail.removed"
    class="l-bar"
  >
    <span class="l-rsvp-label">내 참석</span>
    <div
      class="l-rsvp two"
      role="group"
      aria-label="참석 여부"
    >
      <button
        v-for="status in ['going', 'no']"
        :key="status"
        type="button"
        :data-v="status"
        :aria-pressed="meetup.my_status === status"
        @click="pick(status)"
      >
        <component
          :is="ICONS[status]"
          :size="18"
        />{{ STATUS_LABEL[status] }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  CalendarDays, Check, ChevronDown, ChevronUp, X,
} from 'lucide-vue-next'
import { dateParts, daysUntilLabel, STATUS_LABEL } from '../format'
import { useLiteStore } from '../store'
import LiteMeetupInfo from './LiteMeetupInfo.vue'

const props = defineProps({
  meetup: { type: Object, required: true },
  detail: { type: Object, required: true },
})
const emit = defineEmits(['rsvp'])

// 응답은 참석/불참 두 가지만 고른다. 예전에 고른 미정은 둘 다 눌리지 않은 상태로 보인다.
const ICONS = { going: Check, no: X }
const store = useLiteStore()
const infoOpen = ref(false)
const parts = computed(() => dateParts(props.meetup.starts_at))
const joined = computed(() => ['going', 'maybe'].includes(props.meetup.my_status))
const dday = computed(() => daysUntilLabel(props.meetup.starts_at))
const when = computed(() => (props.meetup.is_today ? '오늘' : `${parts.value.month}/${parts.value.day}(${parts.value.weekday}) · ${dday.value}`))

const pick = (status) => {
  if (status !== props.meetup.my_status) emit('rsvp', status)
}
</script>
