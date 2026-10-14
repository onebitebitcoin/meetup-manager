<template>
  <div class="l-card link">
    <button
      type="button"
      class="l-cardbtn"
      @click="open"
    >
      <div class="l-row">
        <div
          class="l-date"
          :class="{ today: meetup.is_today }"
        >
          <span>{{ meetup.is_today ? '오늘' : `${parts.month}월` }}</span>
          <b>{{ parts.day }}</b>
          <span>{{ parts.weekday }}</span>
        </div>
        <div class="l-grow">
          <div class="l-title">
            {{ meetup.title }}
          </div>
          <div class="l-sub">
            {{ parts.time }} · {{ meetup.location }}
          </div>
          <div
            class="l-sub"
            style="margin-top: 4px"
          >
            <span
              v-if="meetup.my_status && !store.isHost"
              class="l-chip"
              :class="meetup.my_status"
            >
              {{ STATUS_LABEL[meetup.my_status] }}
            </span>
            <span class="l-counts">
              <Users :size="13" />{{ meetup.going_count }}/{{ meetup.capacity }}
            </span>
          </div>
        </div>
      </div>
    </button>
    <LiteJoinRow
      v-if="!meetup.my_status && !store.isHost"
      :meetup="meetup"
      @done="onJoinDone"
    />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { Users } from 'lucide-vue-next'
import { dateParts, STATUS_LABEL } from '../format'
import { useLiteStore } from '../store'
import LiteJoinRow from './LiteJoinRow.vue'

const props = defineProps({ meetup: { type: Object, required: true } })

const router = useRouter()
const store = useLiteStore()
const parts = computed(() => dateParts(props.meetup.starts_at))

const open = () => router.push(`/lite/m/${props.meetup.id}`)

const onJoinDone = () => open()
</script>
