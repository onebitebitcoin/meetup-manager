<template>
  <div class="l-bar">
    <CalendarDays :size="18" />
    <span class="l-grow">{{ when }} {{ parts.time }} · {{ meetup.location }}</span>
    <span
      v-if="!store.isHost && meetup.cancelled"
      class="l-chip no"
    >취소된 모임이에요</span>
    <button
      v-else-if="!store.isHost"
      :class="meetup.my_status || 'none'"
      :aria-expanded="open"
      @click="open = !open"
    >
      {{ STATUS_LABEL[meetup.my_status] || '응답' }}<ChevronDown :size="12" />
    </button>
  </div>
  <div
    v-if="open && !store.isHost && !meetup.cancelled"
    class="l-bar"
  >
    <div class="l-rsvp">
      <button
        v-for="status in ['going', 'maybe', 'no']"
        :key="status"
        :data-v="status"
        :aria-pressed="meetup.my_status === status"
        @click="pick(status)"
      >
        <component
          :is="ICONS[status]"
          :size="16"
        />{{ STATUS_LABEL[status] }}
      </button>
    </div>
  </div>
  <div
    v-if="store.isHost && meetup.is_today && detail.checkin_code"
    class="l-bar strong"
  >
    <QrCode :size="18" />
    <span class="l-grow">도착 코드</span>
    <b class="l-code">{{ detail.checkin_code }}</b>
    <span class="l-counts">{{ detail.checked_in_count }}/{{ meetup.going_count }}</span>
  </div>
  <div
    v-else-if="joined && meetup.is_today && detail.checked_in"
    class="l-bar strong"
  >
    <CheckCircle2 :size="18" />
    <span class="l-grow">도착 완료</span>
  </div>
  <form
    v-else-if="joined && meetup.is_today"
    class="l-bar strong"
    @submit.prevent="emit('checkin', code)"
  >
    <MapPin :size="18" />
    <input
      v-model="code"
      class="l-pin"
      inputmode="numeric"
      maxlength="4"
      placeholder="도착 코드"
      aria-label="도착 코드 4자리"
    >
    <button
      class="l-btn p"
      type="submit"
    >
      도착
    </button>
  </form>
</template>

<script setup>
import { computed, ref } from 'vue'
import {
  CalendarDays, CheckCircle2, Check, ChevronDown, HelpCircle, MapPin, QrCode, X,
} from 'lucide-vue-next'
import { dateParts, daysUntilLabel, STATUS_LABEL } from '../format'
import { useLiteStore } from '../store'

const props = defineProps({
  meetup: { type: Object, required: true },
  detail: { type: Object, required: true },
})
const emit = defineEmits(['rsvp', 'checkin'])

const ICONS = { going: Check, maybe: HelpCircle, no: X }
const store = useLiteStore()
const open = ref(false)
const code = ref('')
const parts = computed(() => dateParts(props.meetup.starts_at))
const joined = computed(() => ['going', 'maybe'].includes(props.meetup.my_status))
const dday = computed(() => daysUntilLabel(props.meetup.starts_at))
const when = computed(() => (props.meetup.is_today ? '오늘' : `${parts.value.month}/${parts.value.day}(${parts.value.weekday}) · ${dday.value}`))

const pick = (status) => {
  open.value = false
  if (status !== props.meetup.my_status) emit('rsvp', status)
}
</script>
