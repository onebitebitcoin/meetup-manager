<template>
  <div class="l-btn-row">
    <button
      class="l-btn p"
      :disabled="busy"
      @click.stop="join"
    >
      {{ meetup.my_status === 'no' ? '다시 신청하기' : '신청하기' }}
    </button>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { liteApi } from '../api'
import { useLiteStore } from '../store'

const props = defineProps({ meetup: { type: Object, required: true } })
const emit = defineEmits(['done'])

const store = useLiteStore()
const busy = ref(false)

const join = async () => {
  if (busy.value) return
  busy.value = true
  const data = await store.act(() => liteApi.rsvp(props.meetup.id, 'going'), '신청했어요')
  busy.value = false
  if (data) emit('done', { status: 'going', meetup: data.meetup })
}
</script>
