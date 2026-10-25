<template>
  <button
    type="button"
    class="l-cardbtn l-mrow"
    @click="router.push(`/lite/m/${meetup.id}`)"
  >
    <span class="l-mrow-date">{{ parts.month }}.{{ parts.day }} {{ parts.weekday }}</span>
    <span class="l-grow">
      <span class="l-mrow-title">{{ meetup.title }}</span>
      <span class="l-mrow-sub">{{ parts.time }} · {{ meetup.location }}</span>
    </span>
    <img
      v-if="meetup.image_url"
      class="l-thumb sm"
      :src="meetup.image_url"
      alt=""
      loading="lazy"
    >
    <span
      v-if="meetup.cancelled"
      class="l-chip no"
    >취소됨</span>
    <span
      v-else-if="meetup.my_status && !store.isHost"
      class="l-chip"
      :class="meetup.my_status"
    >{{ STATUS_LABEL[meetup.my_status] }}</span>
    <ChevronRight
      :size="18"
      class="l-mrow-go"
    />
  </button>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import { ChevronRight } from 'lucide-vue-next'
import { dateParts, STATUS_LABEL } from '../format'
import { useLiteStore } from '../store'

const props = defineProps({ meetup: { type: Object, required: true } })

const router = useRouter()
const store = useLiteStore()
const parts = computed(() => dateParts(props.meetup.starts_at))
</script>
